# backend/routes/qr.py
# QR code generation and smart card endpoints

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.model import User, WalletItem, BenefitApplication, VerifiableCredential
import json
import base64
import io
from datetime import datetime

qr_bp = Blueprint("qr", __name__, url_prefix="/qr")

@qr_bp.post("/generate")
@jwt_required()
def generate_qr():
    """
    Generate QR Code for User
    Purpose: Generate QR code containing user profile and VC data
    Method: POST
    URL: /qr/generate
    Auth Required: Yes (JWT Token)
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Get user's VCs (if any exist)
        vcs = []
        try:
            vcs = VerifiableCredential.query.filter_by(holder_id=user.id).all()
        except:
            vcs = []
        
        # Get user's wallet items
        wallet_items = WalletItem.query.filter_by(owner_id=user.id).all()
        
        # Create QR data
        qr_data = {
            "user_profile": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "verifiable_credentials": [
                {
                    "id": vc.id,
                    "type": vc.credential_type,
                    "status": vc.status.value,
                    "issued_at": vc.issued_at.isoformat() if vc.issued_at else None
                } for vc in vcs
            ],
            "wallet_summary": {
                "total_items": len(wallet_items),
                "total_benefits": sum(item.amount for item in wallet_items),
                "currency": "INR"
            },
            "generated_at": datetime.utcnow().isoformat(),
            "qr_version": "1.0"
        }
        
        # For now, return the data as JSON (frontend will generate QR)
        # In production, you might want to generate actual QR image here
        return jsonify({
            "qr_data": qr_data,
            "qr_text": json.dumps(qr_data, indent=2),
            "message": "QR data generated successfully. Use frontend QR library to generate image."
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate QR: {str(e)}"}), 500

@qr_bp.get("/smartcard")
@jwt_required()
def get_smartcard_data():
    """
    Get Smart Card Data
    Purpose: Get user's smart card information for display
    Method: GET
    URL: /qr/smartcard
    Auth Required: Yes (JWT Token)
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Get user's VCs (if any exist)
        vcs = []
        try:
            vcs = VerifiableCredential.query.filter_by(holder_id=user.id).all()
        except:
            vcs = []
        
        # Get user's applications
        applications = BenefitApplication.query.filter_by(applicant_id=user.id).all()
        
        # Get user's wallet items
        wallet_items = WalletItem.query.filter_by(owner_id=user.id).all()
        
        # Create smart card data
        smartcard_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "idverse_number": f"IDV-{user.id:04d}-{hash(user.email) % 10000:04d}",
                "verified": True,
                "member_since": user.created_at.isoformat() if user.created_at else None
            },
            "verifiable_credentials": [
                {
                    "id": vc.id,
                    "type": vc.credential_type,
                    "status": vc.status.value,
                    "issued_at": vc.issued_at.isoformat() if vc.issued_at else None,
                    "expires_at": vc.expires_at.isoformat() if vc.expires_at else None
                } for vc in vcs
            ],
            "benefits": {
                "total_applications": len(applications),
                "approved_benefits": len([app for app in applications if app.status.value == "approved"]),
                "pending_applications": len([app for app in applications if app.status.value == "submitted"]),
                "total_amount": sum(item.amount for item in wallet_items),
                "currency": "INR"
            },
            "wallet_items": [
                {
                    "id": item.item_id,
                    "scheme_name": item.scheme_name,
                    "amount": item.amount,
                    "currency": item.currency,
                    "status": item.status.value,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                } for item in wallet_items
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return jsonify(smartcard_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get smart card data: {str(e)}"}), 500
