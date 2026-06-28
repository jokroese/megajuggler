from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class Trick(BaseModel):
    id: str
    title: str
    source_url: HttpUrl | str
    object_count: int | None = None
    siteswap: str | None = None
    difficulty: int | None = Field(default=None, ge=1, le=10)
    prerequisites: list[str] = Field(default_factory=list)
    description: str | None = None
