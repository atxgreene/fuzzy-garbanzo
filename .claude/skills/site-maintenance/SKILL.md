---
name: site-maintenance
description: >
  Read this BEFORE editing anything in the fuzzy-garbanzo repo (atxgreene.com).
  Covers the single-file architecture, the hashed Content-Security-Policy that
  WILL silently break every script on the site if you change an inline <script>
  without updating its hash, the mandatory verify.py + PR + CI ship loop, the
  brand system, the site's content map, the gated private "signal desk" feature
  (Bet of the Day / X screener), and the positioning guardrails. Use for any
  change to index.html, the writing/ pages, workflows, service worker, manifest,
  or site assets.
---

# Maintaining atxgreene.com (fuzzy-garbanzo)

This is Austin Greene's personal portfolio + a small **private, gated dashboard**
for friends. It is a few **static HTML files** deployed to GitHub Pages on a custom
domain. There is **no build step, no framework, no bundler, no npm install** —
what's in the repo is what ships.

Read the "Non-negotiables" and "The CSP" sections every time. They are the two
ways to break the live site, and both fail silently (the site still loads, but
JavaScript stops running, or a security header rejects a resource).

---

## Architecture at a glance

- **`index.html`** — atxgreene.com, the main, business-facing page: HTML + one
  inline `<style>` + inline vanilla-JS `<script>` blocks. Also holds the hidden
  signal desk. No external JS/CSS except Google Fonts.
- **`dev/index.html`** — atxgreene.com/dev, the earlier technical portfolio
  (AI-architect framing, full project shelves, constellation/ember effects), kept
  live as-is. It has its **own** hashed CSP and uses root-absolute asset paths
  (`/assets/...`). Don't put business-facing updates here; the root page is primary.
- **`about/index.html`** — a redirect to `/` (old shared links). Leave it alone.
- **`writing/`** — standalone article pages (`mnemosyne-brain.html`,
  `launchpad-civil-mobility.html`) + a PDF. Each is its own self-contained file.
- **`sw.js`** — service worker (offline shell). `manifest.webmanifest` — PWA metadata.
- **`scripts/verify.py`** — the integrity suite. Run it before every commit.
- **`.github/workflows/ci.yml`** — runs `verify.py` on every PR and push to main.
- **`.github/workflows/deploy.yml`** — deploys `main` → GitHub Pages on every push.
- **`CNAME`** — pins the custom domain (`atxgreene.com`). Never delete it.
- Icons/assets: `favicon.png`, `favicon.svg`, `apple-touch-icon.png`, `og.png`,
  `assets/brand/*`. `sitemap.xml`, `robots.txt`, `404.html`. `dev/og.png` is the
  /dev share image.
- **Both `index.html` and `dev/index.html` are in `PAGES` in `verify.py`**, so every
  CSP/re-hash rule below applies to each page separately.

Deploy is automatic: **merge to `main` → GitHub Pages rebuilds → live in ~1–2 min.**

---

## Non-negotiables (do these or you break the site)

1. **Run `python3 scripts/verify.py` before every commit.** It must print
   `All checks passed.` If it fails, fix it before committing. CI runs the exact
   same script and will block the merge.
2. **If you touch ANY inline `<script>` in `index.html`, you must update the CSP
   hashes.** See the next section. This is the #1 cause of a silently broken site.
3. **Ship through a PR, not a direct push to `main`.** Direct pushes skip the CI
   gate and have shipped off-brand content to the live site before. Branch → PR →
   confirm CI green → squash-merge.
4. **Never invent facts** — no fake metrics, credentials, employers, dates, or
   testimonials. If a benchmark isn't measured yet, say "in progress." The site
   is used in real job applications; a claim that contradicts another document
   (or reality) is worse than no claim.
5. **Keep the professional front door clean.** No gambling/casino/mystical/
   "consciousness" language in any publicly visible area. The friends-only tools
   live behind the gate (see "The signal desk").

---

## The CSP — the thing that will bite you

`index.html`'s `<head>` has a **hashed Content-Security-Policy** meta tag. Its
`script-src` directive lists an exact SHA-256 hash for **each** bare inline
`<script>` block. The browser refuses to execute any inline script whose hash
isn't listed. There is no `'unsafe-inline'` for scripts — that's deliberate.

**Consequence:** if you add, remove, or edit *even one character* inside a bare
`<script>…</script>` block, its hash changes, the CSP no longer matches, and the
browser **silently blocks that script** on the live site. The page still loads;
the animations / live feed / signal-desk gate just quietly stop working.

### The workflow whenever you change an inline script

```bash
# 1. Make your script edit in index.html, then:
python3 scripts/verify.py --print-hashes
# 2. Copy the printed 'sha256-...' values into the script-src directive of the
#    Content-Security-Policy <meta> tag in index.html (replace the old set).
# 3. Update the header comment count ("...the N inline script blocks below").
python3 scripts/verify.py            # must say: All checks passed.
```

`verify.py` compares the hashes it computes against the CSP and fails if any is
missing — so as long as it passes, you're safe. CI enforces the same.

