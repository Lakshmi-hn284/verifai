"""
VERIFAI - Unit Tests for Cryptography & Security Primitives
Tests:
- Argon2id password hashing and verification
- AES-256-GCM encryption and decryption
- Tamper resilience on ciphertext and nonce
- Per-user HKDF key derivation isolation
- SHA-256 hashing
- JWT generation and decoding
"""
import pytest
from app.core.security import (
    hash_password,
    verify_password,
    compute_sha256,
    derive_user_vault_key,
    encrypt_vault_payload,
    decrypt_vault_payload,
    create_access_token,
    decode_token
)


def test_argon2id_hashing():
    pw = "SuperSecurePassword2026!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert hashed.startswith("$argon2id$")
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_aes_256_gcm_encryption_and_decryption():
    key = bytes.fromhex("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    secret_data = b"Transcript: Computer Science & Engineering, CGPA: 9.25"
    
    ciphertext, nonce = encrypt_vault_payload(secret_data, key)
    assert ciphertext != secret_data
    assert len(nonce) == 12  # 96-bit nonce
    
    decrypted = decrypt_vault_payload(ciphertext, nonce, key)
    assert decrypted == secret_data


def test_aes_gcm_tamper_detection():
    key = bytes.fromhex("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    secret_data = b"Degree: Bachelor of Technology"
    ciphertext, nonce = encrypt_vault_payload(secret_data, key)
    
    # Tamper with 1 byte in ciphertext
    tampered = bytearray(ciphertext)
    tampered[0] ^= 0xFF
    
    # Decryption MUST fail with exception
    with pytest.raises(Exception):
        decrypt_vault_payload(bytes(tampered), nonce, key)


def test_hkdf_per_user_key_isolation():
    key_user1 = derive_user_vault_key("user_uuid_1")
    key_user2 = derive_user_vault_key("user_uuid_2")
    
    assert len(key_user1) == 32  # 256 bits
    assert len(key_user2) == 32
    assert key_user1 != key_user2  # Cryptographic isolation between users


def test_sha256_integrity():
    content = b"VERIFAI Privacy Preserving Credentials"
    h1 = compute_sha256(content)
    h2 = compute_sha256(content)
    assert h1 == h2
    assert len(h1) == 64


def test_jwt_lifecycle():
    payload = {"sub": "user_123", "email": "test@verifai.io"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_123"
    assert decoded["email"] == "test@verifai.io"
    assert decoded["type"] == "access"
