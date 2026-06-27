# megajuggler

Python data tooling for Megajuggler.

## Requirements

Building public media requires `ffmpeg` on `PATH`. Library of Juggling GIFs are cached in `data/raw/loj-media` and converted to WebM plus MP4 during `data build`.

## Commands

```bash
uv run megajuggler loj fetch
uv run megajuggler loj parse
uv run megajuggler data build
uv run megajuggler schema export
```
