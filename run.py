# run.py
import os

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
    )
