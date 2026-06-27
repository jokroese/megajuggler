# megajuggler

Monorepo for juggling data tooling and the public web app.

```txt
apps/web                 SvelteKit frontend
packages/megajuggler     Python scraping, ingest, schema, export tooling
data/public              generated frontend data
```

## Media pipeline

megajuggler loj fetch caches Library of Juggling trick pages and animation GIFs.
megajuggler data build converts cached GIFs into WebM and MP4 loops for the web app, while keeping a local GIF fallback.

The conversion step requires ffmpeg on PATH.
