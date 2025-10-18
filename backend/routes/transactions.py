# backend/routes/transactions.py
# Transaction history and QR code generation endpoints

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.model import User, WalletItem, BenefitApplication
from datetime import datetime

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")

@transactions_bp.get("/")
@jwt_required()
def get_transactions():
    """
    Get User Transaction History
    Purpose: Retrieve user's transaction history (benefits + applications)
    Method: GET
    URL: /transactions/
    Auth Required: Yes (JWT Token)
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Get wallet items (benefits received)
        wallet_items = WalletItem.query.filter_by(owner_id=user.id).all()
        
        # Get applications (benefits applied)
        applications = BenefitApplication.query.filter_by(applicant_id=user.id).all()
        
        transactions = []
        
        # Add wallet items as transactions
        for item in wallet_items:
            transactions.append({
                "id": item.item_id,
                "type": "benefit_received",
                "description": f"Received {item.scheme_name}",
                "amount": item.amount,
                "currency": item.currency,
                "status": item.status.value,
                "date": item.created_at.isoformat() if item.created_at else None,
                "tx_hash": item.blockchain_tx_hash
            })
        
        # Add applications as transactions
        for app in applications:
            transactions.append({
                "id": app.application_id,
                "type": "application_submitted",
                "description": f"Applied for {app.scheme_name}",
                "amount": 0,
                "currency": "N/A",
                "status": app.status.value,
                "date": app.applied_at.isoformat() if app.applied_at else None,
                "tx_hash": None
            })
        
        # Sort by date (newest first)
        transactions.sort(key=lambda x: x["date"] or "1970-01-01", reverse=True)
        
        return jsonify({
            "user": user_email,
            "transactions": transactions,
            "total": len(transactions)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve transactions: {str(e)}"}), 500

@transactions_bp.get("/summary")
@jwt_required()
def get_transaction_summary():
    """
    Get Transaction Summary
    Purpose: Get summary statistics for user transactions
    Method: GET
    URL: /transactions/summary
    Auth Required: Yes (JWT Token)
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Get wallet items
        wallet_items = WalletItem.query.filter_by(owner_id=user.id).all()
        
        # Get applications
        applications = BenefitApplication.query.filter_by(applicant_id=user.id).all()
        
        # Calculate summary
        total_benefits = sum(item.amount for item in wallet_items)
        total_applications = len(applications)
        pending_applications = len([app for app in applications if app.status.value == "submitted"])
        approved_applications = len([app for app in applications if app.status.value == "approved"])
        
        return jsonify({
            "user": user_email,
            "summary": {
                "total_benefits_received": total_benefits,
                "total_applications": total_applications,
                "pending_applications": pending_applications,
                "approved_applications": approved_applications,
                "currency": "INR"
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve summary: {str(e)}"}), 500

