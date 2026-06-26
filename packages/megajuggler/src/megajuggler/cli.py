from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from megajuggler.export.public_data import build_public_tricks
from megajuggler.sources.loj.export import parse_cached_homepage, parse_cached_tricks
from megajuggler.sources.loj.fetch import fetch_all_tricks, fetch_homepage

app = typer.Typer(help="Megajuggler data tooling.")

loj_app = typer.Typer(help="Library of Juggling source commands.")
data_app = typer.Typer(help="Canonical data build commands.")
schema_app = typer.Typer(help="Schema export commands.")

app.add_typer(loj_app, name="loj")
app.add_typer(data_app, name="data")
app.add_typer(schema_app, name="schema")

RawDirOption = Annotated[
    Path | None,
    typer.Option(help="Raw Library of Juggling cache directory."),
]
OutputDirOption = Annotated[
    Path | None,
    typer.Option(help="Output directory."),
]
InterimOutputDirOption = Annotated[
    Path | None,
    typer.Option(help="Interim output directory."),
]
ForceOption = Annotated[
    bool,
    typer.Option(help="Overwrite cached files."),
]
DelaySecondsOption = Annotated[
    float,
    typer.Option(help="Delay between trick-page requests."),
]
CopyToWebStaticOption = Annotated[
    bool,
    typer.Option(help="Copy generated public data into apps/web/static/data."),
]


@loj_app.command("fetch-home")
def loj_fetch_home(
    output_dir: OutputDirOption = None,
    force: ForceOption = False,
) -> None:
    """Fetch the Library of Juggling homepage into data/raw."""
    output_path = fetch_homepage(output_dir=output_dir, force=force)
    typer.echo(f"Wrote {output_path}")


@loj_app.command("fetch")
def loj_fetch(
    output_dir: OutputDirOption = None,
    delay_seconds: DelaySecondsOption = 0.25,
    force: ForceOption = False,
) -> None:
    """Fetch the Library of Juggling homepage and all linked trick pages."""
    paths = fetch_all_tricks(
        output_dir=output_dir,
        delay_seconds=delay_seconds,
        force=force,
    )
    typer.echo(f"Cached {len(paths)} trick pages")


@loj_app.command("parse-home")
def loj_parse_home(
    raw_dir: RawDirOption = None,
    output_dir: InterimOutputDirOption = None,
) -> None:
    """Parse cached Library of Juggling homepage links."""
    output_path = parse_cached_homepage(raw_dir=raw_dir, output_dir=output_dir)
    typer.echo(f"Wrote {output_path}")


@loj_app.command("parse")
def loj_parse(
    raw_dir: RawDirOption = None,
    output_dir: InterimOutputDirOption = None,
) -> None:
    """Parse cached Library of Juggling trick pages."""
    links_path = parse_cached_homepage(raw_dir=raw_dir, output_dir=output_dir)
    tricks_path = parse_cached_tricks(raw_dir=raw_dir, output_dir=output_dir)
    typer.echo(f"Wrote {links_path}")
    typer.echo(f"Wrote {tricks_path}")


@data_app.command("build")
def data_build(
    copy_to_web_static: CopyToWebStaticOption = True,
) -> None:
    """Build validated public JSON data."""
    output_path = build_public_tricks(copy_to_web_static=copy_to_web_static)
    typer.echo(f"Wrote {output_path}")


@schema_app.command("export")
def schema_export() -> None:
    """Export canonical JSON Schema."""
    typer.echo("TODO: export JSON Schema")


if __name__ == "__main__":
    app()
