"""
VERIFAI - Audit API Router
Exposes read-only tamper-evident security audit logs for the authenticated user.
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.domain.models import User, AuditLog
from app.domain.schemas import ApiResponse

router = APIRouter(prefix="/audit", tags=["Security Audit"])


@router.get("/logs", response_model=ApiResponse)
async def get_my_audit_logs(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve user's tamper-resistant audit trail entries."""
    query = (
        select(AuditLog)
        .where(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    items = [
        {
            "id": log.id,
            "event_type": log.event_type,
            "status": log.status,
            "ip_address": log.ip_address,
            "metadata_hash": log.metadata_hash,
            "details": log.details,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]

    return ApiResponse(
        success=True,
        data={"logs": items, "count": len(items)}
    )
