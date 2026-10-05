"""
VERIFAI - SQLAlchemy Domain Models
Core relational schemas for Users, Audit Logs, Vault Documents, Claims,
Opportunities, Eligibility Evaluations, and Disclosure Records.
"""
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vault_salt: Mapped[str] = mapped_column(String(64), nullable=False, default=lambda: uuid.uuid4().hex)

    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="user", cascade="all, delete-orphan")
    opportunities: Mapped[List["Opportunity"]] = relationship("Opportunity", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUCCESS")
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    metadata_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 for integrity verification
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    nonce_hex: Mapped[str] = mapped_column(String(32), nullable=False)  # 12-byte GCM nonce in hex
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="UPLOADED")  # UPLOADED, PROCESSING, EXTRACTED, FAILED
    doc_type: Mapped[str] = mapped_column(String(64), nullable=False, default="OTHER")  # TRANSCRIPT, DEGREE, CERTIFICATE, etc.
    extracted_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="documents")
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="source_document", cascade="all, delete-orphan")


class Claim(Base, TimestampMixin):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # EDUCATION, SKILL, EXPERIENCE, CERTIFICATE, IDENTITY
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    field_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bounding_box: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="EXTRACTED", nullable=False)
    issuer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    issued_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="claims")
    source_document: Mapped[Optional["Document"]] = relationship("Document", back_populates="claims")


class Opportunity(Base, TimestampMixin):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    opportunity_type: Mapped[str] = mapped_column(String(64), default="JOB", nullable=False)
    extracted_requirements: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="opportunities")
    evaluations: Mapped[List["EligibilityEvaluation"]] = relationship("EligibilityEvaluation", back_populates="opportunity", cascade="all, delete-orphan")
    disclosures: Mapped[List["DisclosureConsent"]] = relationship("DisclosureConsent", back_populates="opportunity", cascade="all, delete-orphan")


class EligibilityEvaluation(Base, TimestampMixin):
    __tablename__ = "eligibility_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # ELIGIBLE, PARTIALLY_ELIGIBLE, INELIGIBLE
    match_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    satisfied_rules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    partially_satisfied_rules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    missing_rules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    evidence_map: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    explanation_markdown: Mapped[str] = mapped_column(Text, nullable=False)

    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="evaluations")


class DisclosureConsent(Base, TimestampMixin):
    __tablename__ = "disclosure_consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_attributes: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    redacted_attributes: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    user_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    package_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="disclosures")
