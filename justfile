install:
    mise install
    mise x -- pnpm install --frozen-lockfile
    mise x -- uv sync --all-packages

dev:
    pnpm run dev

fetch-loj:
    uv run megajuggler loj fetch

parse-loj:
    uv run megajuggler loj parse

data:
    uv run megajuggler data build

schema:
    uv run megajuggler schema export

check:
    pnpm run check
    pnpm run typecheck
    pnpm run test

fix:
    pnpm exec biome check --write .
    uv run ruff check --fix .
    uv run ruff format .
