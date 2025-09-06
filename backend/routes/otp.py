from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


# backend/routes/otp.py
# Purpose: Provide a simple OTP flow so frontend can integrate now.
# This is a stub (no real SMS/email). It stores nothing persistent.
# Replace with a real provider later (e.g., Twilio, Email, or gov gateway).

otp_bp = Blueprint("otp", __name__, url_prefix="/auth/otp")


@otp_bp.post("/request")
def request_otp():
    """Issue a dummy OTP for a given channel.

    Expected JSON:
    { "channel": "email" | "sms", "destination": "user@example.com" }

    Returns a token that must be echoed to verify (simulating OTP id),
    and a constant dummy_otp for now. In real impl, do not return the OTP.
    """
    payload = request.get_json(silent=True) or {}
    channel = (payload.get("channel") or "").strip().lower()
    destination = (payload.get("destination") or "").strip()

    if channel not in {"email", "sms"} or not destination:
        return jsonify({"error": "channel (email|sms) and destination are required"}), 400

    # For demo: constant OTP. Real world should generate random and deliver.
    dummy_otp = "123456"
    otp_token = f"otp:{channel}:{destination}"

    return jsonify({
        "msg": "OTP issued (stub)",
        "otp_token": otp_token,
        "otp_demo": dummy_otp  # NOTE: Do not return in production
    }), 200


@otp_bp.post("/verify")
def verify_otp():
    """Verify a dummy OTP.

    Expected JSON:
    { "otp_token": "...", "otp_code": "123456" }
    """
    payload = request.get_json(silent=True) or {}
    otp_token = payload.get("otp_token") or ""
    otp_code = payload.get("otp_code") or ""

    if not otp_token or not otp_code:
        return jsonify({"error": "otp_token and otp_code are required"}), 400

    if otp_code == "123456":
        return jsonify({"verified": True}), 200

    return jsonify({"verified": False}), 200


