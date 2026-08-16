import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from app import create_app
from app.services import load_models, load_dataset_fast

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        print("MEMULAKAN SISTEM")
        load_models()
        load_dataset_fast()
        print(f"Buka: http://127.0.0.1:5500")
    
    app.run(debug=True, host='0.0.0.0', port=5500)
