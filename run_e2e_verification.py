#!/usr/bin/env python3
"""
End-to-end auto test runner for IDverse.

What it does (idempotent):
- Registers a unique user (or skips if exists)
- Logs in, captures JWT
- Issues a VC
- Fetches a verifier challenge and presents the VC
- Revokes the VC, then presents again to confirm status is false

Environment (optional):
- BASE_URL (default http://localhost:5000)

Prereqs you confirmed:
- SIGN_MODE=ed25519 (backend)
- BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545 (if CHAIN_MODE=real)

Run:
  python run_e2e_verification.py
"""

import os
import time
import json
import random
import string
import requests


BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


def _print(step: str, payload=None):
    print(f"\n=== {step} ===")
    if payload is not None:
        try:
            print(json.dumps(payload, indent=2))
        except Exception:
            print(payload)


def register_or_skip(email: str, username: str, password: str) -> None:
    url = f"{BASE_URL}/auth/register"
    body = {"username": username, "email": email, "password": password}
    resp = requests.post(url, json=body, timeout=10)
    if resp.status_code == 201:
        _print("REGISTERED", resp.json())
    elif resp.status_code == 409:
        _print("REGISTER SKIPPED (already exists)")
    else:
        raise RuntimeError(f"Register failed: {resp.status_code} {resp.text}")


def login(email: str, password: str) -> str:
    url = f"{BASE_URL}/auth/login"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Login failed: {resp.status_code} {resp.text}")
    data = resp.json()
    _print("LOGIN", {"user": data.get("user"), "token_len": len(data.get("access_token", ""))})
    return data["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def issue_vc(token: str) -> dict:
    url = f"{BASE_URL}/vc/issue"
    body = {
        "type": "AadhaarLink",
        "claims": {"aadhaarLast4": "1234", "dob": "1960-02-01"}
    }
    resp = requests.post(url, json=body, headers=auth_headers(token), timeout=20)
    if resp.status_code != 201:
        raise RuntimeError(f"Issue VC failed: {resp.status_code} {resp.text}")
    data = resp.json()
    _print("VC ISSUED", {k: data.get(k) for k in ["vc_id", "cid", "tx_hash"]})
    return data


def get_challenge() -> str:
    url = f"{BASE_URL}/vc/challenge"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Challenge failed: {resp.status_code} {resp.text}")
    return resp.json()["challenge"]


def present_full(vc: dict, challenge: str) -> dict:
    url = f"{BASE_URL}/vc/present"
    resp = requests.post(url, json={"vc": vc, "challenge": challenge}, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"Present failed: {resp.status_code} {resp.text}")
    data = resp.json()
    _print("PRESENT (full VC)", data)
    return data


def revoke_vc(token: str, vc_id: str) -> dict:
    url = f"{BASE_URL}/vc/revoke"
    body = {"vc_id": vc_id, "reason": "e2e-test"}
    resp = requests.post(url, json=body, headers=auth_headers(token), timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f"Revoke failed: {resp.status_code} {resp.text}")
    data = resp.json()
    _print("REVOKE", data)
    return data


def main():
    # Unique identity per run
    suffix = str(int(time.time())) + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    email = f"demo+{suffix}@example.com"
    username = f"demo{suffix}"
    password = "Pass@1234"

    # Health check + issuer info
    try:
        hi = requests.get(f"{BASE_URL}/vc/issuer-info", timeout=10).json()
        _print("ISSUER INFO", hi)
        if (os.getenv("SIGN_MODE", "ed25519").lower() == "ed25519") and not str(hi.get("public_key_hex", "")).strip():
            print("WARNING: SIGN_MODE=ed25519 but issuer public key is empty; ensure keys are set in .env")
    except Exception as e:
        _print("ISSUER INFO error", str(e))

    # Register + login
    register_or_skip(email, username, password)
    token = login(email, password)

    # Issue VC
    issued = issue_vc(token)
    vc_id = issued.get("vc_id")
    vc = issued.get("vc")

    # Present
    ch = get_challenge()
    pres = present_full(vc, ch)
    ok1 = bool(pres.get("verified"))

    # Revoke + present again
    revoke_vc(token, vc_id)
    ch2 = get_challenge()
    pres2 = present_full(vc, ch2)
    ok2 = not bool(pres2.get("verified"))

    summary = {
        "base_url": BASE_URL,
        "vc_id": vc_id,
        "present_verified": ok1,
        "present_after_revoke_verified": ok2,
    }
    _print("SUMMARY", summary)

    # Simple exit code for CI-like use
    if ok1 and ok2:
        print("\nE2E TEST: PASS")
        return 0
    print("\nE2E TEST: FAIL")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())




