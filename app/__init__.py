import os
import logging
from flask import Flask
from config import Config

def create_app():
    # Fix for OMP Initialization Error
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

    # Configure Flask to serve React dist folder
    app = Flask(__name__, static_folder='../dist', static_url_path='/', template_folder='../dist')
    app.config.from_object(Config)

    from flask_cors import CORS
    CORS(app)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Ensure directories exist
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    os.makedirs(app.config['DATASET_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        from app import routes
        app.register_blueprint(routes.bp)

    return app
