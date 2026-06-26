from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """Find the repository root by walking upwards to pyproject.toml + package.json."""
    current = (start or Path.cwd()).resolve()
    for path in [current, *current.parents]:
        if (path / "pyproject.toml").exists() and (path / "package.json").exists():
            return path
    msg = f"Could not find repo root from {current}"
    raise RuntimeError(msg)


def data_dir() -> Path:
    return find_repo_root() / "data"


def raw_loj_dir() -> Path:
    return data_dir() / "raw" / "loj"


def interim_loj_dir() -> Path:
    return data_dir() / "interim" / "loj"


def public_data_dir() -> Path:
    return data_dir() / "public"


def web_static_data_dir() -> Path:
    return find_repo_root() / "apps" / "web" / "static" / "data"
