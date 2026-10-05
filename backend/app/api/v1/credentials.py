"""
VERIFAI - Credentials & Claims API Router
Endpoints for viewing, creating, and updating structured user claims.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.domain.models import User, Claim
from app.domain.schemas import (
    ClaimCreateRequest,
    ClaimResponse,
    ApiResponse,
)
from app.core.errors import NotFoundError
from app.services.graph_service import GraphService

router = APIRouter(prefix="/credentials", tags=["Credentials & Claims"])
graph_service = GraphService()


@router.get("", response_model=ApiResponse)
async def list_credentials(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all structured claims belonging to the authenticated user."""
    query = select(Claim).where(Claim.user_id == current_user.id).order_by(Claim.category, Claim.created_at.desc())
    result = await db.execute(query)
    claims = result.scalars().all()

    items = [ClaimResponse.model_validate(c).model_dump() for c in claims]
    return ApiResponse(
        success=True,
        data={"claims": items, "count": len(items)}
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_credential_claim(
    req: ClaimCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually assert a credential claim."""
    claim = Claim(
        user_id=current_user.id,
        category=req.category.upper(),
        field_name=req.field_name,
        field_value=req.field_value,
        confidence=0.85,  # Self-asserted baseline confidence
        verification_status="USER_VERIFIED",
        issuer=req.issuer or "Self-Asserted",
        issued_date=req.issued_date
    )
    db.add(claim)
    await db.flush()

    # Sync into knowledge graph
    await graph_service.sync_user_claim(current_user, claim)

    await db.commit()
    await db.refresh(claim)

    return ApiResponse(
        success=True,
        data=ClaimResponse.model_validate(claim).model_dump()
    )


@router.get("/{id}", response_model=ApiResponse)
async def get_credential(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve details of a specific credential claim."""
    query = select(Claim).where(Claim.id == id, Claim.user_id == current_user.id)
    result = await db.execute(query)
    claim = result.scalar_one_or_none()
    if not claim:
        raise NotFoundError("Claim", id)

    return ApiResponse(
        success=True,
        data=ClaimResponse.model_validate(claim).model_dump()
    )
