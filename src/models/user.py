"""User data models."""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserRole(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class UserCreate(BaseModel):
    """Model for creating a new user."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)
    role: UserRole = Field(default=UserRole.VIEWER)

    # OAuth info
    google_id: Optional[str] = None
    microsoft_id: Optional[str] = None

    # Preferences
    preferences: Dict[str, Any] = Field(default_factory=dict)


class User(BaseModel):
    """Complete user model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID

    email: EmailStr
    full_name: str
    role: UserRole

    # OAuth info
    google_id: Optional[str] = None
    microsoft_id: Optional[str] = None

    # Connected accounts
    google_tokens: Optional[Dict[str, Any]] = Field(None, exclude=True)
    notion_token: Optional[str] = Field(None, exclude=True)

    # Preferences
    preferences: Dict[str, Any] = Field(default_factory=dict)

    # Status
    is_active: bool = True
    is_verified: bool = False

    # Usage stats
    memories_count: int = 0
    last_active_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserResponse(BaseModel):
    """User response model for API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole

    # Connected services
    has_google_connection: bool = False
    has_notion_connection: bool = False

    # Preferences
    preferences: Dict[str, Any]

    # Status
    is_active: bool
    is_verified: bool

    # Usage stats
    memories_count: int
    last_active_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime


class UserAuth(BaseModel):
    """User authentication model."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: Optional[str] = None
    oauth_token: Optional[str] = None
    oauth_provider: Optional[str] = Field(None, pattern="^(google|microsoft)$")