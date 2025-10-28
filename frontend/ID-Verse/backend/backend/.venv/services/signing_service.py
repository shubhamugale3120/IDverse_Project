import os
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

KEY_PATH = os.environ.get("PRIVATE_KEY_PATH", "keys/issuer_private.pem")

def generate_keys():
    os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
    priv = ed25519.Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub = priv.public_key()
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(KEY_PATH, "wb") as f:
        f.write(priv_bytes)
    with open(KEY_PATH + ".pub", "wb") as f:
        f.write(pub_bytes)

def load_private_key():
    with open(KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def sign_bytes(payload_bytes):
    sk = load_private_key()
    sig = sk.sign(payload_bytes)
    return sig.hex()

def get_public_pem():
    with open(KEY_PATH + ".pub", "rb") as f:
        return f.read().decode('utf-8')