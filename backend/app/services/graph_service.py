"""
VERIFAI - Knowledge Graph Service
Coordinates syncing between relational records (User, Claim, Document, Opportunity)
and graph relationships.
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.models import User, Claim, Document, Opportunity
from app.providers.graph.networkx_adapter import NetworkXGraphProvider

graph_provider = NetworkXGraphProvider()


class GraphService:
    def __init__(self, provider: NetworkXGraphProvider = graph_provider):
        self.provider = provider

    async def sync_user_claim(self, user: User, claim: Claim, doc: Document = None) -> None:
        """Add user, claim, skill/credential, and document to the knowledge graph."""
        # 1. User Node
        await self.provider.add_node(user.id, "User", {
            "name": user.full_name,
            "email": user.email,
            "user_id": user.id
        })

        # 2. Claim Node
        claim_node_id = f"claim_{claim.id}"
        await self.provider.add_node(claim_node_id, "Claim", {
            "field_name": claim.field_name,
            "field_value": str(claim.field_value),
            "category": claim.category,
            "confidence": claim.confidence,
            "user_id": user.id
        })

        # User -> HAS_CLAIM -> Claim
        await self.provider.add_edge(user.id, claim_node_id, "HAS_CLAIM")

        # 3. Document Node & Evidence Edge
        if claim.document_id and doc:
            doc_node_id = f"doc_{doc.id}"
            await self.provider.add_node(doc_node_id, "Document", {
                "filename": doc.filename,
                "doc_type": doc.doc_type,
                "sha256": doc.sha256_hash[:10],
                "user_id": user.id
            })
            # Claim -> EVIDENCED_BY -> Document
            await self.provider.add_edge(claim_node_id, doc_node_id, "EVIDENCED_BY", {
                "page": claim.page_number or 1,
                "confidence": claim.confidence
            })

        # 4. If Skill, create Skill Node: Claim -> DEMONSTRATES -> Skill
        if claim.category == "SKILL":
            skill_node_id = f"skill_{str(claim.field_value).lower().replace(' ', '_')}"
            await self.provider.add_node(skill_node_id, "Skill", {
                "name": str(claim.field_value),
                "user_id": user.id
            })
            await self.provider.add_edge(claim_node_id, skill_node_id, "DEMONSTRATES")
            await self.provider.add_edge(user.id, skill_node_id, "HAS_SKILL")

        # 5. If Education, create Education Node
        elif claim.category == "EDUCATION":
            edu_node_id = f"edu_{claim.id}"
            await self.provider.add_node(edu_node_id, "Education", {
                "field": claim.field_name,
                "value": str(claim.field_value),
                "user_id": user.id
            })
            await self.provider.add_edge(claim_node_id, edu_node_id, "CERTIFIES")

    async def sync_opportunity(self, opportunity: Opportunity, requirements: List[Dict[str, Any]]) -> None:
        """Add opportunity and requirement nodes to the knowledge graph."""
        opp_node_id = f"opp_{opportunity.id}"
        await self.provider.add_node(opp_node_id, "Opportunity", {
            "title": opportunity.title,
            "organization": opportunity.organization,
            "type": opportunity.opportunity_type,
            "user_id": opportunity.user_id
        })

        for idx, req in enumerate(requirements):
            req_node_id = f"req_{opportunity.id}_{idx}"
            await self.provider.add_node(req_node_id, "Requirement", {
                "type": req.get("type", "general"),
                "condition": req.get("field", ""),
                "operator": req.get("operator", "REQUIRED"),
                "value": str(req.get("value", "")),
                "user_id": opportunity.user_id
            })
            # Opportunity -> REQUIRES -> Requirement
            await self.provider.add_edge(opp_node_id, req_node_id, "REQUIRES")

    async def get_user_graph(self, user_id: str) -> Dict[str, Any]:
        """Fetch visual graph payload."""
        return await self.provider.get_user_subgraph(user_id)
