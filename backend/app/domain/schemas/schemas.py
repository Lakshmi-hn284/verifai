"""
VERIFAI - Pydantic Request & Response Schemas
Type-safe input/output models conforming to strict API contracts.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# --- Generic API Envelope ---
class MetaResponse(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: Optional[str] = None


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    meta: Optional[MetaResponse] = Field(default_factory=MetaResponse)


# --- Authentication & User Schemas ---
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    full_name: str = Field(min_length=2, max_length=100)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# --- Document Vault Schemas ---
class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    content_type: str
    file_size_bytes: int
    status: str
    doc_type: str
    sha256_hash: str
    created_at: datetime
    claims_count: Optional[int] = 0


class DocumentDetailResponse(DocumentResponse):
    extracted_metadata: Dict[str, Any] = {}
    claims: List["ClaimResponse"] = []


# --- Claim Schemas ---
class ClaimCreateRequest(BaseModel):
    category: str = Field(description="EDUCATION, SKILL, EXPERIENCE, CERTIFICATE, IDENTITY")
    field_name: str
    field_value: Any
    issuer: Optional[str] = None
    issued_date: Optional[str] = None


class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    document_id: Optional[str]
    category: str
    field_name: str
    field_value: Any
    confidence: float
    page_number: Optional[int]
    bounding_box: Optional[Dict[str, Any]]
    verification_status: str
    issuer: Optional[str]
    issued_date: Optional[str]
    created_at: datetime


# --- Opportunity & Requirement Schemas ---
class OpportunityCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    organization: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10)
    opportunity_type: str = Field(default="JOB", description="JOB, INTERNSHIP, SCHOLARSHIP, ADMISSION, EXAM")


class RequirementCondition(BaseModel):
    type: str  # education, academic, skill, experience, language, certification
    field: str  # degree, cgpa, skill, years, etc.
    operator: str  # IN, >=, <=, ==, REQUIRED, CONTAINS
    value: Any
    importance: str = "REQUIRED"  # REQUIRED or PREFERRED
    description: str


class OpportunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    organization: str
    description: str
    opportunity_type: str
    status: str
    extracted_requirements: Dict[str, Any] = {}
    created_at: datetime


# --- Eligibility Evaluation Schemas ---
class EligibilityEvaluateRequest(BaseModel):
    opportunity_id: str


class EligibilityReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    opportunity_id: str
    opportunity_title: str
    status: str  # ELIGIBLE, PARTIALLY_ELIGIBLE, INELIGIBLE
    match_score: float
    satisfied_rules: List[Dict[str, Any]]
    partially_satisfied_rules: List[Dict[str, Any]]
    missing_rules: List[Dict[str, Any]]
    evidence_map: Dict[str, Any]
    explanation_markdown: str
    created_at: datetime


# --- Privacy & Selective Disclosure Schemas ---
class DisclosurePreviewResponse(BaseModel):
    opportunity_id: str
    opportunity_title: str
    requested_attributes: List[Dict[str, Any]]  # attribute name, requirement reason
    redacted_attributes: List[Dict[str, Any]]   # attribute name, explanation why not needed
    disclosure_reduction_percentage: float


class DisclosureApprovalRequest(BaseModel):
    opportunity_id: str
    approved: bool
    allowed_attributes: List[str]


class ApplicationPackageResponse(BaseModel):
    package_id: str
    opportunity_title: str
    organization: str
    generated_at: datetime
    verifiable_claims: List[Dict[str, Any]]
    redacted_count: int
    package_hash: str
