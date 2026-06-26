from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import PurePosixPath
from typing import cast
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag
from pydantic import HttpUrl

from megajuggler.sources.loj.models import (
    LojLink,
    LojMedia,
    LojPrerequisite,
    LojTrickPage,
    LojTutorialLink,
)

LOJ_BASE_URL = "https://libraryofjuggling.com/"

_OBJECT_COUNTS = {
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
}


def parse_homepage_links(html: str, *, base_url: str = LOJ_BASE_URL) -> list[LojLink]:
    """Parse the Library of Juggling homepage navigation into trick links."""
    soup = BeautifulSoup(html, "html.parser")
    sidebar = soup.select_one("#sidebar")
    if sidebar is None:
        msg = "Could not find #sidebar in Library of Juggling homepage"
        raise ValueError(msg)

    links: list[LojLink] = []
    for heading in sidebar.select("h3"):
        category = clean_text(heading.get_text(" ", strip=True))
        object_count = object_count_from_category(category)
        group = heading.find_next_sibling("ul")
        if group is None:
            continue
        for anchor in group.select("a[href]"):
            href = str(anchor["href"])
            if not is_trick_href(href):
                continue
            links.append(
                LojLink(
                    title=clean_text(anchor.get_text(" ", strip=True)),
                    href=href,
                    url=cast(HttpUrl, urljoin(base_url, href)),
                    category=category,
                    object_count=object_count,
                )
            )
    return dedupe_links(links)


def parse_trick_page(
    html: str,
    *,
    source_url: str,
    relative_path: str | None = None,
) -> LojTrickPage:
    """Parse a Library of Juggling trick page."""
    soup = BeautifulSoup(html, "html.parser")
    title = parse_title(soup)

    siteswap: str | None = None
    difficulty: int | None = None
    prerequisites: list[LojPrerequisite] = []
    for item in soup.select("#otherinfo li"):
        label = parse_info_label(item)
        if label is None:
            continue
        if label == "siteswap":
            siteswap = parse_info_value(item)
        elif label.startswith("difficulty"):
            difficulty = parse_difficulty(parse_info_value(item))
        elif label == "prerequisites":
            prerequisites = parse_prerequisites(item, source_url=source_url)

    tutorials = parse_tutorials(soup, source_url=source_url)
    media = parse_media(soup, source_url=source_url)

    description = soup.select_one("#description")
    description_html = str(description) if description is not None else None
    description_text = (
        clean_text(description.get_text(" ", strip=True)) if description is not None else None
    )

    return LojTrickPage(
        title=title,
        source_url=source_url,
        relative_path=relative_path,
        siteswap=siteswap,
        difficulty=difficulty,
        prerequisites=prerequisites,
        tutorials=tutorials,
        media=media,
        description_text=description_text,
        description_html=description_html,
    )


def parse_title(soup: BeautifulSoup) -> str:
    title = soup.select_one("#Trickname")
    if title is not None:
        return clean_text(title.get_text(" ", strip=True))

    document_title = soup.title.get_text(" ", strip=True) if soup.title is not None else ""
    document_title = re.sub(r"^Library of Juggling\s*-\s*", "", document_title)
    if document_title:
        return clean_text(document_title)

    msg = "Could not parse trick title"
    raise ValueError(msg)


def parse_info_label(item: Tag) -> str | None:
    strong = item.find("strong")
    if strong is None:
        return None
    text = clean_text(strong.get_text(" ", strip=True))
    return text.rstrip(":").lower()


def parse_info_value(item: Tag) -> str | None:
    text = clean_text(item.get_text(" ", strip=True))
    if ":" not in text:
        return None
    value = text.split(":", maxsplit=1)[1].strip()
    return value or None


def parse_difficulty(value: str | None) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def parse_prerequisites(item: Tag, *, source_url: str) -> list[LojPrerequisite]:
    anchors = item.select("a[href]")
    if anchors:
        return [
            LojPrerequisite(
                title=clean_text(anchor.get_text(" ", strip=True)),
                href=str(anchor["href"]),
                url=urljoin(source_url, str(anchor["href"])),
            )
            for anchor in anchors
        ]

    value = parse_info_value(item)
    if not value or value.lower() in {"none", "n/a"}:
        return []
    return [LojPrerequisite(title=value)]


def parse_tutorials(soup: BeautifulSoup, *, source_url: str) -> list[LojTutorialLink]:
    tutorials: list[LojTutorialLink] = []
    tutorial_list = soup.select_one("#tutoriallist")
    if tutorial_list is None:
        return tutorials

    for anchor in tutorial_list.select("a[href]"):
        tutorials.append(
            LojTutorialLink(
                title=clean_text(anchor.get_text(" ", strip=True)),
                url=urljoin(source_url, str(anchor["href"])),
            )
        )
    return tutorials


def parse_media(soup: BeautifulSoup, *, source_url: str) -> list[LojMedia]:
    media: list[LojMedia] = []
    for image in soup.select("img[src]"):
        image_id = image.get("id")
        raw_classes = image.get("class")
        classes = set(raw_classes if isinstance(raw_classes, list) else [])
        if image_id != "jugglinganimation" and "smallanim" not in classes:
            continue
        src = str(image["src"])
        media.append(
            LojMedia(
                kind="animation",
                src=src,
                url=urljoin(source_url, src),
                width=parse_int(image.get("width")),
                height=parse_int(image.get("height")),
            )
        )
    return media


def is_trick_href(href: str) -> bool:
    return href.startswith("Tricks/") and href.endswith(".html")


def object_count_from_category(category: str | None) -> int | None:
    if not category:
        return None
    first_word = category.split(maxsplit=1)[0].lower()
    return _OBJECT_COUNTS.get(first_word)


def dedupe_links(links: Iterable[LojLink]) -> list[LojLink]:
    seen: set[str] = set()
    result: list[LojLink] = []
    for link in links:
        key = canonical_path(str(link.url))
        if key in seen:
            continue
        seen.add(key)
        result.append(link)
    return result


def canonical_path(url: str) -> str:
    parsed = urlparse(url)
    return str(PurePosixPath(parsed.path))


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value))
    except ValueError:
        return None
