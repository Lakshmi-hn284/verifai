"""
VERIFAI - Opportunity Ingestion & Requirement Extraction Service
Converts natural language job/internship/scholarship descriptions into typed,
schema-validated deterministic rule sets.
"""
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.models import Opportunity, User
from app.domain.schemas import OpportunityCreateRequest
from app.core.errors import NotFoundError
from app.services.graph_service import GraphService


class OpportunityService:
    def __init__(self, graph_svc: Optional[GraphService] = None):
        self.graph_service = graph_svc or GraphService()

    def extract_structured_requirements(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses opportunity description into deterministic condition objects.
        Validates condition schemas (type, field, operator, value, importance).
        """
        lower = text.lower()
        rules: List[Dict[str, Any]] = []

        # 1. Degree / Branch Requirements
        if any(k in lower for k in ["cse", "computer science", "information technology", "it"]):
            rules.append({
                "type": "education",
                "field": "degree_major",
                "operator": "IN",
                "value": ["Computer Science", "CSE", "Information Technology", "IT"],
                "importance": "REQUIRED",
                "description": "Degree in Computer Science or Information Technology"
            })

        if any(k in lower for k in ["bachelor", "b.tech", "btech", "b.e", "undergraduate"]):
            rules.append({
                "type": "education",
                "field": "degree_level",
                "operator": "==",
                "value": "Bachelor of Technology",
                "importance": "REQUIRED",
                "description": "Bachelor's degree or equivalent"
            })

        # 2. CGPA / Academic Requirements
        cgpa_match = re.search(r'(?:cgpa|gpa|marks)\s*(?:above|minimum|at least|>=|>)?\s*([0-9]+\.?[0-9]*)', lower)
        if cgpa_match:
            try:
                min_cgpa = float(cgpa_match.group(1))
                if 0.0 < min_cgpa <= 10.0:
                    rules.append({
                        "type": "academic",
                        "field": "cgpa",
                        "operator": ">=",
                        "value": min_cgpa,
                        "importance": "REQUIRED",
                        "description": f"Minimum CGPA of {min_cgpa} or higher"
                    })
            except ValueError:
                pass
        else:
            # Check for percentage if no 10-point scale
            pct_match = re.search(r'([0-9]{2})\s*%\s*(?:aggregate|marks)?', lower)
            if pct_match:
                min_pct = float(pct_match.group(1))
                rules.append({
                    "type": "academic",
                    "field": "percentage",
                    "operator": ">=",
                    "value": min_pct,
                    "importance": "REQUIRED",
                    "description": f"Minimum aggregate score of {min_pct}%"
                })

        # 3. Programming & Technical Skills Requirements
        tech_catalog = [
            ("python", "Python"),
            ("machine learning", "Machine Learning"),
            ("react", "React.js"),
            ("sql", "SQL"),
            ("docker", "Docker"),
            ("aws", "Amazon Web Services"),
            ("fastapi", "FastAPI"),
            ("typescript", "TypeScript"),
            ("data structures", "Data Structures & Algorithms"),
            ("german", "German A2"),
            ("cloud", "Cloud Experience"),
        ]

        for trigger, skill_name in tech_catalog:
            if trigger in lower:
                importance = "REQUIRED" if any(w in lower for w in [f"must have {trigger}", f"required: {trigger}", f"knowledge of {trigger}"]) else "PREFERRED"
                rules.append({
                    "type": "skill",
                    "field": "skill",
                    "operator": "REQUIRED" if importance == "REQUIRED" else "PREFERRED",
                    "value": skill_name,
                    "importance": importance,
                    "description": f"Proficiency in {skill_name}"
                })

        # Fallback if no specific triggers matched
        if not rules:
            rules.append({
                "type": "general",
                "field": "portfolio",
                "operator": "REQUIRED",
                "value": "Verified Credentials",
                "importance": "REQUIRED",
                "description": "Evidence of relevant academic and project experience"
            })

        return rules

    async def create_opportunity(
        self,
        db: AsyncSession,
        user: User,
        data: OpportunityCreateRequest
    ) -> Opportunity:
        """Create opportunity, parse structured requirements, and register in knowledge graph."""
        requirements = self.extract_structured_requirements(data.description)

        opp = Opportunity(
            user_id=user.id,
            title=data.title,
            organization=data.organization,
            description=data.description,
            opportunity_type=data.opportunity_type,
            status="ANALYZED",
            extracted_requirements={"requirements": requirements, "count": len(requirements)}
        )
        db.add(opp)
        await db.flush()

        # Sync to Knowledge Graph
        await self.graph_service.sync_opportunity(opp, requirements)

        await db.commit()
        await db.refresh(opp)
        return opp

    async def list_opportunities(self, db: AsyncSession, user_id: str) -> List[Opportunity]:
        """List opportunities for user."""
        query = select(Opportunity).where(Opportunity.user_id == user_id).order_by(Opportunity.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_opportunity(self, db: AsyncSession, user_id: str, opp_id: str) -> Opportunity:
        """Get specific opportunity."""
        query = select(Opportunity).where(Opportunity.id == opp_id, Opportunity.user_id == user_id)
        result = await db.execute(query)
        opp = result.scalar_one_or_none()
        if not opp:
            raise NotFoundError("Opportunity", opp_id)
        return opp
