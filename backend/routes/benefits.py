from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


# backend/routes/benefits.py
# Purpose: Benefits application and wallet (stub for integration).

benefits_bp = Blueprint("benefits", __name__, url_prefix="/benefits")


@benefits_bp.post("/apply")
@jwt_required()
def apply_benefit():
    """Citizen applies for a benefit (stub)."""
    user_email = get_jwt_identity()
    payload = request.get_json(silent=True) or {}
    scheme = (payload.get("scheme") or "").strip()
    if not scheme:
        return jsonify({"error": "scheme is required"}), 400
    application_id = f"app-{scheme}-001"
    return jsonify({"application_id": application_id, "status": "submitted", "applicant": user_email}), 202


@benefits_bp.post("/approve")
def approve_benefit():
    """Authority approves an application (stub)."""
    payload = request.get_json(silent=True) or {}
    application_id = (payload.get("application_id") or "").strip()
    if not application_id:
        return jsonify({"error": "application_id is required"}), 400
    return jsonify({"application_id": application_id, "status": "approved", "entitlement": {"amount": 1000}}), 200


@benefits_bp.get("/wallet")
@jwt_required()
def wallet_view():
    """Return stubbed wallet entitlements for logged-in user."""
    user_email = get_jwt_identity()
    return jsonify({
        "owner": user_email,
        "entitlements": [
            {"scheme": "PM-Kisan", "amount": 2000, "status": "active"},
            {"scheme": "Scholarship", "amount": 5000, "status": "active"}
        ]
    }), 200


