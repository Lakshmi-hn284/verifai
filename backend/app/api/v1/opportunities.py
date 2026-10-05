"""
VERIFAI - Opportunities API Router
Endpoints for ingesting opportunity descriptions and viewing structured requirements.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.domain.models import User
from app.domain.schemas import (
    OpportunityCreateRequest,
    OpportunityResponse,
    ApiResponse
)
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])
opp_service = OpportunityService()


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    data: OpportunityCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a job, internship, or scholarship description.
    Automatically parses text into structured requirement conditions with JSON schema validation.
    """
    opp = await opp_service.create_opportunity(db, current_user, data)
    return ApiResponse(
        success=True,
        data=OpportunityResponse.model_validate(opp).model_dump()
    )


@router.get("", response_model=ApiResponse)
async def list_opportunities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all ingested opportunities for current user."""
    opps = await opp_service.list_opportunities(db, current_user.id)
    items = [OpportunityResponse.model_validate(o).model_dump() for o in opps]
    return ApiResponse(
        success=True,
        data={"opportunities": items, "count": len(items)}
    )


@router.get("/{id}", response_model=ApiResponse)
async def get_opportunity(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve opportunity criteria and condition rules."""
    opp = await opp_service.get_opportunity(db, current_user.id, id)
    return ApiResponse(
        success=True,
        data=OpportunityResponse.model_validate(opp).model_dump()
    )
