install:
    mise install
    mise x -- pnpm install --frozen-lockfile
    mise x -- uv sync --all-packages

dev:
    mise x -- pnpm run dev

fetch-loj:
    mise x -- uv run megajuggler loj fetch

parse-loj:
    mise x -- uv run megajuggler loj parse

data:
    mise x -- uv run megajuggler data build

schema:
    mise x -- uv run megajuggler schema export

check:
    mise x -- pnpm run check
    mise x -- pnpm run typecheck
    mise x -- pnpm run test

fix:
    mise x -- pnpm exec biome check --write .
    mise x -- uv run ruff check --fix .
    mise x -- uv run ruff format .
