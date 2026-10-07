# VERIFAI — Engineering & Research Roadmap

**Version:** 1.0.0-rc  
**Last Updated:** October 2026  

---

## 1. Roadmap Overview & Philosophy

VERIFAI's architectural strategy separates production-grade security fundamentals (encryption, key derivation, authentication, and deterministic verification) from external cloud dependencies.

This roadmap details the planned progression from the current self-contained baseline to enterprise deep-learning inference, distributed graph stores, and cryptographic zero-knowledge proofs.

---

## 2. Development Milestones

```
+─────────────────────────────────────────────────────────────────────────────+
| PHASE 1: Baseline Architecture (CURRENT RELEASE)                           |
| - AES-256-GCM Vault & HKDF-SHA256 Key Derivation                            |
| - Argon2id Password Hashing & JWT Authentication                            |
| - Deterministic Rule & Eligibility Engine                                   |
| - In-Memory NetworkX Knowledge Graph & Dual-Mode DB (PostgreSQL / SQLite)   |
| - Heuristic Document Extraction & W3C Presentation JSON Schema              |
| - Full Next.js 16 (Turbopack) & React 19 Frontend Dashboard                 |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| PHASE 2: Deep Vision Ingestion & Multi-Format Parsing                      |
| - Local OCR & LayoutLMv3 / Donut multimodal document parsing                |
| - Tabular extraction for semester-wise grade sheets & transcripts           |
| - Real PDF bounding-box mapping with visual highlight rendering             |
| - Anti-tampering visual inspection (font consistency, stamp detection)      |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| PHASE 3: Distributed Graph & Vector Graph RAG                               |
| - Production Neo4j 5.x cluster activation with Cypher query optimization     |
| - Native pgvector integration with local embedding models (MiniLM / BGE)    |
| - Hybrid Graph RAG: multi-hop knowledge graph traversal + semantic search   |
| - Automated ontology alignment between industry skill taxonomies (ESCO/O*NET|
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| PHASE 4: Cryptographic Selective Disclosure & Zero-Knowledge Proofs (ZKP)   |
| - BBS+ Multi-Message Signatures for cryptographic attribute redaction        |
| - Zero-Knowledge Range Proofs (proving CGPA >= 8.0 without revealing value) |
| - Decentralized Identifier (DID) resolution (did:web, did:key)              |
| - Cryptographically anchored Merkle tree audit logs                         |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 3. Detailed Phase Specifications

### Phase 1: Current Operational Baseline (Delivered)
- [x] **Zero-Trust Document Vault**: AES-256-GCM with per-user HKDF key derivation.
- [x] **Identity & Session Management**: Argon2id password hashing and JWT issuance.
- [x] **Relational Schema**: PostgreSQL with transparent SQLite fallback for zero-dependency local runs.
- [x] **Deterministic Rule Engine**: Multi-variable quantitative and categorical evaluation with score calculation.
- [x] **Knowledge Graph**: In-memory NetworkX directed graph with JSON persistence.
- [x] **Selective Disclosure Gateway**: Visual preview and human-in-the-loop consent enforcement.
- [x] **Modern Web UI**: Next.js 16, React 19, TypeScript, and Tailwind CSS.

### Phase 2: Deep Vision Ingestion & OCR
- [ ] **Local Transformer Integration**: Replace regex heuristic parser with a local Hugging Face pipeline (e.g. `microsoft/layoutlmv3-base` or Surya OCR).
- [ ] **Tabular Transcript Extraction**: Dedicated parser for credit tables, course codes, and SGPA/CGPA breakdowns.
- [ ] **Document Format Expansion**: First-class support for PDF vector streams, high-resolution scans, TIFF, and DOCX.
- [ ] **Visual Tamper Detection**: Optical artifact checks detecting text alterations, inconsistent fonts, or altered seal boundaries.

### Phase 3: Distributed Graph & Vector Graph RAG
- [ ] **Active Neo4j Driver Mode**: Move beyond in-memory NetworkX to active Neo4j container with persistent Cypher constraints.
- [ ] **pgvector Similarity Search**: Vector embeddings for requirement descriptions and user experiences using open-source sentence-transformers (`all-MiniLM-L6-v2`).
- [ ] **Skill Taxonomy Mapping**: Standardized alignment with ESCO (European Skills, Competences, Qualifications and Occupations) and O*NET taxonomies.
- [ ] **Multi-Hop Evidence Chains**: Traversal queries: `(Candidate)-[:COMPLETED]->(Project)-[:REQUIRES]->(Skill)-[:VALIDATES]->(OpportunityRequirement)`.

### Phase 4: Cryptographic BBS+ Selective Disclosure & ZKP
- [ ] **BBS+ Multi-Message Signatures**: Enable issuers to sign a credential vector such that the holder can cryptographically prove possession of a subset of claims without revealing others or needing re-issuance.
- [ ] **Zero-Knowledge Range Proofs**: Incorporate zk-SNARKs or Bulletproofs to mathematically prove:
  - $\text{ApplicantAge} \ge 18$
  - $\text{GraduationYear} \le 2024$
  - $\text{CGPA} \ge 8.0$
  without disclosing the actual numeric values to either the VERIFAI server or the third-party verifier.
- [ ] **W3C DID Registry Integration**: Verification of issuer public keys using `did:key` and `did:web` standards.
- [ ] **Immutable Audit Anchoring**: Anchoring audit log batches to an immutable Merkle tree to ensure tamper-evident non-repudiation.

---

## 4. Contributing & Research Collaboration

Researchers, faculty, and engineers interested in contributing to Phase 2 (OCR/Vision), Phase 3 (Graph RAG), or Phase 4 (BBS+/ZKP) are invited to open discussions in GitHub Discussions or submit proposals via pull request.
