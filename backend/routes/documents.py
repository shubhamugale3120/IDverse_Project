# backend/routes/documents.py
# Document upload and management endpoints

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.model import User
from backend.services.ipfs_service import get_ipfs_service
import os
import uuid
from datetime import datetime

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")

# Simple in-memory storage for demo (replace with real database table later)
_documents = {}

@documents_bp.post("/upload")
@jwt_required()
def upload_document():
    """
    Upload Document
    Purpose: Upload document to IPFS and store metadata
    Method: POST
    URL: /documents/upload
    Auth Required: Yes (JWT Token)
    """
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # Read file content
        file_content = file.read()
        file_type = file.content_type or 'application/octet-stream'
        
        # Upload to IPFS (mock)
        ipfs_service = get_ipfs_service()
        file_data = {
            "filename": file.filename,
            "content_type": file_type,
            "content": file_content.decode('utf-8', errors='ignore'),
            "uploaded_by": user_email,
            "uploaded_at": datetime.utcnow().isoformat(),
            "file_size": len(file_content)
        }
        cid = ipfs_service.upload_json(file_data)
        
        # Store metadata
        doc_id = str(uuid.uuid4())
        _documents[doc_id] = {
            "id": doc_id,
            "filename": file.filename,
            "cid": cid,
            "file_size": len(file_content),
            "content_type": file_type,
            "uploaded_by": user.id,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        return jsonify({
            "document_id": doc_id,
            "filename": file.filename,
            "cid": cid,
            "file_size": len(file_content),
            "uploaded_at": datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@documents_bp.get("/list")
@jwt_required()
def list_documents():
    """
    List User Documents
    Purpose: Get user's uploaded documents
    Method: GET
    URL: /documents/list
    Auth Required: Yes (JWT Token)
    """
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Get user's documents
        user_docs = [doc for doc in _documents.values() if doc["uploaded_by"] == user.id]
        
        return jsonify({
            "documents": user_docs,
            "total": len(user_docs)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve documents: {str(e)}"}), 500

@documents_bp.get("/types")
@jwt_required()
def get_document_types():
    """
    Get Available Document Types
    Purpose: Get list of supported document types
    Method: GET
    URL: /documents/types
    Auth Required: Yes (JWT Token)
    """
    try:
        document_types = [
            {"type": "aadhaar", "name": "Aadhaar Card", "required": True, "icon": "🆔"},
            {"type": "pan", "name": "PAN Card", "required": True, "icon": "💳"},
            {"type": "voter_id", "name": "Voter ID", "required": False, "icon": "🗳️"},
            {"type": "passport", "name": "Passport", "required": False, "icon": "🌐"},
            {"type": "driving_license", "name": "Driving License", "required": False, "icon": "🚗"}
        ]
        
        return jsonify({
            "document_types": document_types
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve document types: {str(e)}"}), 500
