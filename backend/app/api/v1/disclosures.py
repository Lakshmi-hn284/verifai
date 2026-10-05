"""
VERIFAI - Privacy & Selective Disclosure API Router
Enforces Zero-Trust Selective Disclosure, minimum information proofs,
and explicit human-in-the-loop consent.
"""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.domain.models import User, DisclosureConsent
from app.domain.schemas import (
    DisclosureApprovalRequest,
    ApiResponse
)
from app.services.privacy_engine import PrivacyEngine

router = APIRouter(prefix="/disclosures", tags=["Privacy & Selective Disclosure"])
privacy_engine = PrivacyEngine()


@router.get("/preview/{opportunity_id}", response_model=ApiResponse)
async def preview_minimum_disclosure(
    opportunity_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Minimum Disclosure preview:
    Categorizes available vault attributes into strictly Requested vs Protected/Redacted.
    Computes Disclosure Reduction Percentage (DRP).
    """
    preview = await privacy_engine.preview_minimum_disclosure(db, current_user, opportunity_id)
    return ApiResponse(
        success=True,
        data=preview
    )


@router.post("/approve", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def approve_disclosure(
    req: DisclosureApprovalRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Explicit user consent sign-off.
    Generates an authenticated W3C Verifiable Presentation containing ONLY approved fields.
    """
    client_ip = request.client.host if request.client else None
    result = await privacy_engine.approve_and_generate_package(
        db=db,
        user=current_user,
        opportunity_id=req.opportunity_id,
        allowed_attributes=req.allowed_attributes,
        ip_address=client_ip
    )

    return ApiResponse(
        success=True,
        data=result
    )


@router.get("/packages", response_model=ApiResponse)
async def list_application_packages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all user-approved minimum disclosure application packages."""
    query = (
        select(DisclosureConsent)
        .where(DisclosureConsent.user_id == current_user.id)
        .order_by(DisclosureConsent.created_at.desc())
    )
    res = await db.execute(query)
    consents = res.scalars().all()

    items = [
        {
            "id": c.id,
            "opportunity_id": c.opportunity_id,
            "user_approved": c.user_approved,
            "approved_at": c.approved_at.isoformat() if c.approved_at else None,
            "package_payload": c.package_payload,
            "created_at": c.created_at.isoformat()
        }
        for c in consents
    ]

    return ApiResponse(
        success=True,
        data={"packages": items, "count": len(items)}
    )
