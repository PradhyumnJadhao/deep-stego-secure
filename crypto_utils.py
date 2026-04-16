"""
Cryptographic utilities for Deep-Stego Secure.
Simple passphrase-based AES-256-GCM encryption + Stego-ID generation.
"""
import os, hashlib, base64, secrets, string
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ── Stego-ID Generation ──────────────────────────────────────────────────────
def generate_stego_id(length=6):
    chars = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(chars) for _ in range(length))
    return f"DSS-{code}"

# ── Passphrase → AES-256 Key ─────────────────────────────────────────────────
def derive_key_from_passphrase(passphrase: str, salt: bytes = None):
    """Derive a 256-bit AES key from a passphrase using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=480_000)
    key = kdf.derive(passphrase.encode('utf-8'))
    return key, salt

# ── AES-256-GCM Encrypt / Decrypt ────────────────────────────────────────────
def encrypt_image_bytes(data: bytes, passphrase: str) -> dict:
    """Encrypt data with a passphrase. Returns dict with ct, nonce, salt (all b64)."""
    key, salt = derive_key_from_passphrase(passphrase)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, data, None)
    return {
        "ct": ct,
        "nonce": base64.b64encode(nonce).decode(),
        "salt": base64.b64encode(salt).decode()
    }

def decrypt_image_bytes(ct: bytes, passphrase: str, nonce_b64: str, salt_b64: str) -> bytes:
    """Decrypt data with a passphrase. Raises InvalidTag on wrong passphrase."""
    salt = base64.b64decode(salt_b64)
    nonce = base64.b64decode(nonce_b64)
    key, _ = derive_key_from_passphrase(passphrase, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None)
