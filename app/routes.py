import logging
from flask import Blueprint, request, jsonify
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
        else:
            # The upload is deliberately not written to disk. On Cloud Run the
            # container filesystem lives in memory, so every saved image would
            # hold RAM for the life of the instance -- nothing deleted them --
            # until it was OOM-killed, and would 404 from any other instance.
            # process_pipeline reads the base64 payload directly, and the
            # frontend already holds the same image to show on the result page.
            res = process_pipeline(data.get('image'), 'image')

        if 'error' in res: return jsonify(res), 500

        return jsonify({
            'success': True,
            'results': res.get('results', []),
            'pantun_input': res.get('pantun_input', ''),
            'extracted_text': res.get('extracted_text', ''),
            'search_mode': res.get('search_mode', ''),
            'input_keywords': res.get('input_keywords', [])
        })

    except Exception as e:
        logger.error(f"Analyze: {e}")
        return jsonify({'error': 'Server Error'}), 500
