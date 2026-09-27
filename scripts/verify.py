#!/usr/bin/env python3
"""Site integrity checks for atxgreene.com — run locally or in CI.

Checks, for every page in PAGES:
  1. Inline <script> hashes match the Content-Security-Policy meta tag
     (edit an inline script -> re-run with --print-hashes and update that page's CSP).
  2. Inline scripts (+ sw.js) pass `node --check` syntax validation.
  3. The JSON-LD block (+ manifest.webmanifest) is valid JSON.
  4. HTML tag balance for structural tags.
  5. Referenced local assets exist.

Exit code 0 = all good; 1 = failures (printed).
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "about/index.html"]
failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL:", msg)


def ok(msg):
    print("  ok:", msg)


def sha256_csp(text):
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode() + "'"


def node_check(label, code):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "s.js")
        open(p, "w").write(code)
        r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    ok("%s syntax" % label) if r.returncode == 0 else fail("%s syntax error:\n%s" % (label, r.stderr.strip()))


pages = {}
for page in PAGES:
    html = open(os.path.join(ROOT, page), encoding="utf-8").read()
    pages[page] = (html, re.findall(r"<script>(.*?)</script>", html, re.S))

if "--print-hashes" in sys.argv:
    for page, (html, scripts) in pages.items():
        print("%s — inline script CSP hashes (paste into its script-src directive):" % page)
        for s in scripts:
            print(" ", sha256_csp(s))
    sys.exit(0)

for page, (html, scripts) in pages.items():
    print("[%s]" % page)
    page_dir = os.path.dirname(os.path.join(ROOT, page))

    # 1. CSP hash coverage
    csp = re.search(r'http-equiv="Content-Security-Policy"\s+content="([^"]+)"', html)
    if not csp:
        fail("%s: no Content-Security-Policy meta tag found" % page)
    else:
        for i, s in enumerate(scripts):
            h = sha256_csp(s)
            if h in csp.group(1):
                ok("script %d hash present in CSP" % i)
            else:
                fail("%s: script %d hash missing from CSP: %s (run scripts/verify.py --print-hashes)" % (page, i, h))

    # 2. JS syntax
    for i, s in enumerate(scripts):
        node_check("%s inline script %d" % (page, i), s)

    # 3. JSON-LD
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if ld:
        try:
            json.loads(ld.group(1))
            ok("JSON-LD valid")
        except Exception as e:
            fail("%s: JSON-LD invalid: %s" % (page, e))
    else:
        fail("%s: JSON-LD block missing" % page)

    # 4. Tag balance
    for tag in ["div", "span", "section", "article", "nav", "aside", "footer", "main", "form", "script", "style", "canvas"]:
        o = len(re.findall(r"<%s[\s>]" % tag, html))
        c = len(re.findall(r"</%s>" % tag, html))
        if o == c:
            ok("<%s> balanced (%d)" % (tag, o))
        else:
            fail("%s: <%s> unbalanced: %d open / %d close" % (page, tag, o, c))

    # 5. Local asset references resolve (root-absolute or page-relative)
    for ref in set(re.findall(r'''(?:src|href)="(/?assets/[^"]+|/favicon\.png|/apple-touch-icon\.png|/manifest\.webmanifest|/sw\.js|/og\.png)"|url\('(/?assets/[^']+)'\)''', html)):
        ref = ref[0] or ref[1]
        path = os.path.join(ROOT, ref.lstrip("/")) if ref.startswith("/") else os.path.join(page_dir, ref)
        ok("asset exists: %s" % ref) if os.path.exists(path) else fail("%s: missing asset: %s" % (page, ref))

# Shared files
print("[shared]")
node_check("sw.js", open(os.path.join(ROOT, "sw.js")).read())
try:
    json.load(open(os.path.join(ROOT, "manifest.webmanifest")))
    ok("manifest.webmanifest valid JSON")
except Exception as e:
    fail("manifest.webmanifest invalid: %s" % e)

print()
if failures:
    print("%d check(s) FAILED" % len(failures))
    sys.exit(1)
print("All checks passed.")
