from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate       # <-- add this import

from backend.extensions import db, jwt
from backend.config import Config
from backend.auth.routes import auth_bp
from backend.scheme_engine import scheme_bp 
from backend.routes.otp import otp_bp
from backend.routes.vc import vc_bp
from backend.routes.benefits import benefits_bp
from backend.routes.transactions import transactions_bp
from backend.routes.qr import qr_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)
    Migrate(app, db) 

    # register blueprints (once each!)
    app.register_blueprint(auth_bp)
    app.register_blueprint(scheme_bp)
    app.register_blueprint(otp_bp)
    app.register_blueprint(vc_bp)
    app.register_blueprint(benefits_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(qr_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # helpful: see all routes in dev
    @app.get("/_debug/routes")
    def list_routes():
        return jsonify(sorted([str(r) for r in app.url_map.iter_rules()]))

    with app.app_context():
        db.create_all()

    return app



# thoery
# 1. backend/__init__.py
# Role: Application factory.
# What it does:
# Creates the Flask app
# Loads config (config.py)
# Initializes extensions (db, jwt)
# Registers blueprints (auth_bp, later scheme_bp, etc.)
# Defines a quick /health check endpoint
# ✅ Frontend needs this indirectly: without this, no backend APIs exist to call.

