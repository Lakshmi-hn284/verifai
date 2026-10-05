"""
VERIFAI - Encrypted Local Storage Provider
Implements AES-256-GCM authenticated encryption at rest for all stored documents.
Derives per-user isolated keys via HKDF.
"""
import os
import aiofiles
from pathlib import Path
from typing import Tuple
from app.providers.base import StorageProvider
from app.core.config import settings
from app.core.security import derive_user_vault_key, encrypt_vault_payload, decrypt_vault_payload
from app.core.errors import VaultSecurityError


class EncryptedLocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str = settings.VAULT_STORAGE_PATH):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_blob(self, user_id: str, document_id: str, data: bytes) -> Tuple[str, str]:
        """Encrypts data with user-derived AES-256 key and writes to disk."""
        user_dir = self.base_path / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = user_dir / f"{document_id}.enc"
        
        # Derive per-user key
        user_key = derive_user_vault_key(user_id)
        
        # Encrypt with AES-256-GCM
        ciphertext, nonce = encrypt_vault_payload(data, user_key)
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(ciphertext)
            
        return str(file_path), nonce.hex()

    async def get_blob(self, user_id: str, storage_path: str, nonce_hex: str) -> bytes:
        """Reads encrypted file and decrypts it with user-derived key."""
        target_path = Path(storage_path)
        if not target_path.exists():
            raise VaultSecurityError("Requested vault file does not exist on disk")

        # Security check: ensure path is within base vault path
        try:
            target_path.resolve().relative_to(self.base_path.resolve())
        except ValueError:
            raise VaultSecurityError("Directory traversal detected")

        async with aiofiles.open(target_path, "rb") as f:
            ciphertext = await f.read()

        user_key = derive_user_vault_key(user_id)
        nonce = bytes.fromhex(nonce_hex)
        
        try:
            plaintext = decrypt_vault_payload(ciphertext, nonce, user_key)
            return plaintext
        except Exception as e:
            raise VaultSecurityError(f"Integrity check failed: file decryption error ({str(e)})")

    async def delete_blob(self, storage_path: str) -> bool:
        """Securely deletes file from disk."""
        target_path = Path(storage_path)
        if target_path.exists():
            try:
                target_path.resolve().relative_to(self.base_path.resolve())
                os.remove(target_path)
                return True
            except (ValueError, OSError):
                return False
        return False
