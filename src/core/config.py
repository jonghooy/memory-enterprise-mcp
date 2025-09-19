"""Core configuration for the application."""

from functools import lru_cache
from typing import Optional, List
from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Environment(str, Enum):
    """Application environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class VectorStoreType(str, Enum):
    """Supported vector store types."""

    PINECONE = "pinecone"
    QDRANT = "qdrant"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        case_sensitive=False,
    )

    # Application
    app_name: str = Field(default="memory-agent-enterprise")
    app_version: str = Field(default="0.1.0")
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=1)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/memory_agent"
    )
    database_pool_size: int = Field(default=20)
    database_max_overflow: int = Field(default=10)

    # Redis
    redis_url: str = Field(default="redis://localhost:6380/0")
    redis_password: Optional[str] = None

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6380/1")
    celery_result_backend: str = Field(default="redis://localhost:6380/2")

    # Vector Store
    vector_store_type: VectorStoreType = Field(default=VectorStoreType.QDRANT)

    # Pinecone
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = Field(default="us-east-1")
    pinecone_index_name: str = Field(default="memory-agent-index")

    # Qdrant
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection_name: str = Field(default="memories")
    qdrant_api_key: Optional[str] = None

    # Embedding
    embedding_model: str = Field(default="BAAI/bge-m3")
    embedding_dimension: int = Field(default=1024)
    embedding_batch_size: int = Field(default=32)

    # LLM
    openai_api_key: Optional[str] = None
    llm_model: str = Field(default="gpt-4-turbo-preview")
    llm_temperature: float = Field(default=0.7)
    llm_max_tokens: int = Field(default=2000)

    # OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = Field(
        default="http://localhost:8000/auth/google/callback"
    )

    # Google APIs
    google_docs_scopes: List[str] = Field(
        default=[
            "https://www.googleapis.com/auth/documents.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
    )

    # Notion
    notion_token: Optional[str] = None

    # Security
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-this-in-production"
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_minutes: int = Field(default=1440)

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    cors_allow_credentials: bool = Field(default=True)

    # Rate Limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_period: int = Field(default=60)

    # Monitoring
    prometheus_enabled: bool = Field(default=True)
    sentry_dsn: Optional[str] = None

    # LlamaIndex
    chunk_size: int = Field(default=512)
    chunk_overlap: int = Field(default=50)

    @field_validator("cors_origins", mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("google_docs_scopes", mode='before')
    @classmethod
    def parse_google_scopes(cls, v):
        """Parse Google scopes from string or list."""
        if isinstance(v, str):
            # Remove quotes if present
            v = v.strip('"\'')
            return [scope.strip() for scope in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()