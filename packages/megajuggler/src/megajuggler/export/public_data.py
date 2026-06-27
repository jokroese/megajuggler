from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, NamedTuple, cast

from pydantic import HttpUrl

from megajuggler.paths import (
    interim_loj_dir,
    public_data_dir,
    public_media_dir,
    raw_loj_media_dir,
    web_static_data_dir,
    web_static_media_dir,
)
from megajuggler.schema.models import Trick
from megajuggler.sources.loj.fetch import url_to_media_cache_path


class AnimationMedia(NamedTuple):
    gif_url: str | None
    webm_url: str | None
    mp4_url: str | None


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
    convert_media: bool = True,
    media_input_dir: Path | None = None,
    media_output_dir: Path | None = None,
) -> Path:
    interim_dir = interim_dir or interim_loj_dir()
    output_dir = output_dir or public_data_dir()
    media_input_dir = media_input_dir or raw_loj_media_dir()
    media_output_dir = media_output_dir or public_media_dir()

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
        source_animation_url = first_media_url(media)
        animation_media = (
            build_animation_media(
                title=raw["title"],
                source_url=source_animation_url,
                input_dir=media_input_dir,
                output_dir=media_output_dir,
            )
            if convert_media and source_animation_url
            else AnimationMedia(gif_url=None, webm_url=None, mp4_url=None)
        )
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
                animation_gif_url=animation_media.gif_url,
                animation_webm_url=animation_media.webm_url,
                animation_mp4_url=animation_media.mp4_url,
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
        if media_output_dir.exists():
            web_media_dir = web_static_media_dir()
            if web_media_dir.exists():
                shutil.rmtree(web_media_dir)
            shutil.copytree(media_output_dir, web_media_dir)

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


def build_animation_media(
    *,
    title: str,
    source_url: str,
    input_dir: Path,
    output_dir: Path,
) -> AnimationMedia:
    source_path = input_dir / url_to_media_cache_path(source_url)
    if not source_path.exists():
        msg = f"Missing cached animation media: {source_path}"
        raise FileNotFoundError(msg)

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = slugify(title)
    gif_path = output_dir / f"{stem}.gif"
    webm_path = output_dir / f"{stem}.webm"
    mp4_path = output_dir / f"{stem}.mp4"

    if needs_update(source_path, gif_path):
        shutil.copyfile(source_path, gif_path)

    convert_gif_to_webm(source_path=source_path, output_path=webm_path)
    convert_gif_to_mp4(source_path=source_path, output_path=mp4_path)

    return AnimationMedia(
        gif_url=public_media_url(gif_path),
        webm_url=public_media_url(webm_path),
        mp4_url=public_media_url(mp4_path),
    )


def public_media_url(path: Path) -> str:
    return f"/data/media/loj/{path.name}"


def needs_update(source_path: Path, output_path: Path) -> bool:
    return not output_path.exists() or output_path.stat().st_mtime < source_path.stat().st_mtime


def convert_gif_to_webm(*, source_path: Path, output_path: Path) -> None:
    if not needs_update(source_path, output_path):
        return

    run_ffmpeg(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source_path),
            "-an",
            "-vf",
            "fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v",
            "libvpx-vp9",
            "-b:v",
            "0",
            "-crf",
            "36",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
    )


def convert_gif_to_mp4(*, source_path: Path, output_path: Path) -> None:
    if not needs_update(source_path, output_path):
        return

    run_ffmpeg(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source_path),
            "-an",
            "-vf",
            "fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v",
            "libx264",
            "-crf",
            "28",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )


def run_ffmpeg(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as caught:
        msg = "ffmpeg is required to convert Library of Juggling GIFs to WebM/MP4."
        raise RuntimeError(msg) from caught
