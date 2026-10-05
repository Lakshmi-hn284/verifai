# VERIFAI — API Specification & Endpoint Design

## 1. Overview
All REST API endpoints follow standard OpenAPI / JSON conventions with unified request/response schemas, error structures, and authorization headers (`Authorization: Bearer <token>`).

---

## 2. API Endpoint Matrix

### 2.1 Authentication & User Identity (`/api/v1/auth`, `/api/v1/users`)
- `POST /api/v1/auth/register` — Register a new account.
- `POST /api/v1/auth/login` — Authenticate user and return JWT access/refresh tokens.
- `POST /api/v1/auth/logout` — Revoke active session tokens.
- `GET /api/v1/users/me` — Retrieve current user profile and account preferences.
- `PUT /api/v1/users/me` — Update user profile settings.

### 2.2 Secure Document Vault (`/api/v1/documents`)
- `POST /api/v1/documents` — Upload raw document file (PDF/Image) with metadata validation.
- `GET /api/v1/documents` — List user's encrypted vault documents with status.
- `GET /api/v1/documents/{id}` — Retrieve metadata for a specific document.
- `DELETE /api/v1/documents/{id}` — Secure deletion of document and related claims.
- `POST /api/v1/documents/{id}/process` — Trigger multimodal processing & extraction.
- `GET /api/v1/documents/{id}/claims` — Retrieve structured claims extracted from document.

### 2.3 Credential Profile & Knowledge Graph (`/api/v1/credentials`, `/api/v1/graph`)
- `GET /api/v1/credentials` — Retrieve user's consolidated structured claims.
- `GET /api/v1/credentials/{id}` — Retrieve specific credential claim details.
- `POST /api/v1/credentials` — Manually add/verify a credential claim.
- `GET /api/v1/graph/nodes` — Fetch entity nodes (User, Skill, Education, Evidence) for UI visualization.
- `GET /api/v1/graph/edges` — Fetch entity relationship edges.

### 2.4 Opportunity Ingestion & Requirement Extraction (`/api/v1/opportunities`)
- `POST /api/v1/opportunities` — Submit new opportunity raw text or document.
- `GET /api/v1/opportunities` — List user's analyzed opportunities.
- `GET /api/v1/opportunities/{id}` — Get specific opportunity details & extracted requirement rules.
- `POST /api/v1/opportunities/{id}/analyse` — Trigger requirement extraction engine.

### 2.5 Hybrid Eligibility Engine & Evidence Explorer (`/api/v1/eligibility`)
- `POST /api/v1/eligibility/evaluate` — Evaluate user credentials against an opportunity.
- `GET /api/v1/eligibility/{id}` — Retrieve detailed eligibility report (Satisfied, Missing, Score).
- `GET /api/v1/eligibility/{id}/evidence` — Retrieve interactive evidence mapping graph.

### 2.6 Privacy Engine & Selective Disclosure (`/api/v1/disclosures`)
- `POST /api/v1/disclosures/preview` — Generate minimum disclosure policy comparison.
- `POST /api/v1/disclosures/{id}/approve` — Record explicit user approval for a disclosure schema.
- `GET /api/v1/disclosures/{id}` — View active disclosure consent record.

### 2.7 Application Package Generator (`/api/v1/applications`)
- `POST /api/v1/applications/package` — Export approved minimum-disclosure application package.
- `GET /api/v1/applications` — List generated application packages.

### 2.8 Career Gap Analytics & Audit Trail (`/api/v1/career`, `/api/v1/audit`)
- `GET /api/v1/career/gaps` — Aggregated top missing skills & recommended development path.
- `GET /api/v1/audit/logs` — Fetch user's tamper-evident security audit logs.

---

## 3. Standard Response Format

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "timestamp": "2026-10-05T20:15:00Z",
    "request_id": "req_8f93a12b"
  }
}
```
