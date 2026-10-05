"""
VERIFAI - Core Security & Cryptography Module
Implements:
- Argon2id password hashing
- AES-256-GCM authenticated encryption/decryption
- Per-user cryptographic key derivation (HKDF)
- SHA-256 integrity hashing
- JWT token lifecycle management
"""
import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from jose import jwt, JWTError

from app.core.config import settings

# Initialize Argon2id with memory-hard parameters per security specification
# time_cost=2, memory_cost=65536 KiB (64MB), parallelism=8, hash_len=32, salt_len=16
_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=8,
    hash_len=32,
    salt_len=16
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2id hash."""
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHash):
        return False


def compute_sha256(data: bytes) -> str:
    """Compute the SHA-256 hex digest of arbitrary byte content."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


def derive_user_vault_key(user_id: str, salt: bytes = b"verifai_vault_salt_v1") -> bytes:
    """
    Derive a 256-bit AES key specific to a user from the master vault key using HKDF-SHA256.
    Ensures cryptographic isolation between users.
    """
    master_key = bytes.fromhex(settings.VAULT_MASTER_KEY_HEX)
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=f"verifai_user_key_{user_id}".encode("utf-8"),
    )
    return hkdf.derive(master_key)


def encrypt_vault_payload(plaintext: bytes, key: bytes) -> Tuple[bytes, bytes]:
    """
    Encrypt plaintext bytes using AES-256-GCM.
    Returns: (ciphertext_with_tag, 96_bit_nonce)
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return ciphertext, nonce


def decrypt_vault_payload(ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
    """
    Decrypt ciphertext bytes using AES-256-GCM with nonce and key.
    Raises InvalidTag if ciphertext or tag was tampered with.
    """
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": now, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a signed JWT refresh token with longer expiration."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": now, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token signature and expiration."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
