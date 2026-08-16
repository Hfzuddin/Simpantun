import os
import logging
import base64
import numpy as np
import pandas as pd
from io import BytesIO
from PIL import Image
import easyocr
import faiss
from sentence_transformers import SentenceTransformer, util
from flask import current_app
from collections import Counter
from app.utils import extract_keywords, clean_ocr_text, format_pantun_visual

logger = logging.getLogger(__name__)

models = {
    "reader": None,
    "text_embedder": None,
    "visual_embedder": None
}

db_data = {
    "texts": [],
    "titles": [],
    "authors": [],
    "index": None
}

TAGS_EMBEDDINGS = None
CANDIDATE_WORDS = [
    "alam", "bunga", "laut", "gunung", "hutan", "awan", "matahari", "bulan",
    "kampung", "sawah", "padi", "sungai", "pantai", "pokok", "daun",
    "kucing", "burung", "ayam", "ikan", "rama-rama", "haiwan", "kerbau",
    "kapal", "perahu", "keris", "rumah", "pelita", "tikar", "masjid",
    "gadis", "jejaka", "orang", "anak", "ibu", "bapa", "keluarga", "guru",
    "makanan", "buah", "pisang", "tebu", "kelapa", "nasi", "durian",
    "sedih", "gembira", "rindu", "cinta", "kasih", "budi", "ilmu", "belajar"
]

def load_models():
    global TAGS_EMBEDDINGS
    if models["text_embedder"] is None:
        logger.info("🔄 Memuatkan Model AI (dan CLIP)...")
        models["reader"] = easyocr.Reader(['ms', 'en'], gpu=False)
        models["text_embedder"] = SentenceTransformer('sentence-transformers/clip-ViT-B-32-multilingual-v1')
        models["visual_embedder"] = SentenceTransformer('clip-ViT-B-32')
        
        logger.info("⚡ Pre-computing Visual Tags...")
        TAGS_EMBEDDINGS = models["text_embedder"].encode(CANDIDATE_WORDS, convert_to_tensor=True)
        logger.info("✅ Model Siap!")

def extract_text(image_np):
    try:
        raw_ocr = models["reader"].readtext(image_np, detail=0)
        text = clean_ocr_text(" ".join(raw_ocr))
        return text if len(text) > 4 else ""
    except:
        return ""

def load_dataset_fast():
    index_file = current_app.config['INDEX_FILE']
    data_file = current_app.config['DATA_FILE']
    processed_csv = current_app.config['PROCESSED_CSV']
    excel_file = current_app.config['EXCEL_FILE']

    if os.path.exists(index_file) and os.path.exists(data_file):
        try:
            logger.info("🚀 Loading Database Cache...")
            db_data["index"] = faiss.read_index(index_file)
            cached = np.load(data_file, allow_pickle=True)
            db_data["texts"] = cached['texts'].tolist()
            db_data["titles"] = cached['titles'].tolist()
            db_data["authors"] = cached['authors'].tolist()
            return
        except Exception as e: 
            logger.warning(f"Gagal memuat cache: {e}")

    logger.info("⚙️ Memproses Excel...")
    load_models()
    
    if not os.path.exists(processed_csv):
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            df.to_csv(processed_csv, index=False)
            
    if os.path.exists(processed_csv):
        df = pd.read_csv(processed_csv).fillna("")
        texts = df['text'].astype(str).tolist()
        titles = df['tema'].tolist() if 'tema' in df.columns else ["Umum"] * len(texts)
        authors = df['asal'].tolist() if 'asal' in df.columns else ["Dataset"] * len(texts)

        embeddings = models["text_embedder"].encode(texts, convert_to_tensor=False, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings)
        
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        
        faiss.write_index(index, index_file)
        np.savez(data_file, texts=texts, titles=titles, authors=authors)
        
        db_data["texts"], db_data["titles"], db_data["authors"], db_data["index"] = texts, titles, authors, index
        logger.info("✅ Database Siap!")

def detect_visual_tags(image, model):
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_vec = model.encode([image], convert_to_tensor=True)
        scores = util.cos_sim(img_vec, TAGS_EMBEDDINGS)[0]
        top_results = scores.topk(5)
        
        detected_tags = []
        for score, idx in zip(top_results[0], top_results[1]):
            if score > 0.10: 
                detected_tags.append(CANDIDATE_WORDS[idx])
        
        if not detected_tags and len(top_results[0]) > 0:
             detected_tags.append(CANDIDATE_WORDS[top_results[1][0]])

        return detected_tags
    except Exception as e:
        logger.error(f"Visual Tag Error: {e}")
        return []

def process_pipeline(input_data, mode='image'):
    load_models()
    
    extracted_text = ""
    search_mode = ""
    query_vec = None
    detected_keywords = []
    
    try:
        if mode == 'text':
            extracted_text = input_data
            search_mode = "⌨️ Carian Teks"
            detected_keywords = extract_keywords(extracted_text)
            query_vec = models["text_embedder"].encode([extracted_text], convert_to_tensor=False)
        else:
            try:
                header, encoded = input_data.split(",", 1)
                image = Image.open(BytesIO(base64.b64decode(encoded)))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                if image.width > 800: image.thumbnail((800, 800))
                image_np = np.array(image)
            except: return {"error": "Imej rosak."}

            extracted_text = extract_text(image_np)
            if extracted_text:
                search_mode = "📄 Carian Teks OCR"
                detected_keywords = extract_keywords(extracted_text)
                query_vec = models["text_embedder"].encode([extracted_text], convert_to_tensor=False)
            else:
                search_mode = "🖼️ Carian Imej (Visual)"
                detected_keywords = detect_visual_tags(image, models["visual_embedder"])
                query_vec = models["visual_embedder"].encode([image_np], convert_to_tensor=False)
                    
        if query_vec is not None:
            query_vec = np.array(query_vec).astype('float32')
            faiss.normalize_L2(query_vec)
            
            k = 50 
            scores, indices = db_data["index"].search(query_vec.reshape(1, -1), k)
            
            results = []
            for i in range(k):
                idx = indices[0][i]
                if idx != -1 and idx < len(db_data["texts"]):
                    fmt_text = format_pantun_visual(db_data["texts"][idx])
                    
                    results.append({
                        'title': db_data["titles"][idx],
                        'content': db_data["texts"][idx],
                        'highlighted_content': fmt_text,
                        'author': db_data["authors"][idx],
                        'score': float(scores[0][i] * 100)
                    })
            
            return {
                'search_mode': search_mode,
                'extracted_text': extracted_text,
                'pantun_input': extracted_text if mode == 'text' or len(extracted_text) > 4 else "Analisis Imej Visual",
                'input_keywords': detected_keywords,
                'results': results
            }
            
    except Exception as e:
        logger.error(f"Pipeline: {e}")
        return {"error": str(e)}
    return {"error": "Ralat."}
