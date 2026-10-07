"""
VERIFAI - Application Configuration
Uses pydantic-settings to manage configuration from environment variables or defaults.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(BASE_DIR.parent / ".env"), str(BASE_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project metadata
    PROJECT_NAME: str = "VERIFAI"
    PROJECT_VERSION: str = "1.0.0-prototype"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="development, testing, production")
    DEBUG: bool = True

    # Security & Cryptography
    # WARNING: Override SECRET_KEY in production via environment variable!
    SECRET_KEY: str = Field(
        default="verifai-dev-insecure-secret-key-change-in-production-32chars!",
        description="JWT signing secret key"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for dev prototype
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AES-256-GCM Vault Master Key (Must be 32 bytes in hex, i.e., 64 chars)
    # WARNING: Override VAULT_MASTER_KEY_HEX in production via environment variable!
    VAULT_MASTER_KEY_HEX: str = Field(
        default="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        description="Hex-encoded 32-byte key for AES-256-GCM vault encryption"
    )

    # Vault Storage Directory
    VAULT_STORAGE_PATH: str = str(BASE_DIR / "vault_storage")

    # Database Configuration (Dual-Mode: SQLite fallback or PostgreSQL)
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{BASE_DIR / 'verifai.db'}",
        description="Async SQLAlchemy database connection string"
    )

    # Graph Configuration (Dual-Mode: Local NetworkX fallback or Neo4j Bolt)
    USE_LOCAL_GRAPH: bool = True
    NEO4J_URI: Optional[str] = "bolt://localhost:7687"
    NEO4J_USER: Optional[str] = "neo4j"
    NEO4J_PASSWORD: Optional[str] = None

    # AI Model Providers
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "mock"  # "gemini", "openai", or "mock"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


settings = Settings()
