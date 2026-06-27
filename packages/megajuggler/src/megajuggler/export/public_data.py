from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, cast

from pydantic import HttpUrl

from megajuggler.paths import interim_loj_dir, public_data_dir, web_static_data_dir
from megajuggler.schema.models import Trick


def slugify(value: str) -> str:
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"['\u2019]", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def build_public_tricks(
    *,
    interim_dir: Path | None = None,
    output_dir: Path | None = None,
    copy_to_web_static: bool = True,
) -> Path:
    interim_dir = interim_dir or interim_loj_dir()
    output_dir = output_dir or public_data_dir()

    raw_tricks_path = interim_dir / "tricks.json"
    raw_tricks = json.loads(raw_tricks_path.read_text(encoding="utf-8"))

    title_to_id = {trick["title"]: slugify(trick["title"]) for trick in raw_tricks}
    tricks: list[Trick] = []
    for raw in raw_tricks:
        prerequisites = [
            title_to_id[prereq["title"]]
            for prereq in raw.get("prerequisites", [])
            if prereq["title"] in title_to_id
        ]
        media = raw.get("media", [])
        tutorials = raw.get("tutorials", [])
        tricks.append(
            Trick(
                id=slugify(raw["title"]),
                title=raw["title"],
                source_url=raw["source_url"],
                category=raw.get("category"),
                object_count=raw.get("object_count") or infer_object_count(raw),
                siteswap=raw.get("siteswap"),
                difficulty=raw.get("difficulty"),
                prerequisites=prerequisites,
                animation_url=first_media_url(media),
                tutorial_urls=tutorial_urls(tutorials),
                description_preview=make_description_preview(raw.get("description_text")),
            )
        )

    tricks.sort(key=lambda trick: (trick.object_count or 999, trick.difficulty or 999, trick.title))

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "tricks.json"
    output_path.write_text(
        json.dumps([trick.model_dump(mode="json") for trick in tricks], indent=2) + "\n",
        encoding="utf-8",
    )

    if copy_to_web_static:
        web_dir = web_static_data_dir()
        web_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(output_path, web_dir / "tricks.json")

    return output_path


def infer_object_count(raw: dict[str, Any]) -> int | None:
    relative_path = raw.get("relative_path") or ""
    match = re.search(r"/(\d+)balltricks/", f"/{relative_path}")
    if match:
        return int(match.group(1))
    return None


def first_media_url(media: Any) -> str | None:
    if not isinstance(media, list) or not media:
        return None
    if not isinstance(media[0], dict):
        return None
    item = cast(dict[str, Any], media[0])
    url = item.get("url")
    return url if isinstance(url, str) else None


def tutorial_urls(tutorials: Any) -> list[HttpUrl | str]:
    if not isinstance(tutorials, list):
        return []
    urls: list[HttpUrl | str] = []
    for item in cast(list[Any], tutorials):
        if not isinstance(item, dict):
            continue
        tutorial = cast(dict[str, Any], item)
        url = tutorial.get("url")
        if isinstance(url, str):
            urls.append(url)
    return urls


def make_description_preview(value: Any, *, max_length: int = 220) -> str | None:
    if not isinstance(value, str):
        return None
    preview = re.sub(r"\s+", " ", value).strip()
    if not preview:
        return None
    if len(preview) <= max_length:
        return preview
    return preview[:max_length].rsplit(" ", maxsplit=1)[0] + "\u2026"
