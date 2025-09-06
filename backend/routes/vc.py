# Import Flask components for HTTP handling and JWT authentication
from flask import Blueprint, request, jsonify  # Blueprint: route grouping, request: HTTP data, jsonify: JSON response
from flask_jwt_extended import jwt_required, get_jwt_identity  # JWT: authentication decorators and utilities

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
    { "type": "GovID|StudentCard|...", "claims": { ... } }
    
    Returns: Request ID for tracking credential issuance
    """
    # Get JSON data from HTTP request body
    # silent=True: Don't raise error if no JSON, return None instead
    body = request.get_json(silent=True) or {}  # {} is default empty dict if None
    
    # Extract and sanitize credential type
    # .get() method: Safe dictionary access (returns None if key doesn't exist)
    # or "": Default value if None
    # .strip(): Remove leading/trailing whitespace
    credential_type = (body.get("type") or "").strip()
    
    # Extract claims (additional data for the credential)
    # claims: Dictionary containing credential-specific data
    claims = body.get("claims") or {}  # {} is default empty dict if None

    # Input validation: Check if credential type is provided
    if not credential_type:
        # Return error response with HTTP status 400 (Bad Request)
        return jsonify({"error": "type is required"}), 400

    # Generate unique request ID for tracking
    # f-string: String formatting (Python 3.6+)
    # Format: "req-{credential_type}-001"
    request_id = f"req-{credential_type}-001"
    
    # Return success response with request tracking info
    # HTTP status 202 (Accepted): Request received, processing
    return jsonify({
        "request_id": request_id,  # Unique identifier for this request
        "status": "received",      # Current status of the request
        "next": "/vc/issue"        # Next step in the process
    }), 202


@vc_bp.post("/issue")  # Decorator: defines HTTP POST method and route
@jwt_required()  # Decorator: requires valid JWT token in Authorization header
def issue_vc():
    """
    VC Issue Endpoint
    Purpose: Authority issues a Verifiable Credential (stub implementation)
    Method: POST
    URL: /vc/issue
    Auth Required: Yes (JWT Token)
    
    For now, we create a mock VC and a placeholder CID.
    Later: Real cryptographic signing, IPFS storage, blockchain registry
    """
    # Extract user identity from JWT token
    # get_jwt_identity(): Flask-JWT-Extended function to get user from token
    # JWT payload contains: {"sub": "user@example.com", ...}
    email = get_jwt_identity()
    
    # Get JSON data from HTTP request body
    body = request.get_json(silent=True) or {}  # {} is default empty dict if None
    
    # Extract and sanitize credential type with fallback
    # or "GenericVC": Default value if type is empty
    credential_type = (body.get("type") or "").strip() or "GenericVC"
    
    # Extract subject ID (who the credential is about)
    # or email: Use JWT user email as default subject
    subject_id = body.get("subject_id") or email
    
    # Extract claims (credential-specific data)
    claims = body.get("claims") or {}  # {} is default empty dict if None

    # Create mock Verifiable Credential in JSON-LD format
    # JSON-LD: JSON for Linked Data (W3C standard for VCs)
    vc = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],  # VC context URL
        "type": ["VerifiableCredential", credential_type],  # VC type array
        "issuer": "did:example:issuer",  # Issuer DID (Decentralized Identifier)
        "credentialSubject": {
            "id": f"did:example:{subject_id}",  # Subject DID
            **claims  # Spread operator: merge claims into credentialSubject
        },
        "proof": {  # Cryptographic proof (stub)
            "type": "Ed25519Signature2020",  # Signature algorithm
            "created": "now",  # Creation timestamp (stub)
            "jws": "stub"  # JSON Web Signature (stub)
        }
    }

    # In future: upload VC JSON to IPFS and get a real CID
    # CID: Content Identifier (IPFS hash)
    cid = "bafybeigdyrstubcidexample"  # Placeholder IPFS CID
    
    # Generate unique VC ID for tracking
    vc_id = "vc-001"
    
    # Return success response with issued credential
    # HTTP status 201 (Created): Resource created successfully
    return jsonify({
        "vc_id": vc_id,  # Unique identifier for this credential
        "cid": cid,      # IPFS Content Identifier (placeholder)
        "vc": vc         # The actual Verifiable Credential JSON
    }), 201


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


