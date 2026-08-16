import os
import logging
from flask import Flask
from config import Config

def create_app():
    # Fix for OMP Initialization Error
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Ensure directories exist
    os.makedirs(app.config['DATASET_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        from app import routes
        app.register_blueprint(routes.bp)

    return app
