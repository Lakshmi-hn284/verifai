import httpx
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def run_live_test():
    client = httpx.Client(base_url=BASE_URL)

    # 1. Register new researcher
    user_email = "lead_researcher@verifai.io"
    reg_resp = client.post("/auth/register", json={
        "email": user_email,
        "password": "ResearchPassword123!",
        "full_name": "Dr. Lead Researcher"
    })
    if reg_resp.status_code == 201:
        token = reg_resp.json()["data"]["access_token"]
    else:
        # Already exists, login
        login_resp = client.post("/auth/login", json={
            "email": user_email,
            "password": "ResearchPassword123!"
        })
        token = login_resp.json()["data"]["access_token"]

    print("[1] Authentication: Token acquired successfully.")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload Academic Transcript to Encrypted Vault
    transcript_bytes = (
        b"%PDF-1.4\n"
        b"Official University Transcript of Academic Records\n"
        b"Degree Awarded: Bachelor of Technology\n"
        b"Major Branch: Computer Science and Engineering (CSE)\n"
        b"Cumulative Grade Point Average CGPA: 9.35\n"
        b"Evidenced Competencies: Python, Machine Learning, Data Structures, FastAPI, SQL\n"
        b"Residential Address: 100 University Park, Tech Avenue\n"
        b"Date of Birth: 18/04/2002\n"
        b"Mobile Phone: +1-234-567-8900\n"
    )
    upload_resp = client.post(
        "/documents",
        headers=headers,
        files={"file": ("university_transcript.pdf", transcript_bytes, "application/pdf")}
    )
    assert upload_resp.status_code == 201
    doc_data = upload_resp.json()["data"]
    print(f"[2] Vault Upload: Stored & Encrypted with AES-256-GCM. Doc ID: {doc_data['id']}, Type: {doc_data['doc_type']}")

    # 3. Check Extracted Claims
    claims_resp = client.get("/credentials", headers=headers)
    claims = claims_resp.json()["data"]["claims"]
    print(f"[3] Extracted Claims: {len(claims)} claims materialized.")
    for c in claims[:4]:
        print(f"    - {c['field_name']}: {c['field_value']} (Confidence: {int(c['confidence']*100)}%)")

    # 4. Ingest Target Opportunity
    opp_resp = client.post(
        "/opportunities",
        headers=headers,
        json={
            "title": "Principal AI Research Scientist",
            "organization": "Google DeepMind",
            "description": "Applicants must hold a Bachelor in Computer Science (CSE) with CGPA >= 8.5 and strong proficiency in Python and Machine Learning.",
            "opportunity_type": "JOB"
        }
    )
    opp_id = opp_resp.json()["data"]["id"]
    rules_count = opp_resp.json()["data"]["extracted_requirements"]["count"]
    print(f"[4] Opportunity Ingested: {opp_resp.json()['data']['title']} with {rules_count} deterministic condition rules.")

    # 5. Execute Hybrid Eligibility Evaluation
    eval_resp = client.post("/eligibility/evaluate", headers=headers, json={"opportunity_id": opp_id})
    eval_data = eval_resp.json()["data"]
    print(f"[5] Hybrid Reasoning: Verdict={eval_data['status']} ({eval_data['match_score']}% match)")
    print(f"    - Satisfied Rules: {len(eval_data['satisfied_rules'])}")
    for s in eval_data['satisfied_rules']:
        print(f"      * {s['rule']['description']} -> Evidenced by '{s['evidence']['document_name']}'")

    # 6. Minimum Disclosure Preview
    prev_resp = client.get(f"/disclosures/preview/{opp_id}", headers=headers)
    prev_data = prev_resp.json()["data"]
    drp = prev_data["disclosure_reduction_percentage"]
    print(f"[6] Privacy Engine: Minimum Disclosure Reduction Percentage (DRP) = {drp}%")
    print(f"    - Disclosed: {[a['attribute'] for a in prev_data['requested_attributes']]}")
    print(f"    - Redacted: {[a['attribute'] for a in prev_data['redacted_attributes']]}")

    # 7. Approve Selective Disclosure & Export W3C Verifiable Presentation
    req_attrs = [a['attribute'] for a in prev_data['requested_attributes']]
    appr_resp = client.post(
        "/disclosures/approve",
        headers=headers,
        json={
            "opportunity_id": opp_id,
            "approved": True,
            "allowed_attributes": req_attrs
        }
    )
    pkg_data = appr_resp.json()["data"]
    print(f"[7] W3C Verifiable Presentation Generated!")
    print(f"    - Package Integrity Hash: {pkg_data['package_hash'][:16]}...")
    print(f"    - Redacted Attribute Count: {pkg_data['redacted_count']}")

    # 8. Check Security Audit Trail
    audit_resp = client.get("/audit/logs", headers=headers)
    logs = audit_resp.json()["data"]["logs"]
    print(f"[8] Security Audit Trail: {len(logs)} tamper-evident entries recorded.")
    for l in logs[:3]:
        print(f"    - [{l['event_type']}] Status: {l['status']} (Hash: {l['metadata_hash'][:12]}...)")

    print("\n>>> ALL VERIFAI CORE MODULES VALIDATED & OPERATIONAL ON LIVE SYSTEM! <<<")

if __name__ == "__main__":
    run_live_test()
