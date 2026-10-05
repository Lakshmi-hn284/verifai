# VERIFAI — Product Requirements Document (PRD)

## 1. Product Identification
- **Name**: VERIFAI
- **Full Title**: Privacy-Preserving AI Credential & Eligibility Intelligence Platform
- **Tagline**: *"Prove what matters. Share only what is needed."*

---

## 2. Problem Statement
Job seekers, students, and applicants frequently upload complete identity and credential documents (degrees, transcripts, IDs, marksheets) to multiple third-party systems without knowing:
1. Whether they actually fulfill the criteria.
2. What specific claims are missing.
3. Which document proves which requirement.
4. What personal sensitive data (address, date of birth, identity numbers) is being unnecessarily exposed.

---

## 3. Key Functional Modules & Requirements

### Module A — Authentication & Identity
- **Req A1**: User registration with email, password, and optional profile metadata.
- **Req A2**: Password hashing using Argon2id with salt.
- **Req A3**: JWT-based session tokens with HTTP-only secure cookie support.
- **Req A4**: Role/Permission scaffolding for future OIDC/OAuth 2.x integration.

### Module B — Secure Document Vault
- **Req B1**: Support PDF, PNG, JPG/JPEG file uploads up to 15MB.
- **Req B2**: AES-256-GCM authenticated encryption at rest for stored files.
- **Req B3**: SHA-256 cryptographic file hashing for content integrity tracking.
- **Req B4**: Strict MIME-type checking, extension verification, and size validation.

### Module C — Multimodal Document Intelligence
- **Req C1**: Extract text, layout hierarchy, tables, page numbers, confidence scores, and bounding boxes.
- **Req C2**: Decoupled interface `DocumentUnderstandingProvider` allowing swapping between providers (Mock/Local, Vision LLM, etc.).
- **Req C3**: Structured output format detailing claim name, value, source document ID, page, bounding region, and confidence rating.

### Module D — Credential Profile & Claim Engine
- **Req D1**: Standardized claims structure (Education, Skills, Work Experience, Certifications, Language, Identity attributes).
- **Req D2**: Claim metadata tracking: Claim status (Verified, Extracted, Pending, Self-asserted), confidence, issuer, issuing date, expiration.

### Module E — Personal Credential Knowledge Graph
- **Req E1**: Model entities: User, Education, Institution, Skill, Certificate, Project, Internship, Requirement, Evidence, Opportunity.
- **Req E2**: Graph query engine supporting path-finding between user claims and target opportunity requirements.

### Module F & G — Opportunity Ingestion & Requirement Extraction
- **Req F1**: Ingestion of raw text job descriptions, university admission criteria, scholarship guidelines, or PDF documents.
- **Req G1**: Structured requirement parsing via `RequirementAgent` into deterministic conditions (`IN`, `>=`, `<=`, `REQUIRED`, `CONTAINS`).
- **Req G2**: Strict JSON Schema validation for all extracted requirement rules.

### Module H, I & J — Hybrid Eligibility Engine & Explainability
- **Req H1**: Dual-layer reasoning: Deterministic rule evaluation + Semantic vector matching + Evidence graph verification + LLM contextual explanation.
- **Req H2**: Output breakdown: Overall match percentage score, Satisfied requirements list, Partially satisfied requirements list, Missing requirements list.
- **Req I1**: Interactive Evidence Graph mapping every decision back to source document, page, and snippet.
- **Req J1**: Explainable AI interface answering: What was decided? Why? What evidence supports it? How confident is it? What action to take?

### Module K, L, M & N — Privacy Engine & Verifiable Credentials
- **Req K1**: Minimum Disclosure Calculator comparing required fields vs document attributes.
- **Req L1**: W3C Verifiable Credentials 2.0 compliant data model (Issuer, Holder, Verifier, CredentialSubject, Proof).
- **Req M1**: Interactive Selective Disclosure review panel displaying "Requested & Approved" vs "Redacted / Unnecessary" fields before any export.
- **Req N1**: Credential status lifecycle (Active, Expired, Suspended, Revoked).

### Module O, P, Q & R — Agentic AI, RAG, Package Generator & Gap Analysis
- **Req O1**: Orchestrate specialized subagents with tool allowlists & strict boundary enforcement.
- **Req P1**: Hybrid retrieval (pgvector semantic similarity + metadata filters + keyword search).
- **Req Q1**: Export user-approved Minimum Disclosure Application Packages (JSON/PDF summary).
- **Req R1**: Career Gap Analytics aggregating missing skills across multiple analyzed opportunities.

---

## 4. Non-Functional Requirements (NFRs)
- **Security**: Zero plain-text secrets, AES-256-GCM file encryption, Argon2id passwords, strict input validation.
- **Performance**: Document analysis < 5s for standard PDFs, eligibility evaluation < 2s.
- **Usability**: Modern SaaS UI design, dark mode palette, responsive visual graph renderers.
- **Maintainability**: Modular clean architecture, type safety (Pydantic v2 & TypeScript interfaces), 80%+ test coverage target.
