from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Import database models and services
from backend.extensions import db
from backend.model import User, BenefitApplication, BenefitApplicationStatus, WalletItem, WalletItemStatus
from backend.services.registry_service import get_registry_service
from backend.services.ipfs_service import get_ipfs_service

# Import utilities
import uuid
from datetime import datetime, timedelta

# backend/routes/benefits.py
# Purpose: Benefits application and wallet with real database persistence

benefits_bp = Blueprint("benefits", __name__, url_prefix="/benefits")


@benefits_bp.post("/apply")
@jwt_required()
def apply_benefit():
    """
    Benefit Application Endpoint
    Purpose: Citizen applies for a government benefit/scheme
    Method: POST
    URL: /benefits/apply
    Auth Required: Yes (JWT Token)
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get application data from request
    payload = request.get_json(silent=True) or {}
    scheme_name = (payload.get("scheme") or payload.get("benefit_type") or "").strip()
    application_data = payload.get("application_data", payload.get("personal_info", {}))
    supporting_documents = payload.get("supporting_documents", [])
    
    # Input validation
    if not scheme_name:
        return jsonify({"error": "scheme or benefit_type is required"}), 400
    
    try:
        # Generate unique application ID
        application_id = f"app-{scheme_name}-{uuid.uuid4().hex[:8]}"
        
        # Create benefit application in database
        application = BenefitApplication(
            application_id=application_id,
            scheme_name=scheme_name,
            applicant_id=user.id,
            application_data=application_data,
            supporting_documents=supporting_documents,
            status=BenefitApplicationStatus.SUBMITTED
        )
        
        # Save to database
        db.session.add(application)
        db.session.commit()
        
        # Return success response
        return jsonify({
            "application_id": application_id,
            "status": "submitted",
            "applicant": user_email,
            "scheme_name": scheme_name,
            "created_at": application.created_at.isoformat()
        }), 202
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to submit application: {str(e)}"}), 500


@benefits_bp.post("/approve")
def approve_benefit():
    """
    Benefit Approval Endpoint
    Purpose: Authority approves a benefit application
    Method: POST
    URL: /benefits/approve
    Auth Required: No (Authority endpoint)
    """
    payload = request.get_json(silent=True) or {}
    application_id = (payload.get("application_id") or "").strip()
    approved_by = payload.get("approved_by", "authority")
    amount = payload.get("amount", 1000)
    benefit_type = payload.get("benefit_type", "cash")
    
    if not application_id:
        return jsonify({"error": "application_id is required"}), 400
    
    try:
        # Find the application
        application = BenefitApplication.query.filter_by(application_id=application_id).first()
        if not application:
            return jsonify({"error": "Application not found"}), 404
        
        # Update application status
        application.status = BenefitApplicationStatus.APPROVED
        application.reviewed_by = approved_by
        application.reviewed_at = datetime.utcnow()
        
        # Create wallet item for the approved benefit
        item_id = f"item-{application_id}-{uuid.uuid4().hex[:8]}"
        wallet_item = WalletItem(
            item_id=item_id,
            owner_id=application.applicant_id,
            application_id=application.id,
            scheme_name=application.scheme_name,
            benefit_type=benefit_type,
            amount=amount,
            currency="INR",
            status=WalletItemStatus.ACTIVE
        )
        
        # Get services for blockchain and IPFS
        registry_service = get_registry_service()
        ipfs_service = get_ipfs_service()
        
        # Create approval receipt
        receipt_data = {
            "application_id": application_id,
            "scheme_name": application.scheme_name,
            "approved_by": approved_by,
            "approved_at": datetime.utcnow().isoformat(),
            "amount": amount,
            "benefit_type": benefit_type
        }
        
        # Store receipt in IPFS
        receipt_cid = ipfs_service.upload_json(receipt_data)
        wallet_item.receipt_cid = receipt_cid
        
        # Record approval on blockchain (mock transaction hash)
        tx_hash = f"0x{uuid.uuid4().hex}"
        wallet_item.blockchain_tx_hash = tx_hash
        
        # Save to database
        db.session.add(wallet_item)
        db.session.commit()
        
        return jsonify({
            "application_id": application_id,
            "status": "approved",
            "wallet_item_id": item_id,
            "entitlement": {
                "amount": amount,
                "benefit_type": benefit_type,
                "currency": "INR"
            },
            "receipt_cid": receipt_cid,
            "tx_hash": tx_hash
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to approve application: {str(e)}"}), 500


@benefits_bp.get("/wallet")
@jwt_required()
def wallet_view():
    """
    Wallet View Endpoint
    Purpose: Return user's benefit entitlements from database
    Method: GET
    URL: /benefits/wallet
    Auth Required: Yes (JWT Token)
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Get user's wallet items from database
        wallet_items = WalletItem.query.filter_by(owner_id=user.id).all()
        
        # Convert to response format
        entitlements = []
        for item in wallet_items:
            entitlements.append({
                "item_id": item.item_id,
                "scheme": item.scheme_name,
                "amount": float(item.amount) if item.amount else None,
                "benefit_type": item.benefit_type,
                "currency": item.currency,
                "status": item.status.value,
                "approved_at": item.approved_at.isoformat() if item.approved_at else None,
                "expires_at": item.expires_at.isoformat() if item.expires_at else None,
                "claimed_at": item.claimed_at.isoformat() if item.claimed_at else None
            })
        
        return jsonify({
            "owner": user_email,
            "entitlements": entitlements,
            "total_items": len(entitlements)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve wallet: {str(e)}"}), 500


@benefits_bp.get("/applications")
@jwt_required()
def get_applications():
    """
    Get User Applications Endpoint
    Purpose: Retrieve user's benefit applications
    Method: GET
    URL: /benefits/applications
    Auth Required: Yes (JWT Token)
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        # Get all applications for user
        applications = BenefitApplication.query.filter_by(applicant_id=user.id).all()
        
        # Format response
        app_list = []
        for app in applications:
            app_list.append({
                "id": app.id,
                "application_id": app.application_id,
                "scheme_name": app.scheme_name,
                "status": app.status.value,
                "applied_at": app.applied_at.isoformat() if app.applied_at else None,
                "approved_at": app.approved_at.isoformat() if app.approved_at else None,
                "application_data": app.application_data,
                "supporting_documents": app.supporting_documents
            })
        
        return jsonify({
            "applicant": user_email,
            "total_applications": len(app_list),
            "applications": app_list
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve applications: {str(e)}"}), 500


