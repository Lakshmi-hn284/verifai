# VERIFAI — System Architecture Document

## 1. Executive Overview

VERIFAI is a **Privacy-Preserving AI Credential & Eligibility Intelligence Platform**. It bridges document understanding, evidence-based reasoning, graph-based credential mapping, and privacy-first selective disclosure to enable users to evaluate eligibility for opportunities (jobs, scholarships, admissions, exams) without over-sharing sensitive personal data.

---

## 2. Architecture & Design Principles

1. **Modular Clean Architecture**: Domain logic is decoupled from AI providers, database drivers, and external frameworks.
2. **Provider Abstraction Pattern**: Interfaces (`LLMProvider`, `EmbeddingProvider`, `DocumentUnderstandingProvider`, `CredentialProvider`, `StorageProvider`) allow plug-and-play AI backends (OpenAI, Gemini, Local models) and storage engines.
3. **Hybrid Eligibility Engine**: Combines deterministic rule checking, semantic vector matching (RAG/pgvector), evidence graph mapping, and LLM explanation generation.
4. **Least-Privilege Agent System**: Multi-agent framework with strict role-based tool boundaries (Document Agent, Requirement Agent, Evidence Agent, Eligibility Agent, Privacy Agent, Credential Agent, Application Agent).
5. **Zero-Trust Privacy & Consent**: Default zero-disclosure state. Selective disclosure policy engine evaluates required vs unrequested attributes, requiring explicit human approval before packaging data.

---

## 3. High-Level System Architecture

```
                                  +-----------------------+
                                  |    Next.js Web UI     |
                                  | (TypeScript/Tailwind) |
                                  +-----------+-----------+
                                              |
                                      HTTPS / REST APIs
                                              |
                                  +-----------v-----------+
                                  |    FastAPI Gateway    |
                                  |  (Auth, Middleware)   |
                                  +-----------+-----------+
                                              |
      +---------------------------------------+---------------------------------------+
      |                                       |                                       |
+-----v-----------------+           +---------v-------------+           +-------------v---------+
|   Core Business Logic |           |   AI Agent Orchestrator|          |   Privacy & VC Engine |
| - Document Manager    |           | - Doc Agent           |          | - Selective Disclosure|
| - Claim Engine        |           | - Requirement Agent   |          | - W3C VC 2.0 Abstr.   |
| - Opportunity Engine  |           | - Eligibility Agent   |          | - Disclosure Approval |
| - Hybrid Rule Engine  |           | - Privacy Agent       |          | - Application Packager|
+-----+-----------------+           +---------+-------------+           +-------------+---------+
      |                                       |                                       |
+-----v---------------------------------------v---------------------------------------v---------+
|                                    Provider Layer (Abstractions)                              |
|   [StorageProvider]       [DocumentUnderstandingProvider]      [LLMProvider]   [EmbeddingProvider] |
+-----+---------------------------------------+---------------------------------------+---------+
      |                                       |                                       |
+-----v-----------------+           +---------v-------------+           +-------------v---------+
| PostgreSQL + pgvector |           |   Graph DB (Neo4j)    |           | Local Encrypted Storage|
| (Users, Metadata,     |           | (User, Skills, Claims,|           | (AES-256-GCM Vault)   |
|  Claims, Audit Logs)  |           |  Evidence, Rules)     |           |                       |
+-----------------------+           +-----------------------+           +-----------------------+
```

---

## 4. Component Deep-Dive

### 4.1 Frontend Layer (Next.js 14+ / React)
- **Tech**: Next.js App Router, TypeScript, Tailwind CSS, Lucide icons, Recharts/Vis.js for visualization.
- **Key Modules**: Dashboard, Document Vault, Credential Profile, Knowledge Graph Visualizer, Opportunity Analyzer, Eligibility Report with Evidence Tree, Selective Disclosure Review Modal, Career Gap Radar, Audit Trail.

### 4.2 API Layer (FastAPI)
- **Tech**: FastAPI, Pydantic v2, Python 3.14+, OAuth2 JWT / HTTP-only secure cookies.
- **Middleware**: Rate limiting, CORS, Request sanitization, Audit logger.

### 4.3 Storage & Persistence Strategy
- **Relational Storage (PostgreSQL)**: Users, Auth Sessions, Document Metadata, Claims, Opportunities, Applications, Audit Trails.
- **Vector Storage (pgvector)**: 1536/768-dim embeddings for document text chunks, requirement semantics, skill definitions.
- **Graph Storage (Neo4j / Fallback Graph Engine)**: Relationships between `(User)-[:HAS_CLAIM]->(Claim)-[:EVIDENCED_BY]->(Document)`, `(Claim)-[:DEMONSTRATES]->(Skill)`, `(Requirement)-[:REQUIRES]->(Skill)`.
- **Encrypted Document Vault**: Local storage (or S3 abstraction) encrypting stored file blobs at rest with AES-256-GCM and unique per-user keys.

### 4.4 AI Provider Abstractions
- `LLMProvider`: Standard interface for structured JSON generation, requirement extraction, and natural language explanations.
- `DocumentUnderstandingProvider`: Abstraction for multimodal page/layout parsing, bounding box extraction, and table understanding.
- `EmbeddingProvider`: Text embedding interface for vector search.

### 4.5 Agent Framework & Safety Control
Agents operate under strict permission sets:
- **Document Agent**: Reads raw document layout & metadata.
- **Requirement Agent**: Reads opportunity raw text, outputs structured criteria.
- **Evidence Agent**: Queries graph & vector store for matching claims/documents.
- **Eligibility Agent**: Evaluates rule engine + evidence graphs.
- **Privacy Agent**: Compares requirement schemas against claim schemas; generates minimum-disclosure proposals.
- **Application Agent**: Packages ONLY user-approved claims into JSON/PDF export.

---

## 5. Deployment Architecture

- **Docker Compose**: Orchestrates FastAPI backend, PostgreSQL + pgvector, Neo4j, and Next.js frontend for single-command orchestration.
- **Standalone Fallback Mode**: Embedded SQLite / in-memory vector & graph modes for instant local development without complex background container requirements.
