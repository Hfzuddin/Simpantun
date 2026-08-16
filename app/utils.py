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

def determine_theme(text):
    if not text: return "Umum"
    text = text.lower()
    
    themes = {
        "Nasihat": ["nasihat", "pesan", "ingat", "jangan", "ilmu", "belajar", "guru", "buku", "tuntut", "pedoman"],
        "Budi": ["budi", "baik", "jasa", "hutang", "emas", "sopan", "bahasa", "adab"],
        "Kasih Sayang": ["kasih", "sayang", "cinta", "rindu", "hati", "jiwa", "kekasih", "merindu", "asmara"],
        "Agama": ["tuhan", "allah", "doa", "syurga", "neraka", "sembahyang", "solat", "iman", "dosa", "pahala", "agama"],
        "Jenaka": ["ketawa", "lucu", "geli", "senyum", "kera", "beruk", "katak", "kucing", "anjing", "tikus"],
        "Nasib & Perantau": ["rantau", "nasib", "dagang", "merantau", "kampung", "sedih", "menangis", "jauh", "miskin", "susah"]
    }
    
    for theme, keywords in themes.items():
        if any(kw in text for kw in keywords):
            return theme
            
    return "Umum"

