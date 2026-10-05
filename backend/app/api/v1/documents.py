"""
VERIFAI - Document Vault API Router
Endpoints for uploading encrypted documents, viewing metadata, listing claims, and secure deletion.
"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, get_current_user
from app.domain.models import User, Document, Claim
from app.domain.schemas import (
    DocumentResponse,
    DocumentDetailResponse,
    ClaimResponse,
    ApiResponse
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Document Vault"])
doc_service = DocumentService()


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Securely upload a document into the AES-256-GCM encrypted vault.
    Performs MIME sniffing, extension check, SHA-256 integrity hashing,
    and automatic multimodal claim extraction.
    """
    client_ip = request.client.host if request.client else None
    doc = await doc_service.upload_and_process_document(
        db=db,
        user=current_user,
        file=file,
        ip_address=client_ip
    )

    return ApiResponse(
        success=True,
        data={
            "id": doc.id,
            "filename": doc.filename,
            "content_type": doc.content_type,
            "file_size_bytes": doc.file_size_bytes,
            "status": doc.status,
            "doc_type": doc.doc_type,
            "sha256_hash": doc.sha256_hash,
            "created_at": doc.created_at.isoformat()
        }
    )


@router.get("", response_model=ApiResponse)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents in the user's encrypted vault."""
    docs = await doc_service.list_documents(db, current_user.id)
    
    # Enrich with claims count
    items = []
    for d in docs:
        c_count_res = await db.execute(
            select(func.count(Claim.id)).where(Claim.document_id == d.id)
        )
        claims_count = c_count_res.scalar() or 0
        items.append({
            "id": d.id,
            "filename": d.filename,
            "content_type": d.content_type,
            "file_size_bytes": d.file_size_bytes,
            "status": d.status,
            "doc_type": d.doc_type,
            "sha256_hash": d.sha256_hash,
            "claims_count": claims_count,
            "created_at": d.created_at.isoformat()
        })

    return ApiResponse(
        success=True,
        data={"documents": items, "count": len(items)}
    )


@router.get("/{id}", response_model=ApiResponse)
async def get_document(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve detailed metadata and extraction results for a specific document."""
    doc = await doc_service.get_document(db, current_user.id, id)
    
    claims_res = await db.execute(select(Claim).where(Claim.document_id == doc.id))
    claims = claims_res.scalars().all()

    return ApiResponse(
        success=True,
        data={
            "id": doc.id,
            "filename": doc.filename,
            "content_type": doc.content_type,
            "file_size_bytes": doc.file_size_bytes,
            "status": doc.status,
            "doc_type": doc.doc_type,
            "sha256_hash": doc.sha256_hash,
            "extracted_metadata": doc.extracted_metadata,
            "claims": [ClaimResponse.model_validate(c).model_dump() for c in claims],
            "created_at": doc.created_at.isoformat()
        }
    )


@router.get("/{id}/claims", response_model=ApiResponse)
async def get_document_claims(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all structured claims derived from a specific document."""
    doc = await doc_service.get_document(db, current_user.id, id)
    claims_res = await db.execute(select(Claim).where(Claim.document_id == doc.id))
    claims = claims_res.scalars().all()

    return ApiResponse(
        success=True,
        data={"claims": [ClaimResponse.model_validate(c).model_dump() for c in claims]}
    )


@router.delete("/{id}", response_model=ApiResponse)
async def delete_document(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Securely delete a document, its ciphertext file, and its derived claims."""
    client_ip = request.client.host if request.client else None
    await doc_service.delete_document(db, current_user.id, id, client_ip)

    return ApiResponse(
        success=True,
        data={"message": "Document securely deleted"}
    )
