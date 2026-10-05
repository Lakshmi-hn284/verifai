# VERIFAI — Privacy-Preserving AI Credential & Eligibility Intelligence Platform

> **"Prove what matters. Share only what is needed."**

VERIFAI is a research-oriented, privacy-first platform that enables users to securely upload identity and credential documents once, extract structured claims using multimodal document intelligence, reason over eligibility requirements for jobs/scholarships using evidence graphs, and export minimum-disclosure application packages without over-sharing personal data.

---

## 🌟 Core Value Proposition

- **Multimodal Document Intelligence**: Parses academic transcripts, degree certificates, skill credentials, and marksheets into structured claims with visual grounding.
- **Evidence-Based Hybrid Reasoning**: Evaluates eligibility through deterministic rules + vector similarity + evidence graph mapping + explainable LLM reasoning.
- **Zero-Trust Selective Disclosure**: Calculates minimum required disclosure and guarantees that sensitive non-required data (e.g. date of birth, address, ID numbers) is redacted prior to user approval.
- **Career Gap Intelligence**: Aggregates recurring missing skills across target opportunities to provide data-driven professional guidance.
- **Agentic AI Architecture**: Employs role-scoped AI agents with tool allowlists and strict safety boundaries.

---

## 🏗 System Architecture Overview

VERIFAI follows a decoupled Clean Architecture with abstraction interfaces:

```
[ Next.js 14+ Frontend ] <--- REST APIs ---> [ FastAPI Backend Service ]
                                                      |
    +-------------------------------------------------+-------------------------------------------------+
    |                                                 |                                                 |
[ Domain Services & Rules Engine ]           [ Multi-Agent Orchestrator ]              [ Privacy & Disclosure Engine ]
    |                                                 |                                                 |
[ PostgreSQL / pgvector Storage ]            [ Neo4j Knowledge Graph ]                 [ Encrypted Vault Storage ]
```

---

## 📁 Repository Structure

```
VERIFAI/
├── docs/                        # Comprehensive Architecture, PRD, Security, API & Research docs
│   ├── architecture.md
│   ├── product-requirements.md
│   ├── security-model.md
│   ├── research-plan.md
│   └── api-design.md
├── backend/                     # Python / FastAPI Backend Service
│   ├── app/
│   │   ├── api/                 # API Routes & Endpoint Handlers
│   │   ├── core/                # Config, Security, Audit Logger, Errors
│   │   ├── db/                  # DB Connection, Base Models, Migrations
│   │   ├── domain/              # Entities, Value Objects, Domain Exceptions
│   │   ├── providers/           # Provider Abstractions & Adapters (LLM, Doc, Storage)
│   │   ├── services/            # Business Logic & Orchestration
│   │   ├── agents/              # Permission-bounded AI Agents
│   │   └── models/              # Pydantic Schemas & ORM Data Models
│   ├── tests/                   # Pytest Test Suite
│   └── requirements.txt
├── frontend/                    # Next.js 14 / TypeScript / Tailwind CSS Web App
│   ├── src/
│   │   ├── app/                 # Next.js App Router Pages
│   │   ├── components/          # UI Components & Modules
│   │   ├── lib/                 # API Clients, Utilities, Types
│   │   └── styles/              # Global Styles & Tokens
│   └── package.json
├── docker-compose.yml           # Multi-container orchestration (FastAPI, Postgres, Neo4j, Next.js)
└── README.md
```

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ (Tested on Node.js v24)
- Docker & Docker Compose (Optional for containerized mode)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔬 Research Goals & Benchmarks

VERIFAI investigates 5 key research questions:
- **RQ1**: Multimodal document extraction precision/recall vs OCR-only baselines.
- **RQ2**: Explainability and auditability via evidence graph mapping.
- **RQ3**: Attribute reduction percentage via minimum disclosure policies.
- **RQ4**: Accuracy and reduction of false positives/negatives in hybrid eligibility vs LLM-only evaluation.
- **RQ5**: Safety and prompt-injection resilience in permission-bounded multi-agent systems.

---

## 🔐 Security & Privacy Commitments

- **Encryption at Rest**: AES-256-GCM authenticated encryption for document vault storage.
- **Password Security**: Argon2id salted hashing.
- **No Plaintext Passwords or Secret Storage**.
- **Human-in-the-Loop Consent**: No autonomous submission or disclosure without explicit user review.
