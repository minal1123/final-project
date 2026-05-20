# Flask Backend Application Server
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, jsonify
from backend.database import db
from backend.routes.api import api_bp

def create_app():
    app = Flask(__name__)
    
    # Initialize SQLite Database tables
    print("[Backend] Initializing database...")
    db.init_db()
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "service": "API Load Testing Dashboard Backend",
            "status": "healthy",
            "endpoints_prefix": "/api"
        })
        
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"[Backend] Starting server on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
