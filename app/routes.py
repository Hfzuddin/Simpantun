import os
import secrets
import base64
import logging
from flask import Blueprint, request, jsonify, url_for, current_app
from werkzeug.utils import secure_filename
from app.services import process_pipeline, db_data

logger = logging.getLogger(__name__)

bp = Blueprint('routes', __name__)

@bp.route('/api/status', methods=['GET'])
def get_status():
    status = "Ready" if db_data["index"] else "Loading..."
    return jsonify({
        "total_pantun": len(db_data["texts"]),
        "status": status
    })

@bp.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if data.get('type') == 'text':
            res = process_pipeline(data.get('text'), 'text')
            img_url = None
        else:
            fname = secure_filename(data.get('filename', 'img.jpg'))
            fname = f"{os.path.splitext(fname)[0]}_{secrets.token_hex(4)}.jpg"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
            with open(upload_path, "wb") as f:
                f.write(base64.b64decode(data.get('image').split(",", 1)[1]))
            res = process_pipeline(data.get('image'), 'image')
            
            img_url = request.host_url.rstrip('/') + url_for('routes.uploaded_file', filename=fname)

        if 'error' in res: return jsonify(res), 500

        return jsonify({
            'success': True,
            'results': res.get('results', []),
            'pantun_input': res.get('pantun_input', ''),
            'extracted_text': res.get('extracted_text', ''),
            'search_mode': res.get('search_mode', ''),
            'input_keywords': res.get('input_keywords', []),
            'image_url': img_url
        })

    except Exception as e:
        logger.error(f"Analyze: {e}")
        return jsonify({'error': 'Server Error'}), 500

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
