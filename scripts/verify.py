#!/usr/bin/env python3
"""Site integrity checks for atxgreene.com — run locally or in CI.

Checks:
  1. Inline <script> hashes match the Content-Security-Policy meta tag
     (edit an inline script -> re-run with --print-hashes and update the CSP).
  2. Inline scripts + sw.js pass `node --check` syntax validation.
  3. manifest.webmanifest and the JSON-LD block are valid JSON.
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
failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL:", msg)


def ok(msg):
    print("  ok:", msg)


def sha256_csp(text):
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode() + "'"


html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
hashes = [sha256_csp(s) for s in scripts]

if "--print-hashes" in sys.argv:
    print("Inline script CSP hashes (paste into the script-src directive):")
    for h in hashes:
        print(" ", h)
    sys.exit(0)

# 1. CSP hash coverage
csp = re.search(r'http-equiv="Content-Security-Policy"\s+content="([^"]+)"', html)
if not csp:
    fail("no Content-Security-Policy meta tag found")
else:
    policy = csp.group(1)
    for i, h in enumerate(hashes):
        if h in policy:
            ok("script %d hash present in CSP" % i)
        else:
            fail("script %d hash missing from CSP: %s (run scripts/verify.py --print-hashes)" % (i, h))

# 2. JS syntax
with tempfile.TemporaryDirectory() as td:
    for i, s in enumerate(scripts):
        p = os.path.join(td, "s%d.js" % i)
        open(p, "w").write(s)
        r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
        if r.returncode == 0:
            ok("inline script %d syntax" % i)
        else:
            fail("inline script %d syntax error:\n%s" % (i, r.stderr.strip()))
    r = subprocess.run(["node", "--check", os.path.join(ROOT, "sw.js")], capture_output=True, text=True)
    ok("sw.js syntax") if r.returncode == 0 else fail("sw.js syntax error:\n" + r.stderr.strip())

# 3. JSON artifacts
try:
    json.load(open(os.path.join(ROOT, "manifest.webmanifest")))
    ok("manifest.webmanifest valid JSON")
except Exception as e:
    fail("manifest.webmanifest invalid: %s" % e)

ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
if ld:
    try:
        json.loads(ld.group(1))
        ok("JSON-LD valid")
    except Exception as e:
        fail("JSON-LD invalid: %s" % e)
else:
    fail("JSON-LD block missing")

# 4. Tag balance
for tag in ["div", "span", "section", "article", "nav", "aside", "footer", "script", "style", "canvas"]:
    o = len(re.findall(r"<%s[\s>]" % tag, html))
    c = len(re.findall(r"</%s>" % tag, html))
    if o == c:
        ok("<%s> balanced (%d)" % (tag, o))
    else:
        fail("<%s> unbalanced: %d open / %d close" % (tag, o, c))

# 5. Local asset references resolve
for ref in set(re.findall(r'(?:src|href)="(/?assets/[^"]+|/favicon\.png|/apple-touch-icon\.png|/manifest\.webmanifest|/sw\.js|/og\.png)"', html)):
    path = os.path.join(ROOT, ref.lstrip("/"))
    if os.path.exists(path):
        ok("asset exists: %s" % ref)
    else:
        fail("missing asset: %s" % ref)

print()
if failures:
    print("%d check(s) FAILED" % len(failures))
    sys.exit(1)
print("All checks passed.")
