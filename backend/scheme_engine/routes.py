# backend/scheme_engine/routes.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.model import User
from .engine import suggest_schemes

scheme_bp = Blueprint("scheme", __name__, url_prefix="/schemes")

@scheme_bp.route("/", methods=["GET"])
@jwt_required()
def get_schemes():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"schemes": suggest_schemes(user)}), 200
