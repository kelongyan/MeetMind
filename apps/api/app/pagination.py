"""Shared pagination primitives for all list endpoints."""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


class PaginatedResponse[T](BaseModel):
    """Generic wrapper for paginated list responses."""

    items: list[T]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
