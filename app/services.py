import os
import logging
import base64
import threading
import numpy as np
import pandas as pd
from io import BytesIO
from PIL import Image
import easyocr
import faiss
from sentence_transformers import SentenceTransformer, util
from flask import current_app
from collections import Counter
from app.utils import extract_keywords, clean_ocr_text, format_pantun_visual, determine_theme

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

_visual_model_lock = threading.Lock()

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
        logger.info("Loading AI Models...")
        models["reader"] = easyocr.Reader(['ms', 'en'], gpu=False)
        models["text_embedder"] = SentenceTransformer('sentence-transformers/clip-ViT-B-32-multilingual-v1')
        # visual_embedder is loaded lazily (see load_visual_model) since it's only
        # needed for image searches with no OCR text, saving ~600MB on every other request.

        logger.info("Pre-computing Visual Tags...")
        TAGS_EMBEDDINGS = models["text_embedder"].encode(CANDIDATE_WORDS, convert_to_tensor=True)
        logger.info("Model Ready!")

def load_visual_model():
    if models["visual_embedder"] is None:
        with _visual_model_lock:
            if models["visual_embedder"] is None:
                logger.info("Loading Visual Model (CLIP)...")
                models["visual_embedder"] = SentenceTransformer('clip-ViT-B-32')
                logger.info("Visual Model Ready!")

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
            logger.info("Loading Database Cache...")
            db_data["index"] = faiss.read_index(index_file)
            cached = np.load(data_file, allow_pickle=True)
            db_data["texts"] = cached['texts'].tolist()
            db_data["titles"] = cached['titles'].tolist()
            db_data["authors"] = cached['authors'].tolist()
            return
        except Exception as e: 
            logger.warning(f"Failed to load cache: {e}")

    logger.info("Processing Excel...")
    load_models()
    
    if not os.path.exists(processed_csv):
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            df.to_csv(processed_csv, index=False)
            
    if os.path.exists(processed_csv):
        df = pd.read_csv(processed_csv).fillna("")
        texts = df['text'].astype(str).tolist()
        titles = df['tema'].tolist() if 'tema' in df.columns else ["General"] * len(texts)
        authors = df['asal'].tolist() if 'asal' in df.columns else ["Dataset"] * len(texts)

        embeddings = models["text_embedder"].encode(texts, convert_to_tensor=False, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings)
        
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        
        faiss.write_index(index, index_file)
        np.savez(data_file, texts=texts, titles=titles, authors=authors)
        
        db_data["texts"], db_data["titles"], db_data["authors"], db_data["index"] = texts, titles, authors, index
        logger.info("Database Ready!")

def detect_visual_tags(image, model):
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')

        img_vec = model.encode([image], convert_to_tensor=True)
        scores = util.cos_sim(img_vec, TAGS_EMBEDDINGS)[0]
        mean_score = float(scores.mean())
        std_score = float(scores.std())
        top_results = scores.topk(5)

        detected_tags = []
        for score, idx in zip(top_results[0], top_results[1]):
            score = float(score)
            # CLIP's raw similarity has a per-image baseline offset (even a
            # blank image scores ~0.25 against everything), so a fixed
            # threshold can't tell "confident match" from "no match". Instead,
            # a tag only counts if it stands out from this image's own score
            # distribution across all candidate words.
            if score > mean_score + 1.5 * std_score:
                detected_tags.append(CANDIDATE_WORDS[idx])

        if not detected_tags:
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
            search_mode = "Text Search"
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
            except: return {"error": "Corrupted image."}

            extracted_text = extract_text(image_np)
            if extracted_text:
                search_mode = "OCR Text Search"
                detected_keywords = extract_keywords(extracted_text)
                query_vec = models["text_embedder"].encode([extracted_text], convert_to_tensor=False)
            else:
                search_mode = "Image Search (Visual)"
                load_visual_model()
                detected_keywords = detect_visual_tags(image, models["visual_embedder"])
                # Search using the detected concepts as text, in the same embedding
                # space as the indexed pantun texts, rather than the raw image
                # embedding. CLIP aligns images well with short captions, but pantuns
                # are stylised rhyming verse, not literal descriptions, so matching
                # the image straight against pantun text is much noisier.
                query_vec = models["text_embedder"].encode([" ".join(detected_keywords)], convert_to_tensor=False)
                    
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
                    semantic_score = float(scores[0][i] * 100)

                    # Short/abstract queries can embed close to a handful of
                    # generic-sounding pantuns that share no actual vocabulary
                    # with the query, letting them outrank genuinely on-topic
                    # results. Blend in literal keyword overlap so a pantun
                    # that doesn't mention any detected keyword can't win
                    # purely on a coincidentally high embedding similarity.
                    if detected_keywords:
                        pantun_lower = db_data["texts"][idx].lower()
                        matched = sum(1 for kw in detected_keywords if kw.lower() in pantun_lower)
                        overlap_ratio = matched / len(detected_keywords)
                        final_score = semantic_score * 0.75 + overlap_ratio * 100 * 0.25
                    else:
                        final_score = semantic_score

                    results.append({
                        'title': determine_theme(db_data["texts"][idx]),
                        'content': db_data["texts"][idx],
                        'highlighted_content': fmt_text,
                        'author': db_data["authors"][idx],
                        'score': final_score
                    })

            results.sort(key=lambda r: r['score'], reverse=True)
            
            return {
                'search_mode': search_mode,
                'extracted_text': extracted_text,
                'pantun_input': extracted_text if mode == 'text' or len(extracted_text) > 4 else "Visual Image Analysis",
                'input_keywords': detected_keywords,
                'results': results
            }
            
    except Exception as e:
        logger.error(f"Pipeline: {e}")
        return {"error": str(e)}
    return {"error": "Error."}
