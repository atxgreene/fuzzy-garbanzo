# atxgreene.io

Personal portfolio site for Austin Greene. Single-page, static, zero build step.

## Files

- `index.html` — the whole site in one file (HTML + inline CSS)
- `favicon.svg` — the little orange "a" tile
- `404.html` — fallback page for missing URLs
- `robots.txt` — allow crawlers, point to sitemap
- `sitemap.xml` — single-URL sitemap

Fonts (Fraunces + JetBrains Mono) load from Google Fonts at runtime. No build tooling, no package.json, no framework.

## Local preview

```bash
cd atxgreene.io
python3 -m http.server 8000
# then open http://localhost:8000
```

Or just double-click `index.html` in a file manager.

## Deploy options

### Cloudflare Pages (recommended — fast, free, nice custom domain UX)

1. Push this folder to a GitHub repo (e.g. `atxgreene/atxgreene.io`)
2. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git
3. Framework preset: **None**. Build command: **(blank)**. Build output directory: **`/`**
4. Deploy, then attach `atxgreene.io` as a custom domain

### GitHub Pages

1. Push this folder to `atxgreene/atxgreene.github.io` (repo must be named exactly that for a user site), OR to any repo and enable Pages from the Settings tab
2. Settings → Pages → Source: `main` branch, `/ (root)`
3. Add a `CNAME` file with the line `atxgreene.io` and point DNS A/AAAA records at GitHub's Pages IPs

### Vercel / Netlify

Drag the folder into the dashboard. No config needed — both will serve it as-is.

## Editing the projects

All project cards live in `index.html` under `<section id="work">`. Each is an `<article class="card">` with:

- `.cover` — coloured block at the top. Swap the class (`.c-mnemosyne`, `.c-tugboat`, etc.) to change the palette, or add your own by copying the `.c-*` CSS pattern and picking a new color variable (`--hot`, `--lime`, `--blue`, `--lilac`).
- `.body h3` — project name
- `.body .desc` — 1–2 sentence description
- `.body .tags` — tech stack chips
- `.body .cta` — GitHub / case study links

Cards size themselves with grid spans: `.card.big` = 4 cols, `.card` = 3 cols, `.card.small` = 2 cols (out of 6). Mix them up to get the magazine-style layout.

## Adding a new project

Copy any `<article>` block, change the `.cover` color class, name, description, tags, and links. Bump the `06 / projects` counter in the section head.

## Adding a new writing item

The `#writing` list is just `<li>` entries with a date on the left, title + description in the middle, and link on the right. Follow the pattern.

## Notes

- Color tokens live in `:root` at the top of the `<style>` block. Change one line, every card using it updates.
- Layout is responsive: 2-col below 900px, 1-col below 520px.
- Prefers-reduced-motion is respected — the pulsing status dot will stop for users who set that preference.
- Open Graph + Twitter meta are set up. Drop an `og.png` (1200×630) in the folder if you want rich link previews.
