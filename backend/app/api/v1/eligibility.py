"""
VERIFAI - Eligibility API Router
Endpoints for triggering hybrid eligibility evaluation and exploring evidence graphs.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.domain.models import User, Opportunity, EligibilityEvaluation
from app.domain.schemas import (
    EligibilityEvaluateRequest,
    ApiResponse
)
from app.core.errors import NotFoundError
from app.services.eligibility_engine import EligibilityEngine

router = APIRouter(prefix="/eligibility", tags=["Eligibility & Reasoning"])
engine = EligibilityEngine()


@router.post("/evaluate", response_model=ApiResponse)
async def evaluate_eligibility(
    data: EligibilityEvaluateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run hybrid eligibility evaluation:
    Combines deterministic rules + semantic matching + calibrated confidence
    + evidence traceability + grounded explainable markdown report.
    """
    evaluation = await engine.evaluate_eligibility(db, current_user, data.opportunity_id)

    return ApiResponse(
        success=True,
        data={
            "id": evaluation.id,
            "opportunity_id": evaluation.opportunity_id,
            "status": evaluation.status,
            "match_score": evaluation.match_score,
            "satisfied_rules": evaluation.satisfied_rules,
            "partially_satisfied_rules": evaluation.partially_satisfied_rules,
            "missing_rules": evaluation.missing_rules,
            "evidence_map": evaluation.evidence_map,
            "explanation_markdown": evaluation.explanation_markdown,
            "created_at": evaluation.created_at.isoformat()
        }
    )


@router.get("/opportunity/{opp_id}", response_model=ApiResponse)
async def get_latest_evaluation_for_opportunity(
    opp_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch the latest eligibility evaluation for a specific opportunity."""
    query = (
        select(EligibilityEvaluation)
        .where(
            EligibilityEvaluation.opportunity_id == opp_id,
            EligibilityEvaluation.user_id == current_user.id
        )
        .order_by(EligibilityEvaluation.created_at.desc())
    )
    res = await db.execute(query)
    eval_record = res.scalars().first()
    if not eval_record:
        # Trigger on-the-fly if not evaluated yet
        eval_record = await engine.evaluate_eligibility(db, current_user, opp_id)

    return ApiResponse(
        success=True,
        data={
            "id": eval_record.id,
            "opportunity_id": eval_record.opportunity_id,
            "status": eval_record.status,
            "match_score": eval_record.match_score,
            "satisfied_rules": eval_record.satisfied_rules,
            "partially_satisfied_rules": eval_record.partially_satisfied_rules,
            "missing_rules": eval_record.missing_rules,
            "evidence_map": eval_record.evidence_map,
            "explanation_markdown": eval_record.explanation_markdown,
            "created_at": eval_record.created_at.isoformat()
        }
    )


@router.get("/{id}/evidence", response_model=ApiResponse)
async def get_evidence_map(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve grounded evidence tree and document pointers."""
    res = await db.execute(
        select(EligibilityEvaluation).where(
            EligibilityEvaluation.id == id,
            EligibilityEvaluation.user_id == current_user.id
        )
    )
    record = res.scalar_one_or_none()
    if not record:
        raise NotFoundError("EligibilityEvaluation", id)

    return ApiResponse(
        success=True,
        data={
            "evaluation_id": record.id,
            "evidence_map": record.evidence_map,
            "satisfied_count": len(record.satisfied_rules),
            "missing_count": len(record.missing_rules)
        }
    )
