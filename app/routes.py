import os
import secrets
import base64
import logging
from flask import Blueprint, render_template, request, jsonify, session, url_for, current_app
from werkzeug.utils import secure_filename
from app.services import process_pipeline, db_data

logger = logging.getLogger(__name__)

bp = Blueprint('routes', __name__)

RESULTS_CACHE = {}

@bp.route('/')
def index():
    status = "Bersedia" if db_data["index"] else "Loading..."
    return render_template('index.html', total_pantun=len(db_data["texts"]), cache_status=status)

@bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if data.get('type') == 'text':
            res = process_pipeline(data.get('text'), 'text')
            fname = None
        else:
            fname = secure_filename(data.get('filename', 'img.jpg'))
            fname = f"{os.path.splitext(fname)[0]}_{secrets.token_hex(4)}.jpg"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
            with open(upload_path, "wb") as f:
                f.write(base64.b64decode(data.get('image').split(",", 1)[1]))
            res = process_pipeline(data.get('image'), 'image')

        if 'error' in res: return jsonify(res), 500

        sid = secrets.token_hex(8)
        RESULTS_CACHE[sid] = res
        session['sid'] = sid
        session['fname'] = fname
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Analyze: {e}")
        return jsonify({'error': 'Server Error'}), 500

@bp.route('/result')
def results_page():
    sid = session.get('sid')
    fname = session.get('fname')
    res = RESULTS_CACHE.get(sid)
    
    if not res: 
        return render_template('index.html', total_pantun=len(db_data["texts"]), cache_status="⚠️ Sesi Tamat")
    
    img_url = url_for('static', filename=f'uploads/{fname}') if fname else None
    
    return render_template('result.html', 
                           results=res.get('results', []),
                           pantun_input=res.get('pantun_input', ''),
                           extracted_text=res.get('extracted_text', ''),
                           search_mode=res.get('search_mode', ''),
                           input_keywords=res.get('input_keywords', []),
                           image_data=img_url)

@bp.route('/analytics')
def analytics():
    return render_template('analytics.html')
