import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from app import create_app
from app.services import load_models, load_dataset_fast

app = create_app()

# Runs at import time (not just __main__) so a WSGI server like gunicorn
# also triggers model/dataset loading before serving requests.
with app.app_context():
    print("System Starting.....")
    load_models()
    load_dataset_fast()
    print("System Ready!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5500))
    debug = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=debug, host='0.0.0.0', port=port)
