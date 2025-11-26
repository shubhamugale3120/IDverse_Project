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
import os  # For environment variables
from datetime import datetime, timedelta  # For timestamps and expiration
import secrets

# backend/routes/vc.py
# Purpose: Verifiable Credential lifecycle (stubbed for integration).
# Later, replace with real signing, IPFS storage, and on-chain registry.

# Create VC blueprint with URL prefix "/vc"
# All routes in this file will be prefixed with /vc
vc_bp = Blueprint("vc", __name__, url_prefix="/vc")

# Simple in-memory nonce store with TTL for demo purposes
_NONCE_STORE = {}
_NONCE_TTL_SECONDS = 120

def _purge_nonces():
    now = datetime.utcnow().timestamp()
    expired = [k for k, v in _NONCE_STORE.items() if v < now]
    for k in expired:
        _NONCE_STORE.pop(k, None)

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
            "id": vc_id,
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
        # Try to capture on-chain numeric id
        onchain_vc_id = None
        try:
            onchain_vc_id = registry_service.get_onchain_id(vc_id)
        except Exception:
            pass
        
        # Create VC record in database
        vc_record = VerifiableCredential(
            vc_id=vc_id,
            credential_type=credential_type,
            holder_id=user.id,
            vc_json=vc_data,
            claims=claims,
            ipfs_cid=cid,
            blockchain_tx_hash=tx_hash,
            registry_address=os.getenv('REGISTRY_CONTRACT_ADDRESS', 'mock'),
            onchain_vc_id=onchain_vc_id
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
    """Verifier sends VC or presentation for verification (supports selective disclosure)."""
    payload = request.get_json(silent=True) or {}
    provided_vc = payload.get("vc")
    disclosed = payload.get("disclosed")  # optional subset of credentialSubject fields
    cid = payload.get("cid")
    presented_vc_id = payload.get("vc_id")

    try:
        signing_service = get_signing_service()
        registry_service = get_registry_service()
        ipfs_service = get_ipfs_service()

        # Resolve canonical VC: prefer provided full VC, else by CID, else by vc_id via DB
        canonical_vc = None
        if provided_vc:
            canonical_vc = provided_vc
        elif cid:
            canonical_vc = ipfs_service.get_json(cid)
        elif presented_vc_id:
                # Try DB lookup to get CID/json. Be tolerant of formats: accept vc ids with or without `vc-`,
                # also accept raw IPFS CIDs and partial matches.
                from backend.model import VerifiableCredential
                def _resolve_vc_by_identifier(identifier):
                    # direct match
                    rec = VerifiableCredential.query.filter_by(vc_id=identifier).first()
                    if rec:
                        return rec
                    # try adding/removing 'vc-' prefix
                    if identifier.startswith('vc-'):
                        rec = VerifiableCredential.query.filter_by(vc_id=identifier[3:]).first()
                        if rec:
                            return rec
                    else:
                        rec = VerifiableCredential.query.filter_by(vc_id='vc-' + identifier).first()
                        if rec:
                            return rec
                    # try searching by ipfs_cid equals identifier
                    rec = VerifiableCredential.query.filter_by(ipfs_cid=identifier).first()
                    if rec:
                        return rec
                    # try contains (partial match) - helpful when IDs were displayed differently
                    try:
                        rec = VerifiableCredential.query.filter(VerifiableCredential.vc_id.contains(identifier)).first()
                        if rec:
                            return rec
                    except Exception:
                        pass
                    return None

                vc_rec = _resolve_vc_by_identifier(presented_vc_id)
                if vc_rec and getattr(vc_rec, 'vc_json', None):
                    canonical_vc = vc_rec.vc_json
                elif vc_rec and getattr(vc_rec, 'ipfs_cid', None):
                    canonical_vc = ipfs_service.get_json(vc_rec.ipfs_cid)
        if not canonical_vc:
            return jsonify({"verified": False, "reason": "VC not found"}), 200

        proof = canonical_vc.get("proof") or {}
        unsigned = {k: v for k, v in canonical_vc.items() if k != "proof"}

        # Basic schema check
        types = unsigned.get("type") or []
        if "VerifiableCredential" not in types:
            return jsonify({"verified": False, "reason": "Invalid VC type"}), 200

        # Expiry check
        exp = unsigned.get("expirationDate")
        if exp:
            try:
                if datetime.fromisoformat(exp.replace("Z", "")) < datetime.utcnow():
                    return jsonify({"verified": False, "reason": "Credential expired"}), 200
            except Exception:
                pass

        # Signature verification (issuer public key)
        pubkey = signing_service.get_public_key()
        sig_ok = signing_service.verify_signature(unsigned, proof, pubkey)

        # On-chain status via registry
        vc_id = unsigned.get("id") or presented_vc_id or ""
        status = {"is_registered": False}
        # Prefer onchain id if we have DB record
        try:
            if not status.get("is_registered") and vc_id:
                from backend.model import VerifiableCredential
                vc_rec2 = VerifiableCredential.query.filter_by(vc_id=vc_id).first()
                if vc_rec2 and vc_rec2.onchain_vc_id is not None:
                    status = registry_service.get_status_by_onchain_id(int(vc_rec2.onchain_vc_id))
                else:
                    status = registry_service.get_credential_status(vc_id)
        except Exception:
            status = registry_service.get_credential_status(vc_id) if vc_id else {"is_registered": False}
        active_ok = status.get("is_registered", False) and not status.get("is_revoked", False)

        # Selective disclosure validation: disclosed must be subset of credentialSubject
        disclosure_ok = True
        if disclosed is not None:
            cred_subj = (unsigned.get("credentialSubject") or {}).copy()
            # Require id to be consistent if provided
            if "id" in disclosed and disclosed["id"] != cred_subj.get("id"):
                disclosure_ok = False
            # Check each disclosed key/value matches canonical
            for k, v in disclosed.items():
                if k == "id":
                    continue
                if cred_subj.get(k) != v:
                    disclosure_ok = False
                    break

        # Optional challenge/nonce validation (prevents replay)
        challenge = payload.get("challenge")
        challenge_ok = True
        if challenge:
            _purge_nonces()
            exp_at = _NONCE_STORE.pop(challenge, None)
            challenge_ok = bool(exp_at and exp_at > datetime.utcnow().timestamp())

        verified = bool(sig_ok and active_ok and disclosure_ok and challenge_ok)
        return jsonify({
            "verified": verified,
            "checks": {"signature": bool(sig_ok), "status": bool(active_ok), "disclosure_subset": bool(disclosure_ok), "challenge": bool(challenge_ok)},
            "status_info": status
        }), 200
    except Exception as e:
        return jsonify({"verified": False, "error": str(e)}), 200


@vc_bp.post("/revoke")
@jwt_required()
def revoke_vc():
    """Authority revokes a VC (marks on registry and DB)."""
    user_email = get_jwt_identity()
    body = request.get_json(silent=True) or {}
    vc_id = (body.get("vc_id") or "").strip()
    reason = (body.get("reason") or "").strip() or "unspecified"
    if not vc_id:
        return jsonify({"error": "vc_id is required"}), 400
    try:
        # registry revoke
        registry_service = get_registry_service()
        # Prefer on-chain id if persisted
        tx_hash = None
        try:
            from backend.model import VerifiableCredential
            vc_rec2 = VerifiableCredential.query.filter_by(vc_id=vc_id).first()
            if vc_rec2 and vc_rec2.onchain_vc_id is not None:
                tx_hash = registry_service.revoke_by_onchain_id(int(vc_rec2.onchain_vc_id), 1)
            else:
                tx_hash = registry_service.revoke_credential(vc_id, reason)
        except Exception:
            tx_hash = registry_service.revoke_credential(vc_id, reason)

        # DB update if present
        from backend.extensions import db
        from backend.model import VerifiableCredential
        vc_rec = VerifiableCredential.query.filter_by(vc_id=vc_id).first()
        if vc_rec:
            vc_rec.is_revoked = True
            vc_rec.revoked_at = datetime.utcnow()
            vc_rec.revoked_by = user_email
            vc_rec.revocation_reason = reason
            vc_rec.blockchain_tx_hash = tx_hash or vc_rec.blockchain_tx_hash
            db.session.commit()

        return jsonify({"vc_id": vc_id, "status": "revoked", "tx_hash": tx_hash}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to revoke: {e}"}), 500


@vc_bp.get("/challenge")
def get_challenge():
    """Issue a short-lived nonce to bind verification and prevent replay."""
    _purge_nonces()
    nonce = secrets.token_urlsafe(16)
    expires_at = datetime.utcnow() + timedelta(seconds=_NONCE_TTL_SECONDS)
    _NONCE_STORE[nonce] = expires_at.timestamp()
    return jsonify({
        "challenge": nonce,
        "expires_at": expires_at.isoformat() + "Z",
        "ttl_seconds": _NONCE_TTL_SECONDS
    }), 200


@vc_bp.get("/issuer-info")
def issuer_info():
    """Expose issuer DID and public key for verifiers (no auth)."""
    try:
        signing_service = get_signing_service()
        return jsonify({
            "issuer_did": signing_service.get_issuer_did(),
            "public_key_hex": signing_service.get_public_key(),
            "sign_mode": os.getenv('SIGN_MODE', 'mock')
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vc_bp.get('/mock-registry')
def mock_registry():
    """Debug endpoint: return mock registry state when running in mock mode.
    This is intended for local demo debugging only - it should not be enabled in production.
    """
    try:
        if os.getenv('CHAIN_MODE', 'mock').lower() != 'mock':
            return jsonify({'error': 'mock registry only available when CHAIN_MODE=mock'}), 403

        registry_service = get_registry_service()
        # Try to return internal structures if available
        registry = getattr(registry_service, '_registry', None)
        vcid_map = getattr(registry_service, '_vcid_map', None)
        tx_counter = getattr(registry_service, '_transaction_counter', None)
        return jsonify({'registry': registry or {}, 'vcid_map': vcid_map or {}, 'transaction_counter': tx_counter or 0}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vc_bp.get("/status/<vc_id>")
def vc_status(vc_id):
    """Return stub status for a VC id."""
    return jsonify({"vc_id": vc_id, "status": "issued", "revoked": False}), 200


@vc_bp.get("/demo-state")
def demo_state():
    """Return a small snapshot useful for the demo UI: issuer info, known VCs from DB and on-chain status."""
    try:
        signing_service = get_signing_service()
        registry_service = get_registry_service()

        # Pull VCs from DB (if any)
        from backend.model import VerifiableCredential
        vcs = []
        for rec in VerifiableCredential.query.limit(100).all():
            vc_id = getattr(rec, 'vc_id', None)
            ipfs_cid = getattr(rec, 'ipfs_cid', None)
            # query registry status (mock or real)
            try:
                status = registry_service.get_credential_status(vc_id) if vc_id else {"is_registered": False}
            except Exception:
                status = {"is_registered": False}

            vcs.append({
                "vc_id": vc_id,
                "holder_id": getattr(rec, 'holder_id', None),
                "ipfs_cid": ipfs_cid,
                "onchain_status": status,
            })

        return jsonify({
            "issuer": signing_service.get_issuer_did(),
            "public_key": signing_service.get_public_key(),
            "vcs": vcs
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vc_bp.post('/demo-upload')
def demo_upload():
    """Unauthenticated demo file upload. Returns a CID using the configured IPFS service."""
    try:
        # prefer multipart file
        if 'file' in request.files:
            f = request.files['file']
            content = f.read()
            file_type = f.content_type or 'application/octet-stream'
            filename = f.filename or 'upload.bin'
            data = {
                'filename': filename,
                'content_type': file_type,
                'content': content.decode('utf-8', errors='ignore')[:100000],
            }
            ipfs_service = get_ipfs_service()
            cid = ipfs_service.upload_json(data)
            return jsonify({'cid': cid}), 201

        # else expect JSON body
        body = request.get_json(silent=True) or {}
        if not body:
            return jsonify({'error': 'no file or json provided'}), 400
        ipfs_service = get_ipfs_service()
        cid = ipfs_service.upload_json(body)
        return jsonify({'cid': cid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vc_bp.post('/demo-issue')
def demo_issue():
    """Issue a credential in demo mode without auth. Creates/demo user if needed and returns the issued VC info."""
    try:
        body = request.get_json(silent=True) or {}
        credential_type = (body.get('type') or 'DemoVC')
        subject = body.get('subject_id') or 'demo-subject'
        claims = body.get('claims') or {}

        signing_service = get_signing_service()
        ipfs_service = get_ipfs_service()
        registry_service = get_registry_service()

        # Ensure demo user exists
        demo_email = os.getenv('DEMO_USER_EMAIL', 'demo@idverse.local')
        demo_username = os.getenv('DEMO_USER_NAME', 'demo_user')
        from backend.model import User, VerifiableCredential
        user = User.query.filter_by(email=demo_email).first()
        if not user:
            user = User(username=demo_username, email=demo_email)
            user.set_password('demo123')
            from backend.extensions import db
            db.session.add(user)
            db.session.commit()

        # build VC
        vc_id = f"vc-{credential_type}-{uuid.uuid4().hex[:8]}"
        vc_data = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": ["VerifiableCredential", credential_type],
            "issuer": signing_service.get_issuer_did(),
            "id": vc_id,
            "credentialSubject": {"id": f"did:example:{subject}", **claims},
            "issuanceDate": datetime.utcnow().isoformat() + "Z",
        }

        # sign
        signing_error = None
        try:
            signature = signing_service.sign_data(vc_data, getattr(signing_service, 'private_key', None))
            vc_data['proof'] = signature
        except Exception as e:
            # record signing error and fallback to mock sign
            signing_error = str(e)
            vc_data['proof'] = {
                'type': 'MockProof', 'created': datetime.utcnow().isoformat() + 'Z',
                'verificationMethod': signing_service.get_issuer_did() + '#key-1',
                'jws': 'mocksig'
            }

        # upload
        cid = ipfs_service.upload_json(vc_data)
        try:
            ipfs_service.pin_cid(cid)
        except Exception:
            pass

        # register on chain (mock or real)
        registry_error = None
        try:
            tx_hash = registry_service.register_credential(vc_id, cid, signing_service.get_issuer_did())
            onchain_id = registry_service.get_onchain_id(vc_id) if hasattr(registry_service, 'get_onchain_id') else None
        except Exception as e:
            registry_error = str(e)
            tx_hash = None
            onchain_id = None

        # persist VC record
        from backend.extensions import db
        vc_record = VerifiableCredential(
            vc_id=vc_id,
            credential_type=credential_type,
            holder_id=user.id,
            vc_json=vc_data,
            claims=claims,
            ipfs_cid=cid,
            blockchain_tx_hash=tx_hash,
            registry_address=os.getenv('REGISTRY_CONTRACT_ADDRESS', 'mock'),
            onchain_vc_id=onchain_id
        )
        db.session.add(vc_record)
        db.session.commit()

        resp = {"vc_id": vc_id, "cid": cid, "tx_hash": tx_hash, "vc": vc_data}
        if signing_error:
            resp['signing_error'] = signing_error
        if registry_error:
            resp['registry_error'] = registry_error
        return jsonify(resp), 201
    except Exception as e:
        try:
            from backend.extensions import db
            db.session.rollback()
        except Exception:
            pass
        return jsonify({"error": str(e)}), 500


@vc_bp.post('/demo-verify')
def demo_verify():
    """Unauthenticated demo verify endpoint. Accepts vc (json) or cid or vc_id and returns verification result."""
    try:
        body = request.get_json(silent=True) or {}
        provided_vc = body.get('vc')
        cid = body.get('cid')
        presented_vc_id = body.get('vc_id')

        signing_service = get_signing_service()
        registry_service = get_registry_service()
        ipfs_service = get_ipfs_service()

        canonical_vc = None
        if provided_vc:
            canonical_vc = provided_vc
        elif cid:
            canonical_vc = ipfs_service.get_json(cid)
        elif presented_vc_id:
            # Use same tolerant resolution as present_vc: accept vc- prefix variations and CID lookups
            def _resolve_vc_by_identifier(identifier):
                rec = VerifiableCredential.query.filter_by(vc_id=identifier).first()
                if rec:
                    return rec
                if identifier.startswith('vc-'):
                    rec = VerifiableCredential.query.filter_by(vc_id=identifier[3:]).first()
                    if rec:
                        return rec
                else:
                    rec = VerifiableCredential.query.filter_by(vc_id='vc-' + identifier).first()
                    if rec:
                        return rec
                rec = VerifiableCredential.query.filter_by(ipfs_cid=identifier).first()
                if rec:
                    return rec
                try:
                    rec = VerifiableCredential.query.filter(VerifiableCredential.vc_id.contains(identifier)).first()
                    if rec:
                        return rec
                except Exception:
                    pass
                return None

            vc_rec = _resolve_vc_by_identifier(presented_vc_id)
            if vc_rec and getattr(vc_rec, 'vc_json', None):
                canonical_vc = vc_rec.vc_json
            elif vc_rec and getattr(vc_rec, 'ipfs_cid', None):
                canonical_vc = ipfs_service.get_json(vc_rec.ipfs_cid)

        if not canonical_vc:
            return jsonify({'verified': False, 'reason': 'VC not found'}), 200

        proof = canonical_vc.get('proof') or {}
        unsigned = {k: v for k, v in canonical_vc.items() if k != 'proof'}

        # signature check
        pubkey = signing_service.get_public_key()
        sig_ok = signing_service.verify_signature(unsigned, proof, pubkey)

        # on-chain status
        vc_id = unsigned.get('id') or presented_vc_id or ''
        try:
            status = registry_service.get_credential_status(vc_id) if vc_id else {'is_registered': False}
        except Exception:
            status = {'is_registered': False}

        active_ok = status.get('is_registered', False) and not status.get('is_revoked', False)

        verified = bool(sig_ok and active_ok)
        return jsonify({'verified': verified, 'checks': {'signature': sig_ok, 'onchain': active_ok}, 'status': status}), 200
    except Exception as e:
        return jsonify({'verified': False, 'error': str(e)}), 500


@vc_bp.post('/demo-revoke')
def demo_revoke():
    """Unauthenticated demo revoke: revoke vc_id on registry and mark DB record revoked."""
    try:
        body = request.get_json(silent=True) or {}
        vc_id = (body.get('vc_id') or '').strip()
        if not vc_id:
            return jsonify({'error': 'vc_id required'}), 400

        registry_service = get_registry_service()
        # try revoke
        try:
            tx = registry_service.revoke_credential(vc_id, 'demo_revoke')
        except Exception:
            # if registry supports revoke_by_onchain_id
            try:
                vc_rec = VerifiableCredential.query.filter_by(vc_id=vc_id).first()
                if vc_rec and vc_rec.onchain_vc_id is not None:
                    tx = registry_service.revoke_by_onchain_id(int(vc_rec.onchain_vc_id), 1)
                else:
                    raise
            except Exception as e:
                return jsonify({'error': f'revoke failed: {e}'}), 500

        # update DB
        vc_rec2 = VerifiableCredential.query.filter_by(vc_id=vc_id).first()
        if vc_rec2:
            vc_rec2.is_revoked = True
            vc_rec2.revoked_at = datetime.utcnow()
            vc_rec2.revoked_by = 'demo'
            vc_rec2.revocation_reason = 'demo_revoke'
            vc_rec2.blockchain_tx_hash = tx or vc_rec2.blockchain_tx_hash
            db.session.commit()

        return jsonify({'vc_id': vc_id, 'tx_hash': tx}), 200
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': str(e)}), 500


