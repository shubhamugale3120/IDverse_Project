from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.extensions import db
from backend.model import User

# define blueprint FIRST
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    # accept both "username" and "name" for convenience
    username = (data.get("username") or data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "name, email, password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    access_token = create_access_token(identity=user.email)
    return jsonify({"access_token": access_token, "user": {
        "id": user.id, "username": user.username, "email": user.email
    }}), 200

    # Debug helper: list all users (secured)
    @auth_bp.route("/users", methods=["GET"])
    @jwt_required()
    def list_users():
        users = User.query.all()
        return jsonify([
            {"id": u.id, "username": u.username, "email": u.email}
            for u in users
        ])

# theory
# 5. backend/auth/routes.py
# Role: Handles Authentication APIs.

# Routes:

# POST /auth/register → register user
# POST /auth/login → login + get JWT token
# Uses User model, db, and JWT.
# ✅ Frontend integrates here:
# Registration page → calls /auth/register
# Login page → calls /auth/login
# Stores JWT in local storage/cookies for later use.