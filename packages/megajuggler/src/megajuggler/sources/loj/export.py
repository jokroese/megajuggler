from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from megajuggler.paths import interim_loj_dir, raw_loj_dir
from megajuggler.sources.loj.fetch import url_to_cache_path
from megajuggler.sources.loj.parse import LOJ_BASE_URL, parse_homepage_links, parse_trick_page


def parse_cached_homepage(*, raw_dir: Path | None = None, output_dir: Path | None = None) -> Path:
    raw_dir = raw_dir or raw_loj_dir()
    output_dir = output_dir or interim_loj_dir()

    homepage_path = raw_dir / "Home.html"
    html = homepage_path.read_text(encoding="utf-8")
    links = parse_homepage_links(html, base_url=LOJ_BASE_URL)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "links.json"
    output_path.write_text(
        json.dumps([link.model_dump(mode="json") for link in links], indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def parse_cached_tricks(*, raw_dir: Path | None = None, output_dir: Path | None = None) -> Path:
    raw_dir = raw_dir or raw_loj_dir()
    output_dir = output_dir or interim_loj_dir()

    homepage_path = raw_dir / "Home.html"
    html = homepage_path.read_text(encoding="utf-8")
    links = parse_homepage_links(html, base_url=LOJ_BASE_URL)

    tricks: list[dict[str, Any]] = []
    for link in links:
        relative_cache_path = url_to_cache_path(str(link.url), base_url=LOJ_BASE_URL)
        html_path = raw_dir / relative_cache_path
        if not html_path.exists():
            continue
        trick = parse_trick_page(
            html_path.read_text(encoding="utf-8"),
            source_url=str(link.url),
            relative_path=str(relative_cache_path),
        )
        trick_data = trick.model_dump(mode="json")
        trick_data["category"] = link.category
        trick_data["object_count"] = link.object_count
        tricks.append(trick_data)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "tricks.json"
    output_path.write_text(json.dumps(tricks, indent=2) + "\n", encoding="utf-8")
    return output_path
