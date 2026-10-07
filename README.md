# VERIFAI — Privacy-Preserving AI Credential & Eligibility Intelligence Platform

[![Build & Test Status](https://img.shields.io/badge/backend%20tests-8%2F8%20passed-brightgreen.svg)](backend/tests/)
[![Next.js](https://img.shields.io/badge/frontend-Next.js%2016%20%7C%20React%2019-black.svg)](frontend/)
[![Security: AES-256-GCM](https://img.shields.io/badge/vault%20cipher-AES--256--GCM-blue.svg)](backend/app/core/crypto.py)
[![Auth: Argon2id](https://img.shields.io/badge/auth-Argon2id%20%7C%20JWT-indigo.svg)](backend/app/core/security.py)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Implementation Status](https://img.shields.io/badge/audit-verified%20honest-orange.svg)](docs/IMPLEMENTATION_STATUS.md)

> **"Prove what matters. Share only what is needed."**

VERIFAI is a research-grade, privacy-first intelligence platform designed to evaluate candidate eligibility for academic programs, scholarships, and employment opportunities **without over-disclosing sensitive personal data**. 

Candidates upload identity and credential documents into an **authenticated, encrypted zero-trust vault**. The platform extracts structured claims, maps relationships across an **evidence knowledge graph**, deterministically verifies qualifications against multi-variable opportunity criteria, and uses **selective disclosure policies** to generate minimal-footprint verifiable presentations with explicit human-in-the-loop consent.

---

## 🔍 Technical Honesty & Implementation Status

In accordance with open-source software integrity and research ethics, VERIFAI maintains a strict separation between **real production code**, **deterministic heuristic prototypes**, **simulated mocks**, and **roadmap objectives**.

👉 **Read the complete [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) report for line-by-line verification.**

| Subsystem | Implementation Classification | Verified Reality |
| :--- | :--- | :--- |
| **Document Vault Encryption** | 🟢 **Real & Active** | **AES-256-GCM** authenticated encryption with 96-bit nonces, 128-bit tags, and per-user **HKDF-SHA256** key derivation. |
| **Authentication & Sessions** | 🟢 **Real & Active** | **Argon2id** password hashing (`argon2-cffi`), cryptographically signed JWT tokens (`HS256`), and role isolation. |
| **Eligibility Rule Engine** | 🟢 **Real & Active** | Deterministic quantitative and categorical evaluation (`>=`, `<=`, `==`, `IN`, `CONTAINS`, `REQUIRED`) with granular evidence mapping. |
| **Knowledge Graph** | 🟢 **Real & Active** | In-memory directed graph modeling `User`, `Document`, `Claim`, and `Skill` nodes with JSON persistence via **NetworkX** (Neo4j driver scaffolded). |
| **Career Continuity Analysis** | 🟢 **Real & Active** | Temporal chronological milestone ordering detecting gaps > 6 months with heuristic skill recommendations. |
| **Selective Disclosure Policy** | 🟢 **Real & Active** | Human-in-the-loop minimization interface comparing requested criteria against candidate claims to redact unneeded PII. |
| **Document Understanding** | 🟡 **Deterministic Heuristic** | Regex-driven layout & text parsing simulating bounding-box coordinates for zero-cost offline reproduction (**not deep vision ML/OCR**). |
| **Verifiable Credentials** | 🟡 **Structured JSON Export** | Generates W3C-aligned Verifiable Presentation JSON payloads (**not BBS+ cryptographic signatures or ZKP circuits**). |
| **LLM & Embeddings** | 🟠 **Mocked / Simulated** | Simulated schema-compliant responses enabling instant, zero-cost offline evaluation without external cloud API dependencies. |

---

## 🏗 System Architecture

VERIFAI enforces a Clean Architecture with clear provider abstractions, decoupling business domain logic from third-party frameworks and external storage drivers:

```
+───────────────────────────────────────────────────────────────────────────────────────+
|                                  PRESENTATION LAYER                                   |
|                    Next.js 16 (Turbopack) / React 19 / Tailwind CSS                   |
|  - Dashboard Summary        - Encrypted Document Vault     - Credentials Visualizer   |
|  - Opportunity Evaluator    - Knowledge Graph Explorer     - Selective Disclosure UI  |
+───────────────────────────────────────────┬───────────────────────────────────────────+
                                            │ HTTPS / Bearer JWT
+───────────────────────────────────────────v───────────────────────────────────────────+
|                                 APPLICATION GATEWAY                                   |
|                        FastAPI / Pydantic v2 / Python 3.14+                           |
|  - Argon2id Auth Middleware - Request Validation Schemas   - Structured Audit Logger  |
+───────────────────────────────────────────┬───────────────────────────────────────────+
                                            │
              +─────────────────────────────┼─────────────────────────────+
              │                             │                             │
+-------------v-------------+ +-------------v-------------+ +-------------v-------------+
|    CORE DOMAIN SERVICES   | |     INTELLIGENCE ENGINES  | |    PRIVACY & PACKAGING    |
| - VaultService (AES-GCM)  | | - EligibilityEngine       | | - DisclosurePolicyEngine  |
| - DocumentManager         | | - DeterministicRuleEngine | | - HumanConsentGateway     |
| - ClaimService            | | - CareerGapAnalyzer       | | - W3C Verifiable          |
| - OpportunityService      | | - KnowledgeGraphService   | |   Presentation Builder    |
+-------------┬-------------+ +-------------┬-------------+ +-------------┬-------------+
              │                             │                             │
+-------------v─────────────────────────────v─────────────────────────────v-------------+
|                                PROVIDER ABSTRACTION LAYER                             |
|  [StorageProvider]        [DocumentProvider]          [GraphProvider]   [LLMProvider] |
+-------------┬─────────────────────┬─────────────────────┬───────────────┬-------------+
              │                     │                     │               │
              v                     v                     v               v
+───────────────────────+ +───────────────────+ +───────────────────+ +─────────────────+
|   DUAL-MODE STORAGE   | |   INGESTION / OCR | |   GRAPH ENGINE    | |   AI INFERENCE  |
| - PostgreSQL / SQLite | | - Heuristic       | | - NetworkX        | | - Offline Mock/ |
| - AES-256-GCM Vault   | |   Document Parser | |   In-Memory Engine| |   Template LLM  |
|   Directory on Disk   | | - Layout Geomet.  | | - Neo4j Driver    | | - Cloud LLM     |
|                       | |   Bounding Boxes  | |   (Scaffolded)    | |   (Abstracted)  |
+───────────────────────+ +───────────────────+ +───────────────────+ +─────────────────+
```

For detailed component interaction, trust boundaries, and sequence diagrams, see [docs/architecture.md](docs/architecture.md).

---

## 🔒 Cryptographic & Privacy Guarantees

1. **Authenticated Encryption at Rest (AES-256-GCM)**:
   Every uploaded document is encrypted with a unique 96-bit nonce and verified with a 128-bit authentication tag. Ciphertext tampering causes immediate decryption rejection.
2. **HKDF-SHA256 Per-User Key Derivation**:
   Encryption keys are derived at runtime:
   $$\text{UserVaultKey} = \text{HKDF-SHA256}(\text{IKM}=\text{MasterKey}, \text{salt}=\text{UserUUID}, \text{info}=\text{"verifai-user-vault"})$$
   Database dumps without the runtime environment master key cannot decrypt user documents.
3. **Argon2id Password Security**:
   User passwords are protected using the memory-hard Argon2id primitive via `argon2-cffi`.
4. **Data Minimization Gateway**:
   Verifiers never receive raw documents. Instead, only user-approved, opportunity-relevant claims are included in export packages.

For threat models and STRIDE vulnerability analysis, see [docs/SECURITY.md](docs/SECURITY.md) and [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

---

## 🚀 Quickstart & Setup Guide

VERIFAI is engineered for **instant reproducibility**. You can run the entire platform with zero external paid APIs.

### Prerequisites
- **Python 3.10+** (Tested on Python 3.12 - 3.14)
- **Node.js 18+** (Tested on Node.js v20 - v24)
- *Optional*: Docker & Docker Compose

---

### Option A: Zero-Dependency Local Setup (Fastest)

#### 1. Configure Environment Variables
Copy the documented environment templates:
```bash
# From repository root:
cp .env.example .env
cp backend/.env.example backend/.env
```

#### 2. Start the Backend (FastAPI + Embedded SQLite + NetworkX)
```bash
cd backend
python -m venv venv

# Activate virtual environment:
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt

# Run backend test suite to verify cryptographic & eligibility engines:
pytest -v

# Start FastAPI development server:
uvicorn app.main:app --reload --port 8000
```
Backend API will be available at: `http://localhost:8000`  
Interactive Swagger OpenAPI documentation: `http://localhost:8000/docs`

#### 3. Start the Frontend (Next.js 16 + React 19)
Open a new terminal:
```bash
cd frontend

# Install Node dependencies:
npm install

# Run ESLint validation:
npm run lint

# Start Next.js development server:
npm run dev
```
Open your browser at `http://localhost:3000`.

---

### Option B: Containerized Orchestration (Docker Compose)

Run the full multi-service stack (FastAPI, PostgreSQL with pgvector, Neo4j, and Next.js):
```bash
# Generate high-entropy secrets and start containers:
docker compose up --build
```
- **Web Interface**: `http://localhost:3000`
- **FastAPI API**: `http://localhost:8000`
- **Neo4j Browser**: `http://localhost:7474`

---

## 💻 Interactive Platform Walkthrough

| Module | Core Capability | Screenshot / Workflow |
| :--- | :--- | :--- |
| **1. Executive Dashboard** | Real-time overview of encrypted vault artifacts, verified claims, eligibility matches, and career health score. | Authenticate via Argon2id, view personal credential telemetry. |
| **2. Encrypted Vault** | Upload transcripts, degrees, and certificates. Immediate AES-256-GCM encryption with SHA-256 integrity checksum. | Files are encrypted on disk; preview decryption is authenticated on-demand. |
| **3. Credential Matrix** | Inspect extracted claims (Degree, CGPA, Major, Institution, Graduation Date) with source document provenance. | Evidence-backed assertions linked to underlying encrypted vault blobs. |
| **4. Knowledge Graph** | Interactive visualization of candidate competence networks (`User` -> `Claim` -> `Skill` -> `Requirement`). | Explore entity relationships powered by NetworkX graph algorithms. |
| **5. Eligibility Engine** | Evaluate qualifications against complex opportunities (e.g., DeepMind ML Engineer, Rhodes Scholarship). | Deterministic evaluation of GPA, coursework, and prerequisites with pass/fail reasons. |
| **6. Selective Disclosure** | Compare required vs unrequested attributes; review masked attributes and approve minimum disclosure packages. | Human-in-the-loop approval before export to W3C-aligned JSON. |
| **7. Career Gap Radar** | Identify missing qualifications across target opportunities and receive structured upskilling pathways. | Algorithmic gap analysis across academic and professional timelines. |
| **8. Audit Trail** | Cryptographically identifiable timeline of all system operations (`UPLOAD`, `ENCRYPT`, `EVALUATE`, `DISCLOSE`). | Full transparency and accountability for privacy compliance. |

---

## 📡 API Reference Overview

The FastAPI gateway exposes RESTful endpoints with strict Pydantic schemas:

| HTTP Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user with Argon2id password hashing | No |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access token | No |
| `GET` | `/api/v1/dashboard/summary` | Retrieve aggregated user credential and audit telemetry | Yes |
| `POST` | `/api/v1/vault/upload` | Ingest and encrypt document with AES-256-GCM | Yes |
| `GET` | `/api/v1/vault/documents` | List encrypted documents belonging to authenticated user | Yes |
| `GET` | `/api/v1/credentials` | List verified structured claims | Yes |
| `GET` | `/api/v1/graph` | Fetch serialized NetworkX knowledge graph payload | Yes |
| `POST` | `/api/v1/eligibility/evaluate` | Deterministically evaluate user claims against an opportunity | Yes |
| `POST` | `/api/v1/privacy/preview` | Preview selective disclosure (disclosed vs redacted fields) | Yes |
| `POST` | `/api/v1/privacy/disclose` | Approve disclosure and generate Verifiable Presentation | Yes |
| `GET` | `/api/v1/career/gaps` | Analyze temporal career gaps and skill deficiencies | Yes |
| `GET` | `/api/v1/audit/logs` | Fetch user audit trail events | Yes |

*Full OpenAPI schema and interactive test console available at `http://localhost:8000/docs`.*

---

## 🔬 Research Context & Academic Evaluation

VERIFAI was formulated to address five foundational research questions in verifiable credentials and privacy-preserving AI:

- **RQ1 (Ingestion Grounding)**: How do multimodal claim extraction pipelines maintain provenance linking to underlying encrypted source documents?
- **RQ2 (Explainable Eligibility)**: Can deterministic rule engines paired with graph representations eliminate hallucinated eligibility decisions while maintaining complete auditability?
- **RQ3 (Data Minimization)**: What percentage of non-essential candidate attributes can be pruned from job/scholarship dossiers using automated selective disclosure policies?
- **RQ4 (Zero-Trust Key Derivation)**: What are the latency and throughput trade-offs of runtime HKDF per-user key derivation on encrypted document vaults?
- **RQ5 (Agentic Safety Boundaries)**: How effectively do strict schema contracts prevent prompt injection when parsing untrusted external opportunity criteria?

For the comprehensive research design and testing protocol, see [docs/research-plan.md](docs/research-plan.md).

---

## 🗺 Engineering Roadmap

- **Phase 1 (Current Baseline)**: AES-256-GCM Vault, Argon2id Auth, Deterministic Rule Engine, In-Memory Graph, Next.js 16 UI.
- **Phase 2 (Deep Vision)**: Local Transformer OCR (LayoutLMv3/Surya) and tabular transcript extraction.
- **Phase 3 (Distributed Graph & Vector)**: Production Neo4j 5.x cluster, pgvector embedding index, and Graph RAG.
- **Phase 4 (Cryptographic ZKP & BBS+)**: BBS+ multi-message signatures for selective disclosure, and zero-knowledge range proofs (e.g., proving `CGPA >= 8.0` without revealing the exact score).

*Review [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) for detailed milestone specifications.*

---

## 📄 Documentation Directory

- 📋 [**Implementation Status Matrix**](docs/IMPLEMENTATION_STATUS.md) — Line-by-line audit of real vs heuristic vs mocked capabilities.
- 🏛 [**System Architecture**](docs/architecture.md) — Comprehensive technical design and data flow diagrams.
- 🛡 [**Security & Vulnerability Policy**](docs/SECURITY.md) — Cryptographic primitives, key management, and responsible disclosure.
- 🎯 [**STRIDE Threat Model**](docs/THREAT_MODEL.md) — Threat actor analysis, trust boundaries, and applied mitigations.
- 🗺 [**Development Roadmap**](docs/DEVELOPMENT_ROADMAP.md) — Phased milestones from baseline to ZKP/BBS+.
- 📜 [**Product Requirements Document (PRD)**](docs/product-requirements.md) — Functional specifications and user personas.
- 🔬 [**Academic Research Plan**](docs/research-plan.md) — Formal methodology and experimental hypotheses.
- 🔌 [**API Design Specification**](docs/api-design.md) — Endpoint schemas and payload definitions.

---

## ⚖ License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software for educational, academic, and commercial purposes with attribution. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Responsible Disclosure & Contact

If you identify a security issue or vulnerability within this codebase, please refer to our [Security Policy](docs/SECURITY.md) and submit your findings responsibly rather than opening a public issue.