### CSP gotchas

- **Only bare `<script>` blocks are hashed.** `verify.py`'s regex is
  `<script>(.*?)</script>` — it ignores any `<script>` with attributes. The
  JSON-LD block (`<script type="application/ld+json">`) is data, not executed
  code, so it is correctly *not* hashed. **Do not add attributes** (`defer`,
  `type="module"`, etc.) to executable inline scripts — the browser would still
  require a hash, but `verify.py` wouldn't manage it, and you'd get a silent block.
- **Other directives gate external resources.** If you add a resource from a new
  host, the CSP will block it until you add the host to the right directive:
  - external **iframe/embed** → add host to `frame-src`
    (currently `https://atxgreene.github.io https://snakepit.dev`)
  - **fetch/XHR** (e.g. the live GitHub feed) → `connect-src`
    (currently `'self' https://api.github.com`)
  - **images** → `img-src` (`'self' data:`), **fonts** → `font-src`
    (`https://fonts.gstatic.com`), **styles** → `style-src`.
- **Daily content edits do NOT touch scripts.** Updating the text of the Bet-of-
  the-Day board, adding a project card, editing prose — none of that changes a
  `<script>` block, so the hashes stay valid. You only re-hash when you edit JS.

---

## The ship loop

```bash
# from a synced main:
git fetch origin main && git checkout -B <branch> origin/main   # or your feature branch

# ...make edits...

python3 scripts/verify.py                 # must pass
git add -A && git commit -m "clear message"
git push -u origin <branch>

# open a PR to main, wait for the "Site integrity" check to go green,
# then squash-merge. Deploy to Pages is automatic on merge.
```

- **Confirm CI is green before merging.** The check is named
  *"Site integrity (CSP hashes, JS syntax, JSON, structure)."*
- After merge, GitHub creates a **squash-merge commit committed by
  `GitHub <noreply@github.com>`** — that commit is GitHub-signed and shows as
  **Verified** on github.com. **Do not amend or rewrite it.** If a hook flags it
  as "unverified," that's a false positive from an email heuristic; leave it.
- To keep a local branch clean after merge: `git fetch origin main &&
  git reset --hard origin/main`.

---

## What verify.py checks (so you know what "green" guarantees)

1. Every bare inline `<script>`'s hash is present in the CSP `script-src`.
2. Every inline script **and** `sw.js` pass `node --check` (JS syntax).
3. `manifest.webmanifest` and the JSON-LD block are valid JSON.
4. Structural tags balance (`div`, `span`, `section`, `article`, `nav`, `aside`,
   `footer`, `script`, `style`, `canvas`) — catches unclosed tags.
5. Referenced local assets (`/favicon.png`, `/og.png`, `/assets/...`, etc.) exist.

It does **not** check brand voice, factual accuracy, or visual layout — those are
on you. A green check means "won't break," not "is good."

---

## Brand system

- **Colors** (CSS vars in `:root`): `--navy #071923`, `--teal #12c9b7`,
  `--teal-deep #0b6e69`, `--orange #f97316`, `--orange-2 #ffb45b`,
  `--bone #f4f1e8`, `--slate #64748b`. Use the existing vars; don't hardcode new hex.
- **Fonts:** Space Grotesk (display/headings), Inter (body), IBM Plex Mono
  (labels/eyebrows/mono). Loaded from Google Fonts.
- **Phoenix mark:** `assets/brand/phoenix-mark.png` is the ONE canonical asset
  (nav, hero, footer, OG). Never redraw or regenerate it — scale, don't reshape.
- **Grid:** 6-column. `.card` = span 3, `.card.full` = span 6.
- **Motion on the main page is restrained on purpose:** scroll reveals, a thin
  accent line between sections, the one-time phoenix ash formation, small hover
  lifts. Don't add constant background animation, particles, cursor effects,
  spinning borders, text-scramble, or 3D tilt there. (`/dev` keeps its original
  effects.) Everything must respect `prefers-reduced-motion`.

---

## Site content map

The main page (`index.html`) is built for a **business visitor first**. Order:

1. **Hero** — "Builder · Problem Solver · Operator" / "I build better ways for
   businesses to work." CTAs *Tell me what's stuck* → `#contact`, *See what I've
   built* → `#work`. Signature: **AUDE FIERI — Dare to become.**
2. **Solve · Build · Advance** (`#framework`).
3. **What I do** (`#services`) — 4 capability cards + "Start with the problem" nudge.
4. **Small business** (`#small-business`) — "You don't need an AI strategy." Keep it.
5. **Selected work** (`#work`) — **4–6 projects max**, each a `<dl class="pbc">`
   with **Problem / Built / Capability**. Currently snakepit.dev, Hermes Play Sheet,
   Mnemosyne, Tugboat, Greene Halls.
6. **Ways to work together** (`#engage`) — Diagnose → Build → Transform → Advise.
   No pricing unless Austin defines it.
7. **About** (`#about`) — identity, the line *"I don't believe every problem needs
   AI. I believe every problem deserves the right tool."*, credibility strip.
