# VERIFAI — System Architecture Document

**Version:** 1.0.0-rc  
**Last Updated:** October 2026  

---

## 1. System Overview

VERIFAI is a privacy-preserving intelligence platform designed to evaluate candidate eligibility for academic, corporate, and governmental opportunities without over-disclosing sensitive personal identifiable information (PII).

The architecture is built upon five foundational pillars:
1. **Zero-Trust Document Vault**: End-to-end encrypted file storage using per-user derived cryptographic keys.
2. **Provider Abstraction Layer**: Decoupled interfaces isolating AI inference, vector search, graph databases, and storage providers from core domain logic.
3. **Deterministic Rule-Based Intelligence**: Verifiable evaluation of multi-variable admission and hiring criteria with granular evidence mapping.
4. **Graph-Modeled Credential Relationships**: Entity-relationship tracking between users, documents, claims, and skill ontologies.
5. **Human-in-the-Loop Selective Disclosure**: Explicit user consent gateways ensuring only minimally required attributes are shared with external verifiers.

---

## 2. High-Level Architecture Diagram

```
+---------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER                                 |
|                     Next.js 16 (Turbopack) / React 19 / Tailwind CSS                  |
|  - Dashboard Summary        - Encrypted Document Vault     - Credentials Visualizer   |
|  - Opportunity Evaluator    - Knowledge Graph Explorer     - Selective Disclosure UI  |
+-------------------------------------------+-------------------------------------------+
                                            |
                                  REST APIs (JSON / HTTPS)
                                  Bearer JWT Authentication
                                            |
+-------------------------------------------v-------------------------------------------+
|                                   APPLICATION GATEWAY                                 |
|                         FastAPI / Pydantic v2 / Python 3.14                           |
|  - Auth & Argon2id Security - Request Validation           - Audit Trail Logger       |
|  - CORS & Error Handlers    - Dependency Injection         - Rate Limiter Middleware  |
+-------------------------------------------+-------------------------------------------+
                                            |
              +-----------------------------+-----------------------------+
              |                             |                             |
+-------------v-------------+ +-------------v-------------+ +-------------v-------------+
|    CORE DOMAIN SERVICES   | |     INTELLIGENCE ENGINES  | |    PRIVACY & PACKAGING    |
| - VaultService            | | - EligibilityEngine       | | - DisclosurePolicyEngine  |
| - DocumentManager         | | - RuleEngine (>=, <=, IN) | | - HumanConsentGateway     |
| - ClaimService            | | - CareerGapAnalyzer       | | - W3C Verifiable          |
| - OpportunityService      | | - KnowledgeGraphService   | |   Presentation Builder    |
+-------------+-------------+ +-------------+-------------+ +-------------+-------------+
              |                             |                             |
+-------------v-----------------------------v-----------------------------v-------------+
|                                 PROVIDER ABSTRACTION LAYER                            |
|  [StorageProvider]        [DocumentProvider]          [GraphProvider]   [LLMProvider] |
+-------------+---------------------+---------------------+---------------+-------------+
              |                     |                     |               |
              v                     v                     v               v
+-----------------------+ +-------------------+ +-------------------+ +-----------------+
|   PERSISTENCE LAYER   | |   INGESTION / OCR | |   GRAPH ENGINE    | |   AI INFERENCE  |
| - PostgreSQL          | | - Multimodal      | | - NetworkX        | | - Template /    |
|   (SQLite Fallback)   | |   Heuristic Parser| |   In-Memory Engine| |   MockLLM       |
| - AES-256-GCM Vault   | | - Layout Geomet.  | | - Neo4j Driver    | | - Cloud LLM     |
|   Storage on Disk     | |   Bounding Boxes  | |   (Scaffolded)    | |   (Abstracted)  |
+-----------------------+ +-------------------+ +-------------------+ +-----------------+
```

---

## 3. End-to-End Data Flow

The platform executes a strict sequence for processing credentials and verifying qualifications:

```
[User Upload]
      │
      ▼
1. INGEST & ENCRYPT
   ├── Compute SHA-256 content checksum of raw file
   ├── Derive per-user AES-256 key via HKDF(MasterKey, UserUUID)
   ├── Encrypt payload using AES-256-GCM (random 96-bit nonce + 128-bit auth tag)
   └── Store encrypted blob in Vault Storage; register metadata in Relational DB
      │
      ▼
2. STRUCTURED EXTRACTION
   ├── DocumentUnderstandingProvider parses document text and metadata
   ├── Extracts structured candidate claims (Degree, Major, Institution, GPA, Dates)
   └── Associates claims with document reference and user identity
      │
      ▼
3. KNOWLEDGE GRAPH REIFICATION
   ├── GraphService inserts/updates nodes: (:User), (:Claim), (:Document), (:Skill)
   └── Creates directed relationships:
         (:User)-[:HAS_CLAIM]->(:Claim)-[:EVIDENCED_BY]->(:Document)
         (:Claim)-[:DEMONSTRATES]->(:Skill)
      │
      ▼
4. OPPORTUNITY ANALYSIS & ELIGIBILITY EVALUATION
   ├── Recruiter or applicant submits opportunity requirements schema
   ├── RuleEngine processes criteria:
   │     • Quantitative bounds (CGPA >= 8.0, YearsOfExperience >= 3)
   │     • Categorical matches (Degree IN ['B.Tech', 'B.S.', 'M.S.'])
   │     • Mandatory requirements (Accreditation REQUIRED)
   └── Generates granular score ratio and evidence-mapped validation trail
      │
      ▼
5. SELECTIVE DISCLOSURE & HUMAN-IN-THE-LOOP APPROVAL
   ├── DisclosurePolicyEngine compares required attributes vs user claims
   ├── Identifies non-essential attributes (DOB, home address, unrelated courses)
   ├── Renders preview showing Disclosed vs Masked vs Redacted fields
   └── Awaits explicit user consent
      │
      ▼
6. VERIFIABLE PRESENTATION EXPORT
   └── Packages approved claims into a standardized W3C Verifiable Presentation JSON
```

