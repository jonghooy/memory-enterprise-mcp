"""Memory data models using Pydantic v2."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class MemoryType(str, Enum):
    """Types of memories."""

    NOTE = "note"
    DOCUMENT = "document"
    CONVERSATION = "conversation"
    CODE = "code"
    TASK = "task"
    MEETING = "meeting"
    INSIGHT = "insight"


class MemoryCreate(BaseModel):
    """Model for creating a new memory."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    type: MemoryType = Field(default=MemoryType.NOTE)
    source_id: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    entities: List[str] = Field(default_factory=list, description="List of entity names referenced")

    # Wiki-link support
    wiki_links: List[str] = Field(
        default_factory=list,
        description="List of [[entity]] links found in content"
    )

    # External references
    external_url: Optional[str] = None
    external_id: Optional[str] = Field(None, description="ID in external system (Google Docs, Notion, etc.)")


class MemoryUpdate(BaseModel):
    """Model for updating an existing memory."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    type: Optional[MemoryType] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    entities: Optional[List[str]] = None
    wiki_links: Optional[List[str]] = None


class Memory(BaseModel):
    """Complete memory model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    user_id: UUID

    title: str
    content: str
    type: MemoryType
    source_id: Optional[UUID] = None

    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    entities: List[str] = Field(default_factory=list)
    wiki_links: List[str] = Field(default_factory=list)

    external_url: Optional[str] = None
    external_id: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: Optional[datetime] = None

    # Vector search
    embedding: Optional[List[float]] = Field(None, exclude=True)
    embedding_model: Optional[str] = None

    # Indexing status
    is_indexed: bool = False
    index_error: Optional[str] = None
    indexed_at: Optional[datetime] = None


class MemoryResponse(BaseModel):
    """Memory response model for API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    type: MemoryType
    source_id: Optional[UUID] = None

    tags: List[str]
    metadata: Dict[str, Any]
    entities: List[str]
    wiki_links: List[str]

    external_url: Optional[str] = None
    external_id: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    accessed_at: Optional[datetime] = None

    # Relationships
    backlinks_count: int = 0
    related_memories: List[UUID] = Field(default_factory=list)

    # Search relevance
    relevance_score: Optional[float] = None


class MemoryFilter(BaseModel):
    """Filters for memory search."""

    model_config = ConfigDict(str_strip_whitespace=True)

    type: Optional[MemoryType] = None
    tags: Optional[List[str]] = None
    source_id: Optional[UUID] = None
    entities: Optional[List[str]] = None

    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None

    # Metadata filters
    metadata_filters: Dict[str, Any] = Field(default_factory=dict)

    # Advanced filters
    has_wiki_links: Optional[bool] = None
    is_indexed: Optional[bool] = None
    external_source: Optional[str] = None


class MemorySearch(BaseModel):
    """Search parameters for memories."""

    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(..., min_length=1, max_length=1000)

    # Search options
    search_type: str = Field(
        default="hybrid",
        pattern="^(semantic|keyword|hybrid)$"
    )

    # Filters
    filters: Optional[MemoryFilter] = None

    # Pagination
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    # Sorting
    sort_by: str = Field(
        default="relevance",
        pattern="^(relevance|created_at|updated_at|accessed_at)$"
    )
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

    # Advanced options
    include_backlinks: bool = False
    include_related: bool = False
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)