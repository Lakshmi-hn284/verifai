"""
VERIFAI - Users API Router
Handles User Profile and Dashboard Summary.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, get_current_user
from app.domain.models import User, Document, Claim, Opportunity, EligibilityEvaluation
from app.domain.schemas import UserResponse, ApiResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Retrieve authenticated user's profile metadata."""
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user).model_dump()
    )


@router.get("/me/dashboard", response_model=ApiResponse)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve personalized dashboard summary metrics:
    - total documents
    - total claims & verified claims
    - opportunity count
    - average eligibility match score
    """
    # Documents count
    doc_count_res = await db.execute(
        select(func.count(Document.id)).where(Document.user_id == current_user.id)
    )
    doc_count = doc_count_res.scalar() or 0

    # Claims count
    claims_count_res = await db.execute(
        select(func.count(Claim.id)).where(Claim.user_id == current_user.id)
    )
    total_claims = claims_count_res.scalar() or 0

    verified_claims_res = await db.execute(
        select(func.count(Claim.id)).where(
            Claim.user_id == current_user.id,
            Claim.verification_status.in_(["USER_VERIFIED", "ISSUER_VERIFIED"])
        )
    )
    verified_claims = verified_claims_res.scalar() or 0

    # Opportunities count
    opp_count_res = await db.execute(
        select(func.count(Opportunity.id)).where(Opportunity.user_id == current_user.id)
    )
    total_opportunities = opp_count_res.scalar() or 0

    # Average match score
    avg_score_res = await db.execute(
        select(func.avg(EligibilityEvaluation.match_score)).where(EligibilityEvaluation.user_id == current_user.id)
    )
    avg_score = avg_score_res.scalar()
    avg_match_score = round(float(avg_score), 1) if avg_score is not None else 0.0

    return ApiResponse(
        success=True,
        data={
            "documents_count": doc_count,
            "total_claims": total_claims,
            "verified_claims": verified_claims,
            "opportunities_count": total_opportunities,
            "average_match_score": avg_match_score,
            "user": UserResponse.model_validate(current_user).model_dump()
        }
    )