---

## 4. Subsystem Details

### 4.1 Encrypted Document Vault & Key Management
- **Key Hierarchy**:
  - `VAULT_MASTER_KEY`: 32-byte high-entropy root secret configured in the environment.
  - `User Salt`: Cryptographically unique user UUID (`user.id`).
  - `Derived Vault Key`: Computed dynamically at runtime via HKDF-SHA256:
    $$\text{UserKey} = \text{HKDF-SHA256}(\text{IKM}=\text{MasterKey}, \text{salt}=\text{UserUUID}, \text{info}=\text{"verifai-user-vault"})$$
- **Encryption Primitive**: AES-256 in Galois/Counter Mode (GCM) using `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.
- **Integrity**: Decryption strictly verifies the 16-byte authentication tag; any ciphertext alteration causes an immediate `CiphertextTamperedError`.

### 4.2 Dual-Mode Persistence Architecture
To guarantee zero-friction onboarding for researchers and evaluators without requiring multi-container setups, all persistence layers support automatic fallback:

| Engine | Production Mode | Fallback / Zero-Dependency Mode |
| :--- | :--- | :--- |
| **Relational Database** | PostgreSQL 16+ via SQLAlchemy ORM | Embedded SQLite (`sqlite:///./verifai.db`) |
| **Graph Database** | Neo4j 5.x via Cypher query driver | `NetworkX` in-memory directed graph with JSON sync |
| **Vector Engine** | `pgvector` extension for PostgreSQL | Deterministic similarity matching |
| **Document Storage** | Local volume encrypted directory | Local sandbox directory (`vault_storage/`) |

### 4.3 Knowledge Graph Ontology
The graph models relationships that cannot be efficiently captured in flat relational tables:
- **Node Labels**:
  - `User`: The platform account holder.
  - `Document`: The cryptographically verified source artifact.
  - `Claim`: A specific factual assertion (e.g., `Degree: B.Tech Computer Science`, `CGPA: 8.85`).
  - `Skill`: Standardized ontology competencies (e.g., `Python`, `Machine Learning`, `Distributed Systems`).
  - `Requirement`: Opportunity constraints.
- **Relationship Edges**:
  - `(User)-[:HAS_CLAIM]->(Claim)`
  - `(Claim)-[:EVIDENCED_BY]->(Document)`
  - `(Claim)-[:DEMONSTRATES]->(Skill)`
  - `(Requirement)-[:REQUIRES]->(Skill)`

---

## 5. Security & Boundary Architecture

```
[Untrusted Client Network]
           │
           ▼
[TLS Termination / Reverse Proxy]
           │
           ▼
[FastAPI Gateway Boundary]
   ├── CORS Validation
   ├── Bearer JWT Verification
   ├── Argon2id Password Auth
   └── Request Body Deserialization (Pydantic)
           │
           ▼
[Domain Execution Sandbox]
   ├── User Isolation (user_id enforced on all queries)
   ├── Memory-Only Decryption (cleartext never written to unencrypted disks)
   └── Audit Logging of all I/O events
           │
           ▼
[Encrypted Storage at Rest]
   ├── AES-256-GCM Blobs
   └── Salted Hash Records
```

---

## 6. Repository Directory Structure

```
VERIFAI/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoint routers
│   │   ├── core/            # Config, security, crypto, database engine
│   │   ├── models/          # SQLAlchemy relational models
│   │   ├── providers/       # Abstraction interfaces and mock/real implementations
│   │   ├── schemas/         # Pydantic data validation schemas
│   │   └── services/        # Core domain services (vault, eligibility, graph, privacy)
│   ├── tests/               # Pytest automated test suite
│   ├── Dockerfile           # Backend container specification
│   ├── pytest.ini           # Test configuration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js 16 App Router pages
│   │   ├── components/      # UI component library
│   │   ├── lib/             # API client and utility routines
│   │   └── types/           # TypeScript interfaces matching backend schemas
│   ├── Dockerfile           # Frontend container specification
│   ├── package.json         # Node.js dependencies
│   └── tsconfig.json        # TypeScript configuration
├── docs/                    # Technical documentation & architecture reports
├── docker-compose.yml       # Multi-service container orchestration
├── .env.example             # Documented template of environment variables
└── README.md                # Project documentation and getting started guide
```
