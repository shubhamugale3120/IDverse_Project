# Import Flask components for HTTP handling and JWT authentication
from flask import Blueprint, request, jsonify  # Blueprint: route grouping, request: HTTP data, jsonify: JSON response
from flask_jwt_extended import jwt_required, get_jwt_identity  # JWT: authentication decorators and utilities

# Import database models and services
from backend.extensions import db  # Database connection
from backend.model import User, VCRequest, VCRequestStatus, VerifiableCredential  # Database models
from backend.services.ipfs_service import get_ipfs_service  # IPFS service interface
from backend.services.signing_service import get_signing_service  # Signing service interface
from backend.services.registry_service import get_registry_service  # Registry service interface

# Import utilities
import uuid  # For generating unique IDs
from datetime import datetime, timedelta  # For timestamps and expiration

# backend/routes/vc.py
# Purpose: Verifiable Credential lifecycle (stubbed for integration).
# Later, replace with real signing, IPFS storage, and on-chain registry.

# Create VC blueprint with URL prefix "/vc"
# All routes in this file will be prefixed with /vc
vc_bp = Blueprint("vc", __name__, url_prefix="/vc")

@vc_bp.post("/request-issue")  # Decorator: defines HTTP POST method and route
@jwt_required()  # Decorator: requires valid JWT token in Authorization header
def request_issue():
    """
    VC Request Issue Endpoint
    Purpose: Citizen requests issuance of a Verifiable Credential
    Method: POST
    URL: /vc/request-issue
    Auth Required: Yes (JWT Token)
    
    Expected JSON:
    { "type": "GovID|StudentCard|...", "claims": { ... }, "subject_id": "optional" }
    
    Returns: Request ID for tracking credential issuance
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get JSON data from HTTP request body
    body = request.get_json(silent=True) or {}
    
    # Extract and sanitize credential type
    credential_type = (body.get("type") or "").strip()
    claims = body.get("claims") or {}
    subject_id = body.get("subject_id") or user_email  # Use user email as default subject

    # Input validation
    if not credential_type:
        return jsonify({"error": "type is required"}), 400

    try:
        # Generate unique request ID
        request_id = f"req-{credential_type}-{uuid.uuid4().hex[:8]}"
        
        # Set expiration time (7 days from now)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Create VC request in database
        vc_request = VCRequest(
            request_id=request_id,
            credential_type=credential_type,
            requester_id=user.id,
            claims=claims,
            subject_id=subject_id,
            status=VCRequestStatus.PENDING,
            expires_at=expires_at
        )
        
        # Save to database
        db.session.add(vc_request)
        db.session.commit()
        
        # Return success response
        return jsonify({
            "request_id": request_id,
            "status": "pending",
            "expires_at": expires_at.isoformat(),
            "next": "/vc/issue"
        }), 202
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create request: {str(e)}"}), 500


@vc_bp.post("/issue")  # Decorator: defines HTTP POST method and route
@jwt_required()  # Decorator: requires valid JWT token in Authorization header
def issue_vc():
    """
    VC Issue Endpoint
    Purpose: Authority issues a Verifiable Credential using real services
    Method: POST
    URL: /vc/issue
    Auth Required: Yes (JWT Token)
    
    Uses IPFS service, signing service, and registry service
    """
    # Get user identity from JWT token
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get JSON data from HTTP request body
    body = request.get_json(silent=True) or {}
    
    # Extract credential data
    credential_type = (body.get("type") or "").strip() or "GenericVC"
    subject_id = body.get("subject_id") or user_email
    claims = body.get("claims") or {}
    request_id = body.get("request_id")  # Optional: link to existing request

    try:
        # Get service instances
        ipfs_service = get_ipfs_service()
        signing_service = get_signing_service()
        registry_service = get_registry_service()
        
        # Generate unique VC ID
        vc_id = f"vc-{credential_type}-{uuid.uuid4().hex[:8]}"
        
        # Create Verifiable Credential in JSON-LD format
        vc_data = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": ["VerifiableCredential", credential_type],
            "issuer": signing_service.get_issuer_did(),
            "credentialSubject": {
                "id": f"did:example:{subject_id}",
                **claims
            },
            "issuanceDate": datetime.utcnow().isoformat() + "Z",
            "expirationDate": (datetime.utcnow() + timedelta(days=365)).isoformat() + "Z"
        }
        
        # Sign the credential
        signature = signing_service.sign_data(vc_data, signing_service.private_key)
        vc_data["proof"] = signature
        
        # Upload to IPFS
        cid = ipfs_service.upload_json(vc_data)
        
        # Pin the CID to ensure availability
        ipfs_service.pin_cid(cid)
        
        # Register on blockchain
        tx_hash = registry_service.register_credential(
            vc_id, cid, signing_service.get_issuer_did()
        )
        
        # Create VC record in database
        vc_record = VerifiableCredential(
            vc_id=vc_id,
            credential_type=credential_type,
            holder_id=user.id,
            vc_json=vc_data,
            claims=claims,
            ipfs_cid=cid,
            blockchain_tx_hash=tx_hash,
            registry_address=os.getenv('REGISTRY_CONTRACT_ADDRESS', 'mock')
        )
        
        # Link to original request if provided
        if request_id:
            vc_request = VCRequest.query.filter_by(request_id=request_id).first()
            if vc_request:
                vc_record.request_id = vc_request.id
                # Update request status
                vc_request.status = VCRequestStatus.ISSUED
                vc_request.approved_at = datetime.utcnow()
                vc_request.approved_by = user_email
        
        # Save to database
        db.session.add(vc_record)
        db.session.commit()
        
        # Return success response
        return jsonify({
            "vc_id": vc_id,
            "cid": cid,
            "tx_hash": tx_hash,
            "vc": vc_data,
            "status": "issued"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to issue credential: {str(e)}"}), 500


@vc_bp.post("/present")
def present_vc():
    """Verifier sends VC or presentation for verification (stub)."""
    payload = request.get_json(silent=True) or {}
    _vc = payload.get("vc") or {}
    # In future: validate signature, issuer DID, expiry, revocation, on-chain.
    return jsonify({"verified": True, "checks": ["signature", "issuer", "expiry", "status"], "stub": True}), 200


@vc_bp.get("/status/<vc_id>")
def vc_status(vc_id):
    """Return stub status for a VC id."""
    return jsonify({"vc_id": vc_id, "status": "issued", "revoked": False}), 200


