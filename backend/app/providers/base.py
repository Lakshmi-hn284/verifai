"""
VERIFAI - Abstract Provider Interfaces
Decouples application services from concrete storage, AI models, and graph engines.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel


class ExtractedField(BaseModel):
    field_name: str
    category: str  # EDUCATION, SKILL, EXPERIENCE, CERTIFICATE, IDENTITY
    value: Any
    confidence: float  # 0.0 to 1.0
    page_number: Optional[int] = 1
    bounding_box: Optional[Dict[str, float]] = None  # {x, y, width, height}
    issuer: Optional[str] = None
    issued_date: Optional[str] = None


class DocumentExtractionResult(BaseModel):
    doc_type: str  # TRANSCRIPT, DEGREE, MARK_SHEET, CERTIFICATE, INTERNSHIP, RESUME, ID_DOCUMENT, OTHER
    extracted_fields: List[ExtractedField]
    raw_text: Optional[str] = None
    layout_metadata: Dict[str, Any] = {}


class StorageProvider(ABC):
    """Abstract interface for encrypted document blob storage."""

    @abstractmethod
    async def save_blob(self, user_id: str, document_id: str, data: bytes) -> Tuple[str, str]:
        """
        Encrypt and save data blob.
        Returns: (storage_path, nonce_hex)
        """
        pass

    @abstractmethod
    async def get_blob(self, user_id: str, storage_path: str, nonce_hex: str) -> bytes:
        """
        Retrieve and decrypt data blob.
        Returns decrypted plaintext bytes.
        """
        pass

    @abstractmethod
    async def delete_blob(self, storage_path: str) -> bool:
        """Delete blob from storage."""
        pass


class DocumentUnderstandingProvider(ABC):
    """Abstract interface for multimodal document intelligence."""

    @abstractmethod
    async def extract_document_structure(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str
    ) -> DocumentExtractionResult:
        """Parse document layout, tables, visual regions, and structured claims."""
        pass


class LLMProvider(ABC):
    """Abstract interface for LLM completions and reasoning."""

    @abstractmethod
    async def extract_requirements(self, text: str) -> List[Dict[str, Any]]:
        """Parse natural language opportunity criteria into structured conditions."""
        pass

    @abstractmethod
    async def generate_explanation(
        self,
        opportunity_title: str,
        matched_rules: List[Dict[str, Any]],
        missing_rules: List[Dict[str, Any]],
        evidence: Dict[str, Any]
    ) -> str:
        """Generate human-readable, grounded explanation of eligibility outcome."""
        pass


class KnowledgeGraphProvider(ABC):
    """Abstract interface for personal credential knowledge graph."""

    @abstractmethod
    async def add_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def add_edge(self, source_id: str, target_id: str, relationship: str, properties: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    async def get_user_subgraph(self, user_id: str) -> Dict[str, Any]:
        """Fetch all connected nodes and edges for visualization and reasoning."""
        pass

    @abstractmethod
    async def delete_node(self, node_id: str) -> None:
        pass