8. **The Lab** (`#lab`) — every other project as compact `.lab-item` tiles, plus
   the live GitHub feed (`#live`).
9. **Writing** (`#writing`) → hidden signal desk → **Contact** (`#contact`).

**Positioning:** Austin is a **builder, problem solver, and operator** who helps
businesses figure out what's wrong, build the right thing, and implement it. AI is
one capability, not the identity. Business outcomes before jargon; proof over
claims; restraint over visual noise. If a change would make the site feel like a
generic AI consultancy, don't make it. Keep employer references neutral.

**Brand hierarchy:** ATXGreene / Austin Greene is the public brand. **Bluebonnet is
subordinate** — only "Select consulting engagements are delivered through
Bluebonnet." Don't promote it to a card or headline.

**Contact facts (verified — reuse exactly):** call/text `[removed]`
(`tel:[removed]` / `sms:[removed]`), `atxgreene@gmail.com`,
`https://linkedin.com/in/atxgreene`, `https://github.com/atxgreene`,
`https://atxgreene.substack.com`, `https://x.com/atxgreene`. Never guess handles.

**The contact form has no backend** — it composes a `mailto:`/`sms:` message in
the visitor's own app. Don't wire it to a third-party form service without
Austin's say-so (that needs CSP changes and a privacy decision).

---

## The signal desk (private, gated friends-only tools)

There is a **hidden dashboard** for Austin and friends — currently "Bet of the
Day" (prediction-market sims), with an "X Social Screener" planned. It must stay
**invisible to ordinary/public visitors** (recruiters, hiring managers).

### How the gate works (no server — pure client)

- A floating 🎰 launcher (`.casino-access`) and the board section
  (`.private-signal-desk`, id `#bet-of-day`) are **`display:none` by default.**
- They appear only when `<body>` has the class **`desk-unlocked`**, set by a small
  inline gate script. Unlock happens via any of:
  - **type `desk`** anywhere on the page, or
  - visit **`atxgreene.com/#desk`** (the shareable link for friends), or
  - a prior unlock remembered on that device (`localStorage['atxg-desk'] === '1'`).
  - **re-hide** with `atxgreene.com/#desk-lock`.
- The board is *also* gated (`body.desk-unlocked .private-signal-desk:target`),
  so guessing the `#bet-of-day` anchor without unlocking shows nothing.

### Rules for the desk

- **Never make the launcher or board visible by default.** Don't remove the
  `display:none` defaults or the `body.desk-unlocked` gating. If you must debug,
  test with `#desk` and revert.
- **Daily "Bet of the Day" updates = HTML-only.** Edit the ticket markup inside
  `<section class="private-signal-desk" id="bet-of-day">`. This does **not** touch
  any `<script>`, so **no CSP re-hash needed**. Just run `verify.py` and ship.
- **Adding a new gated tool (e.g. the X screener):** add a new
  `<section class="private-signal-desk" id="screener">…</section>` (it inherits
  the gate automatically) and add a link to it in the launcher panel
  (`.casino-access-panel`). Still HTML-only → no re-hash.
- **If you change the gate script itself** (the IIFE with `atxg-desk`), that's an
  inline-script edit → **re-hash the CSP** per the CSP section.
- Keep the "not financial advice / research-only" disclaimer on any betting content.

---

## Common tasks — quick recipes

**Add / edit a selected-work card** (HTML-only, no re-hash): copy an
`<article class="card">` in `#work`, keep the Problem / Built / Capability
`<dl class="pbc">`, and stay within 4–6 cards — add one, move one to the Lab.

**Add an experiment to the Lab** (HTML-only, no re-hash): copy a
`<article class="lab-item">` into the right `.lab-group`.

**Add a writing/research entry** (HTML-only, no re-hash):
add an `<li>` to the `.writing-list` (title is an `<h3>`), and if it's a
new page, drop the file in `writing/` and add a `<url>` to `sitemap.xml`. New
writing pages are self-contained — match an existing page's structure; they don't
share the main CSP (each is its own file) but keep them script-light and on-brand.

**Update Bet of the Day** (HTML-only, no re-hash): edit tickets in `#bet-of-day`.

**Change an animation or the live feed** (JS edit → **re-hash required**):
edit the script, then follow the CSP workflow (`--print-hashes` → update meta →
verify). Bump `VERSION` in `sw.js` if you want clients to drop the old cache.

**Add an external embed/API** → update the matching CSP directive (`frame-src` /
`connect-src` / `img-src`) or the browser will block it.

---

## Footguns checklist

- [ ] Edited an inline `<script>`? → re-ran `--print-hashes`, updated CSP, count comment.
- [ ] `verify.py` prints `All checks passed.`?
- [ ] Went through a PR and saw CI green before merging?
- [ ] No new public-facing gambling/mystical/unverified content?
- [ ] Signal-desk launcher + board still `display:none` by default?
- [ ] New external host? → added to the right CSP directive.
- [ ] Didn't delete `CNAME`, and didn't amend GitHub's Verified squash commit?
