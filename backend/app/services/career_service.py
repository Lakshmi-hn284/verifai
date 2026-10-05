"""
VERIFAI - Career Gap Analysis Service
Aggregates criteria across multiple target opportunities and computes recurring
missing competencies to guide proactive professional credential acquisition.
"""
from typing import Dict, Any, List
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.models import User, Opportunity, Claim


class CareerGapService:
    async def analyze_skill_gaps(self, db: AsyncSession, user: User) -> Dict[str, Any]:
        """
        Analyze recurring skill demands vs existing user portfolio.
        Returns top missing competencies with frequency ratios.
        """
        # 1. Fetch user skills
        claims_res = await db.execute(
            select(Claim).where(Claim.user_id == user.id, Claim.category == "SKILL")
        )
        user_skills = {str(c.field_value).lower() for c in claims_res.scalars().all()}

        # 2. Fetch all analyzed opportunities
        opps_res = await db.execute(
            select(Opportunity).where(Opportunity.user_id == user.id)
        )
        opportunities = opps_res.scalars().all()
        total_opps = len(opportunities)

        if total_opps == 0:
            return {
                "total_opportunities_analyzed": 0,
                "top_skill_gaps": [],
                "user_skill_count": len(user_skills),
                "market_readiness_score": 0.0
            }

        # 3. Track skill demand frequencies
        demanded_skills = Counter()
        missing_skills = Counter()

        for opp in opportunities:
            reqs = opp.extracted_requirements.get("requirements", [])
            for r in reqs:
                if r.get("field") == "skill":
                    val = str(r.get("value", "")).strip()
                    val_lower = val.lower()
                    demanded_skills[val] += 1
                    
                    # Check if user has it
                    has_skill = any(val_lower in s or s in val_lower for s in user_skills)
                    if not has_skill:
                        missing_skills[val] += 1

        # Format top skill gaps
        gap_items = []
        for skill_name, miss_count in missing_skills.most_common(10):
            demand_count = demanded_skills.get(skill_name, miss_count)
            gap_items.append({
                "skill": skill_name,
                "missing_in_opportunities": miss_count,
                "total_demanding_opportunities": demand_count,
                "gap_percentage": round((miss_count / total_opps) * 100.0, 1),
                "importance": "HIGH" if miss_count >= 2 else "MEDIUM"
            })

        # Calculate overall market readiness
        total_demands = sum(demanded_skills.values())
        total_missing = sum(missing_skills.values())
        readiness = round(((total_demands - total_missing) / total_demands * 100.0), 1) if total_demands > 0 else 100.0

        return {
            "total_opportunities_analyzed": total_opps,
            "user_skill_count": len(user_skills),
            "market_readiness_score": max(0.0, readiness),
            "top_skill_gaps": gap_items
        }
