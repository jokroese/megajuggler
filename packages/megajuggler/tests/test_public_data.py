from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from megajuggler.export.public_data import build_public_tricks, slugify


def test_slugify() -> None:
    assert slugify("Al's Slide") == "als-slide"
    assert slugify("441 (Half-Box)") == "441-half-box"
    assert slugify("Mills Mess Shower") == "mills-mess-shower"


def test_build_public_tricks(tmp_path: Path) -> None:
    interim_dir = tmp_path / "interim"
    output_dir = tmp_path / "public"
    interim_dir.mkdir()

    raw_tricks: list[dict[str, Any]] = [
        {
            "title": "Infinity",
            "source_url": "https://libraryofjuggling.com/Tricks/3balltricks/Infinity.html",
            "relative_path": "Tricks/3balltricks/Infinity.html",
            "siteswap": None,
            "difficulty": 2,
            "prerequisites": [],
        },
        {
            "title": "Al's Slide",
            "source_url": "https://libraryofjuggling.com/Tricks/3balltricks/Al'sSlide.html",
            "relative_path": "Tricks/3balltricks/Al'sSlide.html",
            "siteswap": "(4x,2x)(2,4x)*",
            "difficulty": 4,
            "prerequisites": [{"title": "Infinity"}],
        },
    ]
    (interim_dir / "tricks.json").write_text(json.dumps(raw_tricks), encoding="utf-8")

    output_path = build_public_tricks(
        interim_dir=interim_dir,
        output_dir=output_dir,
        copy_to_web_static=False,
    )
    tricks = json.loads(output_path.read_text(encoding="utf-8"))

    assert tricks == [
        {
            "id": "infinity",
            "title": "Infinity",
            "source_url": "https://libraryofjuggling.com/Tricks/3balltricks/Infinity.html",
            "object_count": 3,
            "siteswap": None,
            "difficulty": 2,
            "prerequisites": [],
        },
        {
            "id": "als-slide",
            "title": "Al's Slide",
            "source_url": "https://libraryofjuggling.com/Tricks/3balltricks/Al'sSlide.html",
            "object_count": 3,
            "siteswap": "(4x,2x)(2,4x)*",
            "difficulty": 4,
            "prerequisites": ["infinity"],
        },
    ]
