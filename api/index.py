import os
import sys

# Ensure root directory is in Python path so all modules (models, config, etc.) import cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class VercelPathFixer:
    """
    WSGI Middleware to restore the original client path from Vercel's edge proxy headers.
    Vercel sets HTTP_X_MATCHED_PATH to the actual URL path requested by the client.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = environ.get('HTTP_X_MATCHED_PATH')
        if matched_path:
            environ['PATH_INFO'] = matched_path
        elif environ.get('PATH_INFO') in ('/api/index', '/api/index.py'):
            environ['PATH_INFO'] = '/'
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixer(app.wsgi_app)
