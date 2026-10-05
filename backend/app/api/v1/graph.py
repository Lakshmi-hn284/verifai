"""
VERIFAI - Knowledge Graph API Router
Returns graph nodes and edges for visualization and reasoning.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.domain.models import User, Claim, Document, Opportunity
from app.domain.schemas import ApiResponse
from app.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])
graph_service = GraphService()


@router.get("", response_model=ApiResponse)
async def get_user_knowledge_graph(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve user's complete Personal Credential Knowledge Graph.
    Includes User, Claims, Evidencing Documents, Skills, and Opportunities.
    """
    # Ensure current user's claims and documents are synced in the graph
    claims_res = await db.execute(select(Claim).where(Claim.user_id == current_user.id))
    claims = claims_res.scalars().all()

    docs_res = await db.execute(select(Document).where(Document.user_id == current_user.id))
    docs_map = {d.id: d for d in docs_res.scalars().all()}

    for c in claims:
        doc = docs_map.get(c.document_id) if c.document_id else None
        await graph_service.sync_user_claim(current_user, c, doc)

    opps_res = await db.execute(select(Opportunity).where(Opportunity.user_id == current_user.id))
    for opp in opps_res.scalars().all():
        reqs = opp.extracted_requirements.get("requirements", [])
        await graph_service.sync_opportunity(opp, reqs)

    graph_payload = await graph_service.get_user_graph(current_user.id)

    return ApiResponse(
        success=True,
        data=graph_payload
    )
