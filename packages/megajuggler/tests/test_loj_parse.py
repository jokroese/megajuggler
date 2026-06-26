from __future__ import annotations

from pathlib import Path

from megajuggler.sources.loj.parse import LOJ_BASE_URL, parse_homepage_links, parse_trick_page

FIXTURES = Path(__file__).parent / "fixtures" / "loj"


def test_parse_homepage_links() -> None:
    html = (FIXTURES / "Home.html").read_text(encoding="utf-8")
    links = parse_homepage_links(html, base_url=LOJ_BASE_URL)
    assert len(links) > 100

    als_slide = next(link for link in links if link.title == "Al's Slide")
    assert als_slide.href == "Tricks/3balltricks/Al'sSlide.html"
    assert str(als_slide.url) == "https://libraryofjuggling.com/Tricks/3balltricks/Al'sSlide.html"
    assert als_slide.category == "Three Ball Patterns"
    assert als_slide.object_count == 3

    six_ball_fountain = next(link for link in links if link.title == "Six Ball Fountain")
    assert six_ball_fountain.object_count == 6


def test_parse_trick_page() -> None:
    html = (FIXTURES / "Al'sSlide.html").read_text(encoding="utf-8")
    trick = parse_trick_page(
        html,
        source_url="https://libraryofjuggling.com/Tricks/3balltricks/Al'sSlide.html",
        relative_path="Tricks/3balltricks/Al'sSlide.html",
    )
    assert trick.title == "Al's Slide"
    assert trick.siteswap == "(4x,2x)(2,4x)*"
    assert trick.difficulty == 4
    assert len(trick.prerequisites) == 1
    assert trick.prerequisites[0].title == "Infinity"
    assert trick.prerequisites[0].href == "Infinity.html"
    assert len(trick.tutorials) == 1
    assert trick.tutorials[0].title == "Idiosensory (second trick)"
    assert len(trick.media) == 4
    assert trick.media[0].src == "../../JugglingGifs/3balltricks/alsslide.gif"
    assert trick.description_text is not None
    assert "Al's Slide is a three ball pattern" in trick.description_text
