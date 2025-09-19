"""Entity and wiki-link relationship models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class EntityType(str, Enum):
    """Types of entities."""

    PERSON = "person"
    PROJECT = "project"
    CONCEPT = "concept"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    TOOL = "tool"
    UNKNOWN = "unknown"


class Entity(BaseModel):
    """Entity model for wiki-links."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID

    name: str = Field(..., min_length=1, max_length=200)
    normalized_name: str = Field(..., description="Lowercase, normalized for matching")
    type: EntityType = Field(default=EntityType.UNKNOWN)

    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)

    # Stats
    mention_count: int = 0
    backlink_count: int = 0

    # Timestamps
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EntityLink(BaseModel):
    """Link between a memory and an entity."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    memory_id: UUID
    entity_id: UUID
    tenant_id: UUID

    # Link metadata
    position_start: int = Field(..., description="Character position where link starts")
    position_end: int = Field(..., description="Character position where link ends")
    context: str = Field(..., max_length=500, description="Surrounding text context")

    created_at: datetime = Field(default_factory=datetime.utcnow)


class EntityRelation(BaseModel):
    """Relationship between two entities."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID

    source_entity_id: UUID
    target_entity_id: UUID

    relation_type: str = Field(..., description="Type of relationship")
    strength: float = Field(default=1.0, ge=0.0, le=1.0)

    # Evidence
    evidence_memory_ids: List[UUID] = Field(default_factory=list)
    evidence_count: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)