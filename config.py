import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sc_2025")
    
    # Dataset Paths
    DATASET_FOLDER = "dataset"
    EXCEL_FILE = os.path.join(DATASET_FOLDER, "PantunGH.xlsx")
    PROCESSED_CSV = os.path.join(DATASET_FOLDER, "Dataset.csv")
    
    # Uploads (relative to the run script)
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # AI Data Paths
    INDEX_FILE = "pantun_faiss.index"
    DATA_FILE = "pantun_data.npz"
