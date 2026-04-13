"""Data models for the todo application."""

from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class TodoItem(BaseModel):
    """A todo item with all fields."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    priority: Literal["low", "medium", "high"] = "medium"


class TodoCreate(BaseModel):
    """Model for creating a new todo."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: Literal["low", "medium", "high"] = "medium"


class TodoUpdate(BaseModel):
    """Model for updating an existing todo."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    completed: bool | None = None
    priority: Literal["low", "medium", "high"] | None = None
