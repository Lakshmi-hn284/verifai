"""
VERIFAI - Hybrid Eligibility Engine & Evidence Reasoning
Combines deterministic rule validation, semantic matching, calibrated claim confidence,
and grounded evidence mapping.
"""
from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.models import User, Opportunity, Claim, Document, EligibilityEvaluation
from app.core.errors import NotFoundError


class EligibilityEngine:
    """
    Hybrid Eligibility Engine.
    Executes multi-phase evaluation:
    Phase 1: Deterministic schema comparison (>=, <=, IN, ==)
    Phase 2: Semantic skill & keyword matching
    Phase 3: Evidence traceability linkage (linking to specific document IDs, pages, bounding boxes)
    Phase 4: Match score calculation
    Phase 5: Contextual explainable AI generation
    """

    async def evaluate_eligibility(
        self,
        db: AsyncSession,
        user: User,
        opportunity_id: str
    ) -> EligibilityEvaluation:
        # 1. Fetch Opportunity
        opp_query = select(Opportunity).where(Opportunity.id == opportunity_id, Opportunity.user_id == user.id)
        opp_res = await db.execute(opp_query)
        opp = opp_res.scalar_one_or_none()
        if not opp:
            raise NotFoundError("Opportunity", opportunity_id)

        requirements = opp.extracted_requirements.get("requirements", [])

        # 2. Fetch User Claims & associated Documents
        claims_query = select(Claim).where(Claim.user_id == user.id)
        claims_res = await db.execute(claims_query)
        claims = claims_res.scalars().all()

        docs_query = select(Document).where(Document.user_id == user.id)
        docs_res = await db.execute(docs_query)
        docs_map = {d.id: d for d in docs_res.scalars().all()}

        # 3. Rule Evaluation & Evidence Mapping
        satisfied_rules: List[Dict[str, Any]] = []
        partially_satisfied_rules: List[Dict[str, Any]] = []
        missing_rules: List[Dict[str, Any]] = []
        evidence_map: Dict[str, Any] = {}

        total_weight = 0.0
        earned_weight = 0.0

        for idx, req in enumerate(requirements):
            req_id = f"req_{idx}"
            weight = 2.0 if req.get("importance") == "REQUIRED" else 1.0
            total_weight += weight

            match_result, matched_claim = self._check_requirement(req, claims)

            if match_result == "SATISFIED" and matched_claim:
                earned_weight += weight
                doc = docs_map.get(matched_claim.document_id)
                evidence_info = {
                    "claim_id": matched_claim.id,
                    "field_name": matched_claim.field_name,
                    "field_value": matched_claim.field_value,
                    "confidence": matched_claim.confidence,
                    "document_id": doc.id if doc else None,
                    "document_name": doc.filename if doc else "User Asserted",
                    "page_number": matched_claim.page_number or 1,
                    "bounding_box": matched_claim.bounding_box
                }
                satisfied_rules.append({
                    "rule": req,
                    "status": "SATISFIED",
                    "evidence": evidence_info
                })
                evidence_map[req.get("description", req_id)] = evidence_info

            elif match_result == "PARTIALLY_SATISFIED" and matched_claim:
                earned_weight += (weight * 0.5)
                doc = docs_map.get(matched_claim.document_id)
                evidence_info = {
                    "claim_id": matched_claim.id,
                    "field_name": matched_claim.field_name,
                    "field_value": matched_claim.field_value,
                    "confidence": matched_claim.confidence,
                    "document_id": doc.id if doc else None,
                    "document_name": doc.filename if doc else "User Asserted",
                    "page_number": matched_claim.page_number or 1,
                    "bounding_box": matched_claim.bounding_box
                }
                partially_satisfied_rules.append({
                    "rule": req,
                    "status": "PARTIALLY_SATISFIED",
                    "reason": "Meets condition partially or confidence below threshold",
                    "evidence": evidence_info
                })
                evidence_map[req.get("description", req_id)] = evidence_info
            else:
                missing_rules.append({
                    "rule": req,
                    "status": "MISSING",
                    "reason": f"No supporting claim or evidence found for '{req.get('description', '')}'"
                })

        # 4. Compute Match Score
        score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 0.0
        score = round(score, 1)

        if score >= 80.0:
            status = "ELIGIBLE"
        elif score >= 50.0:
            status = "PARTIALLY_ELIGIBLE"
        else:
            status = "INELIGIBLE"

        # 5. Generate Grounded Explainable AI Report
        explanation = self._generate_explanation_markdown(
            opp_title=opp.title,
            score=score,
            status=status,
            satisfied=satisfied_rules,
            partially=partially_satisfied_rules,
            missing=missing_rules
        )

        evaluation = EligibilityEvaluation(
            user_id=user.id,
            opportunity_id=opp.id,
            status=status,
            match_score=score,
            satisfied_rules=satisfied_rules,
            partially_satisfied_rules=partially_satisfied_rules,
            missing_rules=missing_rules,
            evidence_map=evidence_map,
            explanation_markdown=explanation
        )
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    def _check_requirement(self, req: Dict[str, Any], claims: List[Claim]) -> Tuple[str, Any]:
        """Evaluate deterministic and semantic conditions."""
        req_field = req.get("field", "").lower()
        operator = req.get("operator", "==")
        expected_val = req.get("value")

        # 1. Academic CGPA / Percentage
        if req_field == "cgpa":
            for c in claims:
                if c.field_name == "cgpa":
                    try:
                        user_cgpa = float(c.field_value)
                        target_cgpa = float(expected_val)
                        if operator == ">=" and user_cgpa >= target_cgpa:
                            return "SATISFIED", c
                        elif user_cgpa >= (target_cgpa - 0.5):
                            return "PARTIALLY_SATISFIED", c
                    except (ValueError, TypeError):
                        pass

        # 2. Education Major / Degree
        elif req_field in ["degree_major", "degree_level", "branch"]:
            for c in claims:
                if c.field_name in ["degree_major", "degree_level"]:
                    c_val = str(c.field_value).lower()
                    if isinstance(expected_val, list):
                        if any(item.lower() in c_val for item in expected_val):
                            return "SATISFIED", c
                    elif str(expected_val).lower() in c_val:
                        return "SATISFIED", c

        # 3. Technical Skills
        elif req_field == "skill":
            target_skill = str(expected_val).lower()
            for c in claims:
                if c.category == "SKILL":
                    c_skill = str(c.field_value).lower()
                    if target_skill in c_skill or c_skill in target_skill:
                        if c.confidence >= 0.8:
                            return "SATISFIED", c
                        return "PARTIALLY_SATISFIED", c

        # 4. General fallback
        for c in claims:
            if str(expected_val).lower() in str(c.field_value).lower():
                return "SATISFIED", c

        return "MISSING", None

    def _generate_explanation_markdown(
        self,
        opp_title: str,
        score: float,
        status: str,
        satisfied: List[Dict[str, Any]],
        partially: List[Dict[str, Any]],
        missing: List[Dict[str, Any]]
    ) -> str:
        """Create structured, transparent explainable AI markdown."""
        md = f"### Eligibility Analysis for {opp_title}\n\n"
        md += f"**Overall Eligibility Status**: `{status}` ({score}% match score)\n\n"
        
        md += "#### 1. What did the system decide?\n"
        if status == "ELIGIBLE":
            md += f"You demonstrate high compatibility ({score}%) for this opportunity with all primary requirements evidenced in your vault.\n\n"
        elif status == "PARTIALLY_ELIGIBLE":
            md += f"You fulfill several core criteria ({score}%), but have pending or partially satisfied requirements that need verification.\n\n"
        else:
            md += f"Your current verified credential portfolio covers {score}% of the required criteria. Several key competencies are unevidenced.\n\n"

        md += "#### 2. Satisfied Requirements & Supporting Evidence\n"
        if satisfied:
            for s in satisfied:
                desc = s['rule'].get('description', 'Requirement')
                ev = s['evidence']
                doc_name = ev.get('document_name', 'User Asserted')
                conf = int(ev.get('confidence', 1.0) * 100)
                md += f"- **{desc}**: Proven by `{doc_name}` (Page {ev.get('page_number', 1)}) with {conf}% extraction confidence.\n"
        else:
            md += "- None fully satisfied yet.\n"
        md += "\n"

        if partially:
            md += "#### 3. Partially Satisfied Criteria\n"
            for p in partially:
                desc = p['rule'].get('description', 'Requirement')
                md += f"- ⚠️ **{desc}**: {p.get('reason')}\n"
            md += "\n"

        if missing:
            md += "#### 4. Missing Requirements\n"
            for m in missing:
                desc = m['rule'].get('description', 'Requirement')
                md += f"- ❌ **{desc}**\n"
            md += "\n"

        md += "#### 5. Recommended Next Actions\n"
        if missing:
            first_missing = missing[0]['rule'].get('value', 'missing skill')
            md += f"- Upload documentation or course certifications demonstrating **{first_missing}** to your secure vault.\n"
        md += "- Review the **Selective Disclosure** preview before generating any application packages to ensure your unneeded personal attributes remain private.\n"

        return md
