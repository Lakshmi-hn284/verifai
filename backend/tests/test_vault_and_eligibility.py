"""
VERIFAI - Integration Tests for Vault, Claims, Eligibility, and Selective Disclosure
"""
import pytest
import io
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_end_to_end_credential_and_eligibility_flow(client: AsyncClient):
    # 1. Register & Login
    reg_res = await client.post("/api/v1/auth/register", json={
        "email": "candidate@verifai.io",
        "password": "Password123!",
        "full_name": "Test Candidate"
    })
    token = reg_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload Document into Vault (Synthetic academic transcript)
    transcript_content = (
        b"%PDF-1.4\n"
        b"University Semester Grade Sheet - Official Academic Transcript\n"
        b"Degree: Bachelor of Technology\n"
        b"Branch: Computer Science and Engineering (CSE)\n"
        b"Cumulative Grade Point Average CGPA: 8.75\n"
        b"Core Skills Demonstrated: Python, Machine Learning, Data Structures\n"
        b"Residential Address: 42 Innovation Road, Tech Park, District 7\n"
        b"Date of Birth: 15/08/2003\n"
        b"Phone: +1-555-0199\n"
    )
    files = {
        "file": ("academic_transcript.pdf", io.BytesIO(transcript_content), "application/pdf")
    }
    upload_res = await client.post("/api/v1/documents", files=files, headers=headers)
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["data"]["id"]
    assert doc_id is not None
    assert upload_res.json()["data"]["doc_type"] == "TRANSCRIPT"

    # 3. Verify Extracted Claims
    claims_res = await client.get("/api/v1/credentials", headers=headers)
    assert claims_res.status_code == 200
    claims = claims_res.json()["data"]["claims"]
    assert len(claims) >= 3

    field_names = [c["field_name"] for c in claims]
    assert "cgpa" in field_names
    assert "degree_major" in field_names
    assert "skill" in field_names

    # Verify confidence and bounding box grounding
    cgpa_claim = next(c for c in claims if c["field_name"] == "cgpa")
    assert cgpa_claim["field_value"] == 8.75
    assert cgpa_claim["confidence"] >= 0.95
    assert cgpa_claim["bounding_box"] is not None

    # 4. Ingest Opportunity
    opp_payload = {
        "title": "Machine Learning Research Intern",
        "organization": "DeepAI Labs",
        "description": "Applicants must be CSE students with CGPA above 7.5 and knowledge of Python.",
        "opportunity_type": "INTERNSHIP"
    }
    opp_res = await client.post("/api/v1/opportunities", json=opp_payload, headers=headers)
    assert opp_res.status_code == 201
    opp_id = opp_res.json()["data"]["id"]
    extracted_reqs = opp_res.json()["data"]["extracted_requirements"]["requirements"]
    assert len(extracted_reqs) >= 3

    # 5. Hybrid Eligibility Evaluation
    eval_res = await client.post("/api/v1/eligibility/evaluate", json={"opportunity_id": opp_id}, headers=headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()["data"]
    assert eval_data["status"] == "ELIGIBLE"
    assert eval_data["match_score"] >= 80.0
    assert len(eval_data["satisfied_rules"]) >= 3
    assert len(eval_data["evidence_map"]) >= 2
    assert "### Eligibility Analysis" in eval_data["explanation_markdown"]

    # 6. Minimum Disclosure Preview
    preview_res = await client.get(f"/api/v1/disclosures/preview/{opp_id}", headers=headers)
    assert preview_res.status_code == 200
    preview_data = preview_res.json()["data"]
    assert preview_data["disclosure_reduction_percentage"] > 0
    # Confirm sensitive PII like address and DOB are marked for redaction
    redacted_names = [r["attribute"] for r in preview_data["redacted_attributes"]]
    assert any("address" in name.lower() or "birth" in name.lower() or "phone" in name.lower() for name in redacted_names)

    # 7. Approve Selective Disclosure & Export Verifiable Presentation
    req_attrs = [r["attribute"] for r in preview_data["requested_attributes"]]
    approve_res = await client.post("/api/v1/disclosures/approve", json={
        "opportunity_id": opp_id,
        "approved": True,
        "allowed_attributes": req_attrs
    }, headers=headers)
    assert approve_res.status_code == 201
    pkg = approve_res.json()["data"]
    assert pkg["package_hash"] is not None
    assert pkg["redacted_count"] > 0
    assert len(pkg["verifiable_claims"]) >= len(req_attrs)
    claimed_fields = {c["field_name"] for c in pkg["verifiable_claims"]}
    assert set(req_attrs).issubset(claimed_fields)

    # 8. Check Career Gap Analysis
    career_res = await client.get("/api/v1/career/gaps", headers=headers)
    assert career_res.status_code == 200
    assert "market_readiness_score" in career_res.json()["data"]
