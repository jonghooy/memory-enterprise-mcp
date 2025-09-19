"""Tenant (Organization) data models."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class TenantCreate(BaseModel):
    """Model for creating a new tenant."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    description: Optional[str] = None

    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict)

    # Limits
    max_users: int = Field(default=50)
    max_memories_per_user: int = Field(default=10000)
    max_storage_gb: int = Field(default=100)


class Tenant(BaseModel):
    """Complete tenant model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    slug: str
    description: Optional[str] = None

    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict)

    # Limits
    max_users: int
    max_memories_per_user: int
    max_storage_gb: int

    # Usage stats
    current_users: int = 0
    current_memories: int = 0
    current_storage_gb: float = 0.0

    # Pinecone namespace
    vector_namespace: str = Field(description="Pinecone namespace for this tenant")

    # Status
    is_active: bool = True
    is_trial: bool = True
    trial_ends_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TenantResponse(BaseModel):
    """Tenant response model for API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: Optional[str] = None

    settings: Dict[str, Any]

    # Usage stats
    current_users: int
    current_memories: int
    current_storage_gb: float

    # Limits
    max_users: int
    max_memories_per_user: int
    max_storage_gb: int

    # Status
    is_active: bool
    is_trial: bool
    trial_ends_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime