import os
import logging
from flask import Flask, request, jsonify, send_from_directory
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

    # SPA fallback: Flask's static handler (static_url_path='/') owns any
    # single-segment path like /history, so it 404s before React Router
    # ever gets a chance to render that route client-side. Catch those
    # 404s here and serve index.html instead, so a hard reload/deep link
    # on a client-side route (e.g. /history, /result, /guide) still works.
    # /api/* keeps a real 404 rather than silently returning HTML. So does
    # any path whose last segment has a file extension (e.g. /vite.svg) —
    # that was meant to be a real static asset, not a client-side route, so
    # a missing one should stay a genuine 404 instead of masking it as HTML.
    @app.errorhandler(404)
    def spa_fallback(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not Found'}), 404
        if '.' in request.path.rsplit('/', 1)[-1]:
            return jsonify({'error': 'Not Found'}), 404
        return send_from_directory(app.static_folder, 'index.html')

    return app
