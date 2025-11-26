import os
import base64
from typing import Optional
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

ISSUER_KEYS_DIR = os.getenv("ISSUER_KEYS_DIR", "./instance/issuer_keys")
os.makedirs(ISSUER_KEYS_DIR, exist_ok=True)

class Ed25519SigningService:
    """
    Simple Ed25519 signing service.
    Persists private key bytes to ISSUER_KEYS_DIR/{issuer_id}.key
    """
    def __init__(self, issuer_id: str):
        self.issuer_id = issuer_id
        self.key_path = os.path.join(ISSUER_KEYS_DIR, f"{issuer_id}.key")
        self._sk = self._load_or_create_key()
        self._vk = self._sk.verify_key

    def _load_or_create_key(self) -> SigningKey:
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as fh:
                raw = fh.read()
            return SigningKey(raw)
        sk = SigningKey.generate()
        with open(self.key_path, "wb") as fh:
            fh.write(sk.encode())
        return sk

    def sign(self, payload: bytes) -> str:
        sig = self._sk.sign(payload).signature
        return base64.b64encode(sig).decode("utf-8")

    def public_key_b64(self) -> str:
        return base64.b64encode(self._vk.encode()).decode("utf-8")

    @staticmethod
    def verify(public_key_b64: str, signature_b64: str, payload: bytes) -> bool:
        try:
            vk_bytes = base64.b64decode(public_key_b64)
            sig = base64.b64decode(signature_b64)
            vk = VerifyKey(vk_bytes)
            vk.verify(payload, sig)
            return True
        except (BadSignatureError, Exception): 
            return False