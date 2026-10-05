"""
VERIFAI - Document Vault & Extraction Service
Handles file security validation, AES-256-GCM encryption, integrity hashing,
multimodal claim extraction, and audit log integration.
"""
from pathlib import Path
from typing import List, Optional, Tuple
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import compute_sha256
from app.core.errors import VaultSecurityError, NotFoundError
from app.core.audit import log_security_event
from app.domain.models import Document, Claim, User
from app.providers.storage.encrypted_local import EncryptedLocalStorageProvider
from app.providers.document_ai.multimodal_parser import MultimodalDocumentProvider

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg"
}

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15MB


class DocumentService:
    def __init__(
        self,
        storage_provider: Optional[EncryptedLocalStorageProvider] = None,
        doc_ai_provider: Optional[MultimodalDocumentProvider] = None
    ):
        self.storage = storage_provider or EncryptedLocalStorageProvider()
        self.doc_ai = doc_ai_provider or MultimodalDocumentProvider()

    async def upload_and_process_document(
        self,
        db: AsyncSession,
        user: User,
        file: UploadFile,
        ip_address: Optional[str] = None
    ) -> Document:
        """Validate, encrypt, store, and automatically extract claims from uploaded document."""
        # 1. Validate file extension
        filename = file.filename or "uploaded_document"
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise VaultSecurityError(
                f"Unsupported file extension '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 2. Read bytes & check size limit
        file_bytes = await file.read()
        file_size = len(file_bytes)
        if file_size == 0:
            raise VaultSecurityError("Uploaded file is empty")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise VaultSecurityError(
                f"File size ({file_size / (1024*1024):.2f}MB) exceeds maximum limit of 15MB"
            )

        # 3. MIME validation
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_MIME_TYPES:
            # Fallback check based on extension
            if suffix == ".pdf":
                content_type = "application/pdf"
            elif suffix == ".png":
                content_type = "image/png"
            elif suffix in [".jpg", ".jpeg"]:
                content_type = "image/jpeg"
            else:
                raise VaultSecurityError(f"Unsupported MIME type: {content_type}")

        # 4. Compute SHA-256 integrity hash
        sha256_hash = compute_sha256(file_bytes)

        # 5. Create initial document database record
        doc = Document(
            user_id=user.id,
            filename=filename,
            content_type=content_type,
            file_size_bytes=file_size,
            storage_path="",
            nonce_hex="",
            sha256_hash=sha256_hash,
            status="PROCESSING",
            doc_type="OTHER",
            extracted_metadata={}
        )
        db.add(doc)
        await db.flush()

        # 6. Save encrypted payload in vault storage
        storage_path, nonce_hex = await self.storage.save_blob(user.id, doc.id, file_bytes)
        doc.storage_path = storage_path
        doc.nonce_hex = nonce_hex

        # 7. Execute Multimodal Document Extraction
        extraction_res = await self.doc_ai.extract_document_structure(file_bytes, filename, content_type)
        doc.doc_type = extraction_res.doc_type
        doc.extracted_metadata = extraction_res.layout_metadata
        doc.status = "EXTRACTED"

        # 8. Materialize extracted fields as structured claims
        for field in extraction_res.extracted_fields:
            claim = Claim(
                user_id=user.id,
                document_id=doc.id,
                category=field.category,
                field_name=field.field_name,
                field_value=field.value,
                confidence=field.confidence,
                page_number=field.page_number,
                bounding_box=field.bounding_box,
                verification_status="EXTRACTED",
                issuer=field.issuer,
                issued_date=field.issued_date
            )
            db.add(claim)

        # 9. Audit logging
        await log_security_event(
            db=db,
            event_type="DOCUMENT_UPLOADED",
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            details={
                "document_id": doc.id,
                "filename": doc.filename,
                "doc_type": doc.doc_type,
                "sha256_hash": doc.sha256_hash,
                "extracted_claims_count": len(extraction_res.extracted_fields)
            }
        )

        await db.commit()
        await db.refresh(doc)
        return doc

    async def get_document(self, db: AsyncSession, user_id: str, document_id: str) -> Document:
        """Fetch document verifying user ownership."""
        query = select(Document).where(Document.id == document_id, Document.user_id == user_id)
        result = await db.execute(query)
        doc = result.scalar_one_or_none()
        if not doc:
            raise NotFoundError("Document", document_id)
        return doc

    async def list_documents(self, db: AsyncSession, user_id: str) -> List[Document]:
        """List all vault documents for the authenticated user."""
        query = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def delete_document(
        self,
        db: AsyncSession,
        user_id: str,
        document_id: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """Securely deletes document from vault disk, database, and logs audit record."""
        doc = await self.get_document(db, user_id, document_id)
        
        # Remove encrypted blob from storage
        await self.storage.delete_blob(doc.storage_path)

        # Remove from database (cascades to claims)
        await db.delete(doc)

        await log_security_event(
            db=db,
            event_type="DOCUMENT_DELETED",
            status="SUCCESS",
            user_id=user_id,
            ip_address=ip_address,
            details={"document_id": document_id, "filename": doc.filename}
        )
        await db.commit()
        return True
