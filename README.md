# atxgreene.com

Personal portfolio site for Austin Greene. Single-page, static, zero build step.
ATXGreene brand (Midnight Navy + Electric Teal, phoenix mark) with a generative
constellation background, hero embers, and a **live "from GitHub" feed** that
auto-syncs recent repositories at page load.

## Files

- `index.html` — the whole site in one file (HTML + inline CSS + a small vanilla JS block)
- `favicon.svg` — the little tile icon
- `404.html` — fallback page for missing URLs
- `robots.txt` — allow crawlers, point to sitemap
- `sitemap.xml` — single-URL sitemap
- `CNAME` — custom domain for GitHub Pages (`atxgreene.com`)
- `.github/workflows/deploy.yml` — auto-deploys `main` to GitHub Pages

Fonts (Space Grotesk display + Inter body + IBM Plex Mono) load from Google Fonts at
runtime, following the ATXGreene brand. No build tooling, no package.json, no framework.

## Local preview

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Or just double-click `index.html` in a file manager.

## Deploy — GitHub Pages (current setup)

1. Push to the `main` branch.
2. Repo → **Settings → Pages → Source: GitHub Actions**.
3. The included workflow (`.github/workflows/deploy.yml`) builds and deploys on every push to `main`.
4. The `CNAME` file already requests `atxgreene.com`. Point DNS at GitHub:
   - Apex (`atxgreene.com`): four `A` records → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` (and the matching `AAAA` records if you want IPv6).
   - `www` (optional): `CNAME` → `atxgreene.github.io`.
5. In **Settings → Pages**, confirm the custom domain and tick **Enforce HTTPS** once the cert provisions.

## The live GitHub feed

The `#live` section renders cards from `https://api.github.com/users/atxgreene/repos`
at page load — newest-pushed first, forks/archived/featured repos filtered out, top 6 shown.

- **No key needed.** Uses the unauthenticated GitHub API. Results are cached in
  `localStorage` for 1 hour to stay well under the 60-requests/hour limit.
- **Graceful fallback.** If GitHub is rate-limited or offline, the section shows a link
  to the profile instead of breaking.
- **Tuning** (top of the `<script>` block): `GH_USER`, the `FEATURED` skip-list
  (repos already shown in *selected work*), `CACHE_TTL`, and the `.slice(0, 6)` count.

## Editing the curated projects

The hand-picked cards live in `index.html` under `<section id="work">`. Each is an
`<article class="card">` with:

- `.cover` — gradient block at the top. Swap the class (`.c-mnemosyne`, `.c-tugboat`, …)
  to change the palette, or add your own `.c-*` rule using the color tokens
  (`--gold`, `--hot`, `--lime`, `--blue`, `--lilac`).
- `.body h3` — project name
- `.body .desc` — 1–2 sentence description
- `.body .tags` — tech stack chips
- `.body .cta` — GitHub / case study links

Cards size with grid spans: `.card.big` = 4 cols, `.card` = 3 cols, `.card.small` = 2 cols
(out of 6). Mix them for the magazine layout.

## Notes

- Color tokens live in `:root` at the top of the `<style>` block — change one line, every
  card using it updates.
- Layout is responsive: 2-col below 900px, 1-col below 520px.
- `prefers-reduced-motion` is respected — the constellation/embers render a static frame
  and all reveal, beam, marquee, and pulse animations stop.
- Hero embers only run above 760px; the constellation pauses on hidden tabs.
- Open Graph + Twitter meta are set; `og.png` (1200×630) ships at the repo root for rich
  link previews (`https://atxgreene.com/og.png`).
