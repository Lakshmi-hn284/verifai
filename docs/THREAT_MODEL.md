# VERIFAI — STRIDE Threat Model & Risk Analysis

**Version:** 1.0.0-rc  
**Last Updated:** October 2026  

---

## 1. Introduction & Scope

This document provides a systematic threat model for VERIFAI using the **STRIDE** methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege).

The scope encompasses:
- End-user interactions via the web client.
- The FastAPI application gateway and business logic services.
- The document vault and cryptographic subsystem.
- Relational and graph persistence layers.
- The selective disclosure and verifiable presentation export pipeline.

---

## 2. System Assets & Trust Boundaries

```
[ UNTRUSTED ZONE: Public Internet ]
           │
           │  (TLS Boundary / HTTPS)
           ▼
[ TRUST BOUNDARY 1: Web Gateway ]
   - Next.js Client & Browser Memory
   - Reverse Proxy & Gateway Endpoints
           │
           │  (Authenticated JWT Boundary)
           ▼
[ TRUST BOUNDARY 2: Core Domain Execution ]
   - FastAPI Domain Services
   - Cryptographic Engine (Memory Only)
   - Knowledge Graph Engine
           │
           │  (Storage Boundary)
           ▼
[ TRUST BOUNDARY 3: Persistence Layer ]
   - Encrypted Document Vault (AES-256-GCM Blobs)
   - Relational Database (SQLAlchemy / PostgreSQL)
   - Audit Log Trail
```

### Critical Assets Protected
1. **Raw Document Payloads**: Academic transcripts, certificates, government IDs.
2. **Derived Structured Claims**: Verified grades, degree names, graduation dates, test scores.
3. **User Authentication Secrets**: Passwords, derived encryption keys, active JWTs.
4. **Eligibility Reports & Verifiable Packages**: Decision rationales and exported claims.
5. **System Audit Logs**: Historical records of uploads, extractions, evaluations, and disclosures.

---

## 3. Threat Actors & Adversarial Profiles

| Threat Actor | Motivation | Capabilities & Access |
| :--- | :--- | :--- |
| **Untrusted Third-Party Verifier** | Harvest excessive PII, cross-correlate candidate profiles across platforms. | Authorized to receive candidate presentation packages; attempts to demand or infer unrequested attributes. |
| **Compromised Storage Operator** | Exfiltrate candidate records or bulk credentials from server backup dumps. | Has direct read access to raw disk volumes and relational database backups, but does NOT possess runtime environment secrets. |
| **Malicious Candidate** | Forge credentials, alter GPA/degree claims, or bypass eligibility gates. | Legitimate authenticated user attempting to upload tampered files or forge API payloads. |
| **Network Eavesdropper** | Intercept credentials or authentication tokens in transit. | Passive or active man-in-the-middle on public Wi-Fi or transit networks. |

---

## 4. STRIDE Threat Analysis & Mitigations

### 4.1 Spoofing (Identity Deception)
- **Threat**: An attacker impersonates a candidate or verifier to access confidential dossiers.
- **Vulnerabilities**: Weak passwords, token replay, lack of multi-factor authentication.
- **Implemented Mitigations**:
  - Passwords hashed with high-cost **Argon2id** algorithm (`argon2-cffi`).
  - Cryptographically signed JWTs using HMAC-SHA256 with explicit expiration (`exp` claim).
  - User identity strictly isolated: all database queries enforce `user_id == current_user.id`.

### 4.2 Tampering (Data Modification)
- **Threat**: An attacker modifies encrypted document blobs on disk or alters claim values in the database.
- **Vulnerabilities**: Storage without integrity verification; lack of signature verification on claims.
- **Implemented Mitigations**:
  - **AES-256-GCM 128-bit Authentication Tag**: Decryption verifies the tag before returning plaintext. Any modified byte causes immediate failure.
  - **SHA-256 Content Addressing**: Hash of the raw document is stored at upload time and validated against subsequent reads.
  - **ORM Parameterization**: Prevents SQL injection attacks altering relational state.

### 4.3 Repudiation (Denial of Action)
- **Threat**: A candidate denies having shared a credential package, or an auditor disputes an eligibility evaluation.
- **Vulnerabilities**: Missing or mutable audit trails.
- **Implemented Mitigations**:
  - Comprehensive `AuditLog` service records every critical lifecycle event: `UPLOAD`, `ENCRYPT`, `EXTRACT`, `EVALUATE`, `DISCLOSE`, `EXPORT`.
  - Every event captures `user_id`, `event_type`, `resource_id`, `timestamp`, and structured metadata.
  - *Roadmap*: Merkle tree anchoring to achieve cryptographic non-repudiation.

### 4.4 Information Disclosure (Data Leakage)
- **Threat**: Over-disclosure of unrequested personal attributes (home address, exact date of birth, caste/demographic data) to corporate or academic verifiers.
- **Vulnerabilities**: Sending whole PDF documents to verifiers when only a degree requirement was requested.
- **Implemented Mitigations**:
  - **Selective Disclosure Policy Engine**: Compares opportunity criteria against available claims and excludes non-essential attributes.
  - **Human-in-the-Loop Consent Gateway**: Candidate inspects a visual diff of requested, disclosed, and redacted attributes before approving transmission.
  - **Zero-Trust Encryption at Rest**: Compromised disk volumes yield only AES-256-GCM ciphertext without the environment-held master key.

### 4.5 Denial of Service (System Exhaustion)
- **Threat**: Uploading massive files or generating recursive graph operations to exhaust server CPU and RAM.
- **Vulnerabilities**: Unbounded file uploads, unindexed graph queries.
- **Implemented Mitigations**:
  - Strict file size constraints enforced in FastAPI endpoints.
  - In-memory graph processing operates on localized subgraphs scoped strictly to the authenticated user.
  - Ephemeral memory deallocation after document processing.

### 4.6 Elevation of Privilege (Unauthorized Access)
- **Threat**: An authenticated user accesses another candidate's document vault or claims.
- **Vulnerabilities**: Broken Object Level Authorization (BOLA / IDOR).
- **Implemented Mitigations**:
  - Strict authorization checks in all service layers: `get_document_by_id(doc_id, user_id=current_user.id)`.
  - Per-user cryptographic key derivation: even if User B somehow bypassed database authorization, they cannot decrypt User A's ciphertext without User A's derived key.

---

## 5. Trust Assumptions & Operational Limits

1. **Host Environment Integrity**: The operating system and runtime environment holding `VAULT_MASTER_KEY_HEX` and `JWT_SECRET_KEY` are assumed to be secure.
2. **Current Heuristic Boundary**: Document text extraction currently operates via deterministic heuristic regex parsing. Verification against cryptographically signed issuing institution root keys (e.g. EBSI or W3C DID Registries) is an architectural roadmap item.
3. **Application Layer Enforcement**: Selective disclosure is enforced by the application's policy engine. Cryptographic Zero-Knowledge Proofs (such as proving `CGPA > 8.0` without revealing exact score to the server) are designed for Phase 4 of the development roadmap.
