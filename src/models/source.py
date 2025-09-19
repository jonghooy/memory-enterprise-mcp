"""Source data models for external integrations."""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class SourceType(str, Enum):
    """Types of external sources."""

    GOOGLE_DOCS = "google_docs"
    NOTION = "notion"
    SLACK = "slack"
    LOCAL_FILE = "local_file"
    WEB_URL = "web_url"
    API = "api"
    MANUAL = "manual"


class SourceCreate(BaseModel):
    """Model for creating a new source."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=200)
    type: SourceType
    description: Optional[str] = None

    # Connection details
    connection_config: Dict[str, Any] = Field(default_factory=dict)

    # Sync settings
    auto_sync: bool = False
    sync_frequency_minutes: Optional[int] = Field(None, ge=5)

    # Access control
    is_shared: bool = False  # If True, available to all users in tenant


class Source(BaseModel):
    """Complete source model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    user_id: UUID  # Owner of the source

    name: str
    type: SourceType
    description: Optional[str] = None

    # Connection details
    connection_config: Dict[str, Any] = Field(default_factory=dict)

    # Sync settings
    auto_sync: bool
    sync_frequency_minutes: Optional[int] = None
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None

    # Sync status
    sync_status: str = Field(default="idle")  # idle, syncing, error
    sync_error: Optional[str] = None
    memories_synced: int = 0

    # Access control
    is_shared: bool
    is_active: bool = True

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SourceResponse(BaseModel):
    """Source response model for API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: SourceType
    description: Optional[str] = None

    # Sync settings
    auto_sync: bool
    sync_frequency_minutes: Optional[int] = None
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None

    # Sync status
    sync_status: str
    sync_error: Optional[str] = None
    memories_synced: int

    # Access control
    is_shared: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime