from __future__ import annotations

import typer

app = typer.Typer(help="Megajuggler data tooling.")

loj_app = typer.Typer(help="Library of Juggling source commands.")
data_app = typer.Typer(help="Canonical data build commands.")
schema_app = typer.Typer(help="Schema export commands.")

app.add_typer(loj_app, name="loj")
app.add_typer(data_app, name="data")
app.add_typer(schema_app, name="schema")


@loj_app.command("fetch")
def loj_fetch() -> None:
    """Fetch Library of Juggling pages into data/raw."""
    typer.echo("TODO: fetch Library of Juggling pages")


@loj_app.command("parse")
def loj_parse() -> None:
    """Parse cached Library of Juggling pages into data/interim."""
    typer.echo("TODO: parse Library of Juggling pages")


@data_app.command("build")
def data_build() -> None:
    """Build validated public JSON data."""
    typer.echo("TODO: build data/public")


@schema_app.command("export")
def schema_export() -> None:
    """Export canonical JSON Schema."""
    typer.echo("TODO: export JSON Schema")


if __name__ == "__main__":
    app()
