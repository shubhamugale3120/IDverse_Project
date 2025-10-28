import os, json, hashlib, time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from services.signing_service import sign_bytes, get_public_pem
from services.ipfs_service import upload_bytes, upload_file, cat
from services.chain_service import load_contract, issue_on_chain
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Simple in-memory DB for demo; replace with real DB in production
DB = {"vcs": {}}

def sha256_hex(b: bytes) -> str:
    import hashlib
    return hashlib.sha256(b).hexdigest()

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/ipfs/upload", methods=["POST"])
def ipfs_upload_route():
    if "file" in request.files:
        f = request.files["file"]
        path = "./tmp_upload"
        os.makedirs(path, exist_ok=True)
        fp = os.path.join(path, f.filename)
        f.save(fp)
        cid = upload_file(fp)
        return jsonify({"cid": cid})
    data = request.get_data()
    cid = upload_bytes(data)
    return jsonify({"cid": cid})

@app.route("/vc/request-issue", methods=["POST"])
def request_issue():
    data = request.get_json()
    holder = data.get("holder")
    vcType = data.get("vcType")
    credSubj = data.get("credentialSubject", {})
    payload = {
        "type": vcType,
        "holder": holder,
        "credentialSubject": credSubj,
        "issuanceDate": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    cid = upload_bytes(payload_bytes)
    signature = sign_bytes(payload_bytes)
    payload_hash = sha256_hex(payload_bytes)
    vc_id = len(DB["vcs"]) + 1
    DB["vcs"][vc_id] = {"cid": cid, "signature": signature, "issuer_pub": get_public_pem(), "holder": holder, "type": vcType, "issuedAt": payload["issuanceDate"], "hash": payload_hash}
    # Optionally record on chain (if configured)
    # Example: record hash (converted to bytes32) via chain_service.issue_on_chain
    return jsonify({"vc_id": vc_id, "cid": cid, "hash": payload_hash, "signature": signature})

@app.route("/vc/verify", methods=["POST"])
def vc_verify():
    data = request.get_json()
    cid = data.get("cid")
    signature = data.get("signature")
    # Look up local DB by cid
    found = None
    for k, v in DB["vcs"].items():
        if v["cid"] == cid:
            found = v
            break
    if not found:
        return jsonify({"verified": False, "reason": "not_found"})
    # Retrieve payload bytes from IPFS
    try:
        payload_bytes = cat(cid)
    except Exception as e:
        return jsonify({"verified": False, "reason": "ipfs_error", "error": str(e)})
    if sha256_hex(payload_bytes) != found["hash"]:
        return jsonify({"verified": False, "reason": "hash_mismatch"})
    # verify signature using public key
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    pub = serialization.load_pem_public_key(found["issuer_pub"].encode())
    try:
        pub.verify(bytes.fromhex(signature), payload_bytes)
        verified = True
    except Exception:
        verified = False
    return jsonify({"verified": verified, "holder": found["holder"], "vc_type": found["type"]})

if __name__ == "__main__":
    app.run(host=os.environ.get("FLASK_HOST", "127.0.0.1"), port=int(os.environ.get("FLASK_PORT", 5000)))
