"""
generate_static.py
Runs all fetchers and generates docs/index.html for GitHub Pages.
No Flask required — runs as a plain Python script.

Usage:
    python python/generate_static.py
"""

import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("generate_static")

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_DIR = os.path.join(REPO_ROOT, "python")
DATA_DIR   = os.path.join(PYTHON_DIR, "data")
DOCS_DIR   = os.path.join(REPO_ROOT, "docs")
HTML_OUT   = os.path.join(DOCS_DIR, "index.html")

sys.path.insert(0, PYTHON_DIR)

# Override config paths before importing anything else
import config as _cfg
_cfg.DATA_DIR  = DATA_DIR
_cfg.WWW_DIR   = DOCS_DIR
_cfg.HTML_FILE = HTML_OUT

# Inject YOUTUBE_API_KEY from environment if set (GitHub Actions secret)
_yt_key = os.environ.get("YOUTUBE_API_KEY", "")
if _yt_key:
    _cfg.YOUTUBE_API_KEY = _yt_key

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# ── Run fetchers ──────────────────────────────────────────────────────────────
from fetchers import fetch_docs, fetch_blog, fetch_projects, fetch_youtube
import traceback

for fetcher in [fetch_docs, fetch_blog, fetch_projects, fetch_youtube]:
    name = fetcher.__name__.split(".")[-1]
    try:
        items = fetcher.fetch()
        fetcher.save(items)
        log.info("%s: %d items saved", name, len(items))
    except Exception:
        log.warning("%s failed:\n%s", name, traceback.format_exc())

# ── Generate HTML ─────────────────────────────────────────────────────────────
import generate_html
generate_html.DATA_DIR  = DATA_DIR
generate_html.WWW_DIR   = DOCS_DIR
generate_html.HTML_FILE = HTML_OUT

# Patch out the Refresh button — no Flask server on GitHub Pages
_original_build = generate_html.build_html

def _static_build() -> str:
    html = _original_build()
    # Replace the refresh button with a static "auto-updated daily" note
    html = html.replace(
        '<button class="refresh-btn" id="btn-refresh" onclick="triggerRefresh()">↺ Refresh</button>',
        '<span class="refresh-btn" style="cursor:default;opacity:.6">↺ Auto-updated daily</span>'
    )
    # Remove the JS refresh function to keep the page clean
    return html

generate_html.build_html = _static_build
generate_html.main()

log.info("✓ Generated %s", HTML_OUT)
