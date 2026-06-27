from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from megajuggler.export.public_data import (
    build_public_tricks,
    first_media_url,
    make_description_preview,
    slugify,
    tutorial_urls,
)


def test_slugify() -> None:
    assert slugify("Al's Slide") == "als-slide"
    assert slugify("441 (Half-Box)") == "441-half-box"
    assert slugify("Mills Mess Shower") == "mills-mess-shower"


def test_first_media_url() -> None:
    assert first_media_url([{"url": "https://example.com/animation.gif"}]) == (
        "https://example.com/animation.gif"
    )
    assert first_media_url([]) is None
    assert first_media_url([{"src": "animation.gif"}]) is None


def test_tutorial_urls() -> None:
    assert tutorial_urls(
        [
            {"url": "https://example.com/tutorial-one"},
            {"url": "https://example.com/tutorial-two"},
            {"title": "Missing URL"},
        ]
    ) == [
        "https://example.com/tutorial-one",
        "https://example.com/tutorial-two",
    ]


def test_make_description_preview() -> None:
    assert make_description_preview("Short description.") == "Short description."
    assert make_description_preview("  Lots\n\nof    whitespace.  ") == "Lots of whitespace."
    long_preview = make_description_preview("word " * 100, max_length=30)
    assert long_preview is not None
    assert long_preview.endswith("…")
    assert len(long_preview) <= 31


def test_build_public_tricks(tmp_path: Path) -> None:
    interim_dir = tmp_path / "interim"
    output_dir = tmp_path / "public"
    interim_dir.mkdir()
    raw_tricks: list[dict[str, Any]] = [
        {
            "title": "Infinity",
            "source_url": "https://libraryofjuggling.com/Tricks/3balltricks/Infinity.html",
            "relative_path": "Tricks/3balltricks/Infinity.html",
            "category": "Three Ball Patterns",
            "object_count": 3,
            "siteswap": None,
            "difficulty": 2,
            "prerequisites": [],
            "media": [
                {"url": "https://libraryofjuggling.com/JugglingGifs/3balltricks/infinity.gif"}
            ],
            "tutorials": [],
            "description_text": "Infinity is a three ball pattern.",
        },
        {
            "title": "Al's Slide",
            "source_url": "https://libraryofjuggling.com/Tricks/3balltricks/Al'sSlide.html",
            "relative_path": "Tricks/3balltricks/Al'sSlide.html",
            "category": "Three Ball Patterns",
            "object_count": 3,
            "siteswap": "(4x,2x)(2,4x)*",
            "difficulty": 4,
            "prerequisites": [{"title": "Infinity"}],
            "media": [
                {"url": "https://libraryofjuggling.com/JugglingGifs/3balltricks/alsslide.gif"}
            ],
            "tutorials": [{"url": "https://www.youtube.com/watch?v=8C6VjYyqxAg"}],
            "description_text": "Al's Slide is a three ball pattern established by Idiosensory.",
        },
    ]
    (interim_dir / "tricks.json").write_text(json.dumps(raw_tricks), encoding="utf-8")

    output_path = build_public_tricks(
        interim_dir=interim_dir,
        output_dir=output_dir,
        copy_to_web_static=False,
        # This unit test does not create cached GIF fixtures or run ffmpeg.
        convert_media=False,
    )
    tricks = json.loads(output_path.read_text(encoding="utf-8"))

    assert tricks == [
        {
            "id": "infinity",
            "title": "Infinity",
            "source_url": "https://libraryofjuggling.com/Tricks/3balltricks/Infinity.html",
            "category": "Three Ball Patterns",
            "object_count": 3,
            "siteswap": None,
            "difficulty": 2,
            "prerequisites": [],
            "animation_gif_url": None,
            "animation_webm_url": None,
            "animation_mp4_url": None,
            "tutorial_urls": [],
            "description_preview": "Infinity is a three ball pattern.",
        },
        {
            "id": "als-slide",
            "title": "Al's Slide",
            "source_url": "https://libraryofjuggling.com/Tricks/3balltricks/Al'sSlide.html",
            "category": "Three Ball Patterns",
            "object_count": 3,
            "siteswap": "(4x,2x)(2,4x)*",
            "difficulty": 4,
            "prerequisites": ["infinity"],
            "animation_gif_url": None,
            "animation_webm_url": None,
            "animation_mp4_url": None,
            "tutorial_urls": ["https://www.youtube.com/watch?v=8C6VjYyqxAg"],
            "description_preview": "Al's Slide is a three ball pattern established by Idiosensory.",
        },
    ]
