import string
import re
from flask import current_app

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def clean_ocr_text(text):
    cleaned = re.sub(r'[^\w\s.,?!]', '', text)
    return " ".join(cleaned.split())

def format_pantun_visual(text):
    """Format teks pantun (tambah newline jika perlu)."""
    if '\n' in text: return text
    parts = text.split(',')
    if len(parts) >= 2: return ",\n".join(parts)
    return text

def extract_keywords(text):
    if not text: return []
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    stopwords = {'dan', 'yang', 'di', 'ke', 'itu', 'ini', 'adalah', 'saya', 'nak', 'untuk'}
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    return list(set(keywords))
