from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from backend.extensions import db, jwt
from backend.config import Config
from backend.auth.routes import auth_bp

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)

    # ✅ Register blueprints
    app.register_blueprint(auth_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    with app.app_context():
        db.create_all()

    return app
