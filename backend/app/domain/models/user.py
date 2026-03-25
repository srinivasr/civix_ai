"""User model for SQLite-backed authentication."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """Represents an authenticated user (booth official or government official)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = Field(default="official")  # "booth" or "official"
    display_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
