from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

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
        tricks.append(
            Trick(
                id=slugify(raw["title"]),
                title=raw["title"],
                source_url=raw["source_url"],
                object_count=infer_object_count(raw),
                siteswap=raw.get("siteswap"),
                difficulty=raw.get("difficulty"),
                prerequisites=prerequisites,
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
