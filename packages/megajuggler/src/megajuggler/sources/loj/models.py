from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class LojLink(BaseModel):
    title: str
    href: str
    url: HttpUrl
    category: str | None = None
    object_count: int | None = None


class LojTutorialLink(BaseModel):
    title: str
    url: HttpUrl | str


class LojMedia(BaseModel):
    kind: str
    src: str
    url: HttpUrl | str
    width: int | None = None
    height: int | None = None


class LojPrerequisite(BaseModel):
    title: str
    href: str | None = None
    url: HttpUrl | str | None = None


class LojTrickPage(BaseModel):
    source_id: str = "library-of-juggling"
    title: str
    source_url: HttpUrl | str
    relative_path: str | None = None
    siteswap: str | None = None
    difficulty: int | None = Field(default=None, ge=1, le=10)
    prerequisites: list[LojPrerequisite] = Field(default_factory=list)
    tutorials: list[LojTutorialLink] = Field(default_factory=list)
    media: list[LojMedia] = Field(default_factory=list)
    description_text: str | None = None
    description_html: str | None = None
