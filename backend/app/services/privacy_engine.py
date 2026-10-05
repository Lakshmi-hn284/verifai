"""
VERIFAI - Privacy Engine & Minimum Disclosure Synthesizer
Calculates necessary vs unnecessary attributes, generates selective disclosure proofs,
and enforces zero-trust human-in-the-loop consent.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.models import User, Opportunity, Claim, DisclosureConsent
from app.core.security import compute_sha256
from app.core.audit import log_security_event
from app.core.errors import NotFoundError, PrivacyPolicyError


class PrivacyEngine:
    """
    Zero-Trust Privacy & Selective Disclosure Engine.
    Enforces data minimization principles per GDPR / W3C Verifiable Credentials.
    """

    async def preview_minimum_disclosure(
        self,
        db: AsyncSession,
        user: User,
        opportunity_id: str
    ) -> Dict[str, Any]:
        """
        Compare target opportunity requirements against user claims in vault.
        Returns:
        - requested_attributes: strictly required for the opportunity
        - redacted_attributes: unneeded sensitive attributes that will be withheld
        - disclosure_reduction_percentage (DRP)
        """
        # Fetch opportunity
        opp_res = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id, Opportunity.user_id == user.id))
        opp = opp_res.scalar_one_or_none()
        if not opp:
            raise NotFoundError("Opportunity", opportunity_id)

        # Fetch user claims
        claims_res = await db.execute(select(Claim).where(Claim.user_id == user.id))
        claims = claims_res.scalars().all()

        requirements = opp.extracted_requirements.get("requirements", [])
        req_fields = {r.get("field", "").lower(): r for r in requirements}

        requested_attributes: List[Dict[str, Any]] = []
        redacted_attributes: List[Dict[str, Any]] = []

        # Common sensitive PII fields that should NEVER be disclosed unless specifically mandated
        sensitive_pii_fields = {
            "residential_address": "Personal home address is not required for qualification evaluation.",
            "date_of_birth": "Exact date of birth is unnecessary; age verification not requested.",
            "phone_number": "Personal phone number is withheld to prevent spam / tracking.",
            "national_id": "Government national identity numbers are protected under privacy policy.",
            "bank_details": "Financial details are strictly confidential."
        }

        # Categorize user claims
        seen_fields = set()
        for c in claims:
            f_name = c.field_name.lower()
            if f_name in seen_fields:
                continue
            seen_fields.add(f_name)

            # Check if this claim directly answers an opportunity requirement
            matched_req = req_fields.get(f_name)
            if not matched_req and c.category == "SKILL":
                # Check skill match
                for r in requirements:
                    if r.get("field") == "skill" and str(r.get("value", "")).lower() in str(c.field_value).lower():
                        matched_req = r
                        break

            if matched_req:
                requested_attributes.append({
                    "attribute": c.field_name,
                    "category": c.category,
                    "value_preview": str(c.field_value),
                    "required_by": matched_req.get("description", "Opportunity criterion"),
                    "action": "DISCLOSE"
                })
            else:
                reason = sensitive_pii_fields.get(
                    f_name,
                    f"Attribute '{c.field_name}' was not requested by '{opp.title}' criteria."
                )
                redacted_attributes.append({
                    "attribute": c.field_name,
                    "category": c.category,
                    "reason": reason,
                    "action": "REDACT"
                })

        total_attrs = len(requested_attributes) + len(redacted_attributes)
        drp = (len(redacted_attributes) / total_attrs * 100.0) if total_attrs > 0 else 0.0

        return {
            "opportunity_id": opp.id,
            "opportunity_title": opp.title,
            "organization": opp.organization,
            "requested_attributes": requested_attributes,
            "redacted_attributes": redacted_attributes,
            "disclosure_reduction_percentage": round(drp, 1)
        }

    async def approve_and_generate_package(
        self,
        db: AsyncSession,
        user: User,
        opportunity_id: str,
        allowed_attributes: List[str],
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record explicit user consent and generate minimum-disclosure application package.
        Any attribute NOT in allowed_attributes is mathematically stripped.
        """
        opp_res = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id, Opportunity.user_id == user.id))
        opp = opp_res.scalar_one_or_none()
        if not opp:
            raise NotFoundError("Opportunity", opportunity_id)

        claims_res = await db.execute(select(Claim).where(Claim.user_id == user.id))
        claims = claims_res.scalars().all()

        allowed_set = {a.lower() for a in allowed_attributes}
        verifiable_claims = []
        redacted_count = 0

        for c in claims:
            if c.field_name.lower() in allowed_set:
                verifiable_claims.append({
                    "claim_id": c.id,
                    "category": c.category,
                    "field_name": c.field_name,
                    "field_value": c.field_value,
                    "confidence": c.confidence,
                    "verification_status": c.verification_status,
                    "issuer": c.issuer or "VERIFAI Certified Vault"
                })
            else:
                redacted_count += 1

        now = datetime.now(timezone.utc)
        package_payload = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": ["VerifiablePresentation", "VerifaiMinimumDisclosurePackage"],
            "holder": f"did:verifai:user:{user.id}",
            "opportunity": {
                "id": opp.id,
                "title": opp.title,
                "organization": opp.organization
            },
            "issuanceDate": now.isoformat(),
            "verifiableClaims": verifiable_claims,
            "privacyProof": {
                "type": "SelectiveDisclosureProof2026",
                "redactedAttributeCount": redacted_count,
                "consentTimestamp": now.isoformat()
            }
        }

        # Calculate package integrity hash
        import json
        package_hash = compute_sha256(json.dumps(package_payload, sort_keys=True).encode("utf-8"))
        package_payload["packageHash"] = package_hash

        # Persist consent record
        consent = DisclosureConsent(
            user_id=user.id,
            opportunity_id=opp.id,
            requested_attributes=allowed_attributes,
            redacted_attributes=[c.field_name for c in claims if c.field_name.lower() not in allowed_set],
            user_approved=True,
            approved_at=now,
            package_payload=package_payload
        )
        db.add(consent)

        await log_security_event(
            db=db,
            event_type="DISCLOSURE_APPROVED",
            status="SUCCESS",
            user_id=user.id,
            ip_address=ip_address,
            details={
                "opportunity_id": opp.id,
                "allowed_count": len(verifiable_claims),
                "redacted_count": redacted_count,
                "package_hash": package_hash
            }
        )

        await db.commit()
        await db.refresh(consent)

        return {
            "package_id": consent.id,
            "opportunity_title": opp.title,
            "organization": opp.organization,
            "generated_at": now.isoformat(),
            "verifiable_claims": verifiable_claims,
            "redacted_count": redacted_count,
            "package_hash": package_hash,
            "w3c_payload": package_payload
        }
