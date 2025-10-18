# backend/routes/linked_ids.py
# Linked IDs management endpoints

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.model import User
import uuid
from datetime import datetime

linked_ids_bp = Blueprint("linked_ids", __name__, url_prefix="/linked-ids")

# Simple in-memory storage for demo (replace with real database table later)
_linked_ids = {}

@linked_ids_bp.get("/")
@jwt_required()
def get_linked_ids():
    """
    Get User's Linked IDs
    Purpose: Get user's linked identification documents
    Method: GET
    URL: /linked-ids/
    Auth Required: Yes (JWT Token)
    """
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Get user's linked IDs
        user_linked_ids = [linked_id for linked_id in _linked_ids.values() if linked_id["user_id"] == user.id]
        
        # If no linked IDs, return default mock data
        if not user_linked_ids:
            default_ids = [
                {
                    "id": "aadhaar_001",
                    "type": "aadhaar",
                    "name": "Aadhaar Card",
                    "number": "****1234",
                    "is_verified": True,
                    "icon": "🆔",
                    "status": "Linked"
                },
                {
                    "id": "pan_001", 
                    "type": "pan",
                    "name": "PAN Card",
                    "number": "****5678",
                    "is_verified": True,
                    "icon": "💳",
                    "status": "Linked"
                },
                {
                    "id": "voter_001",
                    "type": "voter_id",
                    "name": "Voter ID",
                    "number": "Linked",
                    "is_verified": True,
                    "icon": "🗳️",
                    "status": "Linked"
                },
                {
                    "id": "passport_001",
                    "type": "passport",
                    "name": "Passport",
                    "number": "Not Linked",
                    "is_verified": False,
                    "icon": "🌐",
                    "status": "Not Linked"
                }
            ]
            user_linked_ids = default_ids
        
        return jsonify({
            "linked_ids": user_linked_ids,
            "total": len(user_linked_ids)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve linked IDs: {str(e)}"}), 500

@linked_ids_bp.post("/link")
@jwt_required()
def link_id():
    """
    Link New ID
    Purpose: Link a new identification document
    Method: POST
    URL: /linked-ids/link
    Auth Required: Yes (JWT Token)
    """
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json() or {}
    id_type = data.get("type", "").strip()
    id_number = data.get("number", "").strip()
    
    if not id_type or not id_number:
        return jsonify({"error": "Type and number are required"}), 400
    
    try:
        # Create new linked ID
        linked_id = {
            "id": f"{id_type}_{uuid.uuid4().hex[:8]}",
            "type": id_type,
            "name": data.get("name", id_type.replace("_", " ").title()),
            "number": id_number,
            "is_verified": False,
            "icon": data.get("icon", "📄"),
            "status": "Pending Verification",
            "user_id": user.id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        _linked_ids[linked_id["id"]] = linked_id
        
        return jsonify({
            "message": "ID linked successfully",
            "linked_id": linked_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to link ID: {str(e)}"}), 500

@linked_ids_bp.post("/verify")
@jwt_required()
def verify_id():
    """
    Verify Linked ID
    Purpose: Verify a linked identification document
    Method: POST
    URL: /linked-ids/verify
    Auth Required: Yes (JWT Token)
    """
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json() or {}
    linked_id = data.get("linked_id", "").strip()
    
    if not linked_id:
        return jsonify({"error": "Linked ID is required"}), 400
    
    try:
        if linked_id in _linked_ids:
            _linked_ids[linked_id]["is_verified"] = True
            _linked_ids[linked_id]["status"] = "Verified"
            _linked_ids[linked_id]["verified_at"] = datetime.utcnow().isoformat()
            
            return jsonify({
                "message": "ID verified successfully",
                "linked_id": _linked_ids[linked_id]
            }), 200
        else:
            return jsonify({"error": "Linked ID not found"}), 404
        
    except Exception as e:
        return jsonify({"error": f"Failed to verify ID: {str(e)}"}), 500
