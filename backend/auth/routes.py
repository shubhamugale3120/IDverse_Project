# Import Flask components for HTTP handling
from flask import Blueprint, request, jsonify  # Blueprint: route grouping, request: HTTP data, jsonify: JSON response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  # JWT: authentication tokens
from backend.extensions import db  # Database connection
from sqlalchemy.exc import IntegrityError
from backend.model import User  # User database model

# Create authentication blueprint with URL prefix "/auth"
# Blueprint: Groups related routes together for organization
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])  # Decorator: defines HTTP method and route
def register():
    """
    User Registration Endpoint
    Purpose: Create new user account in database
    Method: POST
    URL: /auth/register
    Auth Required: No
    """
    # Get JSON data from HTTP request body
    # silent=True: Don't raise error if no JSON, return None instead
    data = request.get_json(silent=True) or {}  # {} is default empty dict if None
    
    # Extract and sanitize input data
    # .get() method: Safe dictionary access (returns None if key doesn't exist)
    # or "": Default value if None
    # .strip(): Remove leading/trailing whitespace
    # .lower(): Convert to lowercase for consistency
    username = (data.get("username") or data.get("name") or "").strip()  # Accept both "username" and "name"
    email = (data.get("email") or "").strip().lower()  # Normalize email format
    password = data.get("password")  # Get password (don't strip, might have spaces)

    # Input validation: Check if required fields are present
    if not username or not email or not password:
        # Return error response with HTTP status 400 (Bad Request)
        return jsonify({"error": "name, email, password are required"}), 400

    # Check if email already exists in database
    # SQLAlchemy ORM: User.query.filter_by(email=email).first()
    # filter_by(): WHERE clause in SQL
    # .first(): Get first result or None
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        # Return error with HTTP status 409 (Conflict)
        return jsonify({"error": "Email already registered"}), 409

    # Check if username already exists as well to avoid DB integrity error
    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        return jsonify({"error": "Username already taken"}), 409

    # Create new User object
    user = User(username=username, email=email)  # User model constructor
    
    # Hash password before storing (security best practice)
    # set_password() method uses werkzeug.security.generate_password_hash()
    user.set_password(password)
    
    # Add user to database session
    db.session.add(user)  # Add to SQLAlchemy session (not yet saved)
    try:
        db.session.commit()   # Commit transaction to database
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "User already exists"}), 409

    # Return success response with HTTP status 201 (Created)
    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])  # Decorator: defines HTTP method and route
def login():
    """
    User Login Endpoint
    Purpose: Authenticate user and return JWT access token
    Method: POST
    URL: /auth/login
    Auth Required: No
    Returns: JWT access token for protected endpoints
    """
    # Get JSON data from HTTP request body
    data = request.get_json(silent=True) or {}  # {} is default empty dict if None
    
    # Extract and sanitize credentials
    email = (data.get("email") or "").strip().lower()  # Normalize email format
    password = data.get("password") or ""  # Get password, default to empty string

    # Find user in database by email
    # SQLAlchemy ORM: translates to SQL query "SELECT * FROM users WHERE email = ?"
    user = User.query.filter_by(email=email).first()  # .first() returns User object or None
    
    # Verify user exists and password is correct
    # check_password() method uses werkzeug.security.check_password_hash()
    if not user or not user.check_password(password):
        # Return error with HTTP status 401 (Unauthorized)
        return jsonify({"error": "invalid credentials"}), 401

    # Create JWT access token
    # create_access_token(): Flask-JWT-Extended function
    # identity: What to store in JWT payload (user identifier)
    # JWT contains: {"sub": user.email, "exp": timestamp, "iat": timestamp, ...}
    access_token = create_access_token(identity=user.email)
    
    # Return success response with JWT token and user info
    # HTTP status 200 (OK)
    return jsonify({
        "access_token": access_token,  # JWT token for authentication
        "user": {  # User information (without sensitive data)
            "id": user.id,           # Database primary key
            "username": user.username,  # Display name
            "email": user.email      # Email address
        }
    }), 200

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