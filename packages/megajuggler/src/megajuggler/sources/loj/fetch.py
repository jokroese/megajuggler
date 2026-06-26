from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
import typer
from rich.progress import track

from megajuggler.paths import raw_loj_dir
from megajuggler.sources.loj.parse import LOJ_BASE_URL, parse_homepage_links

USER_AGENT = "megajuggler/0.1 (+https://github.com/jokroese/megajuggler)"


def fetch_homepage(
    *,
    output_dir: Path | None = None,
    base_url: str = LOJ_BASE_URL,
    force: bool = False,
) -> Path:
    output_dir = output_dir or raw_loj_dir()
    output_path = output_dir / "Home.html"
    fetch_url_to_path(
        url=urljoin(base_url, "Home.html"),
        output_path=output_path,
        force=force,
    )
    return output_path


def fetch_all_tricks(
    *,
    output_dir: Path | None = None,
    base_url: str = LOJ_BASE_URL,
    delay_seconds: float = 0.25,
    force: bool = False,
) -> list[Path]:
    output_dir = output_dir or raw_loj_dir()
    homepage_path = fetch_homepage(output_dir=output_dir, base_url=base_url, force=force)
    homepage_html = homepage_path.read_text(encoding="utf-8")
    links = parse_homepage_links(homepage_html, base_url=base_url)

    written: list[Path] = []
    for link in track(links, description="Fetching Library of Juggling tricks"):
        output_path = output_dir / url_to_cache_path(str(link.url), base_url=base_url)
        fetch_url_to_path(
            url=str(link.url),
            output_path=output_path,
            force=force,
        )
        written.append(output_path)
        time.sleep(delay_seconds)

    manifest_path = output_dir / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps([link.model_dump(mode="json") for link in links], indent=2) + "\n",
        encoding="utf-8",
    )
    return written


def fetch_url_to_path(*, url: str, output_path: Path, force: bool = False) -> None:
    if output_path.exists() and not force:
        typer.echo(f"Already cached: {output_path}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(
        timeout=20.0,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        response = client.get(url)
        response.raise_for_status()

    output_path.write_text(response.text, encoding="utf-8")
    typer.echo(f"Fetched {url} -> {output_path}")


def url_to_cache_path(url: str, *, base_url: str = LOJ_BASE_URL) -> Path:
    base_path = urlparse(base_url).path.rstrip("/")
    parsed = urlparse(url)
    relative = parsed.path.removeprefix(base_path).lstrip("/")
    if not relative:
        relative = "Home.html"
    return Path(relative)
