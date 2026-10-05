"""
VERIFAI - Career Gap Intelligence Router
Endpoints for aggregated missing skills and proactive competency guidance.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.domain.models import User
from app.domain.schemas import ApiResponse
from app.services.career_service import CareerGapService

router = APIRouter(prefix="/career", tags=["Career Gap Intelligence"])
career_service = CareerGapService()


@router.get("/gaps", response_model=ApiResponse)
async def get_career_skill_gaps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compute recurring skill gaps across all analyzed opportunities.
    Returns prioritized list of missing skills and market readiness percentage.
    """
    gaps = await career_service.analyze_skill_gaps(db, current_user)
    return ApiResponse(
        success=True,
        data=gaps
    )
