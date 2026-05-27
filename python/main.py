"""
main.py — Arduino UNO Q Sales Hub
App Lab entry point.

Starts a Flask web server on port 8080 and schedules a daily content
refresh. All content fetching and HTML generation happen in background
threads so the server stays responsive at all times.
"""

from arduino.app_utils import App

import os
import sys
import json
import logging
import threading
import time
import traceback
import importlib
from datetime import datetime, timezone

from flask import Flask, jsonify, send_from_directory

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("sales-hub")

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import DATA_DIR, WWW_DIR, HTML_FILE, SERVER_PORT, REFRESH_TIME
import generate_html
from fetchers import fetch_docs, fetch_blog, fetch_projects, fetch_youtube

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WWW_DIR, exist_ok=True)

# ── Refresh logic ─────────────────────────────────────────────────────────────
_refresh_lock = threading.Lock()
_refresh_status = {"running": False, "last_run": None, "last_error": None}


def run_refresh():
    """Fetch all sources and regenerate the HTML page."""
    if not _refresh_lock.acquire(blocking=False):
        log.info("Refresh already running — skipping")
        return

    _refresh_status["running"] = True
    _refresh_status["last_error"] = None
    log.info("=== Content refresh started ===")

    try:
        for fetcher in [fetch_docs, fetch_blog, fetch_projects, fetch_youtube]:
            importlib.reload(fetcher)
            name = fetcher.__name__.split(".")[-1]
            try:
                items = fetcher.fetch()
                fetcher.save(items)
                log.info("%s: %d items", name, len(items))
            except Exception:
                log.warning("%s failed:\n%s", name, traceback.format_exc())

        importlib.reload(generate_html)
        generate_html.main()
        _refresh_status["last_run"] = datetime.now(timezone.utc).isoformat()
        log.info("=== Refresh complete ===")

    except Exception:
        msg = traceback.format_exc()
        _refresh_status["last_error"] = msg
        log.error("Refresh failed:\n%s", msg)
    finally:
        _refresh_status["running"] = False
        _refresh_lock.release()


def _background_refresh():
    """Run refresh in a daemon thread."""
    threading.Thread(target=run_refresh, daemon=True).start()


# ── Daily scheduler ───────────────────────────────────────────────────────────
def _scheduler():
    """Lightweight scheduler: fires run_refresh once per day at REFRESH_TIME."""
    log.info("Scheduler started — daily refresh at %s", REFRESH_TIME)
    while True:
        now = datetime.now()
        h, m = map(int, REFRESH_TIME.split(":"))
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if target <= now:
            # Already past today's window — schedule for tomorrow
            from datetime import timedelta
            target += timedelta(days=1)
        wait_sec = (target - now).total_seconds()
        log.info("Next refresh in %.0f minutes", wait_sec / 60)
        time.sleep(wait_sec)
        _background_refresh()


threading.Thread(target=_scheduler, daemon=True).start()

# ── Flask app ─────────────────────────────────────────────────────────────────
flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    """Serve the Sales Hub page, generating it first if it doesn't exist."""
    if not os.path.exists(HTML_FILE):
        log.info("index.html not found — generating from fallback data")
        generate_html.main()
    return send_from_directory(WWW_DIR, "index.html")


@flask_app.route("/refresh", methods=["POST"])
def refresh():
    """Trigger an immediate content refresh (non-blocking)."""
    if _refresh_status["running"]:
        return jsonify({"status": "already_running"}), 202
    _background_refresh()
    return jsonify({"status": "started"}), 202


@flask_app.route("/status")
def status():
    """Return refresh status as JSON."""
    return jsonify({
        "running":    _refresh_status["running"],
        "last_run":   _refresh_status["last_run"],
        "last_error": _refresh_status["last_error"],
    })


def _start_flask():
    log.info("Flask server starting on port %d", SERVER_PORT)
    flask_app.run(host="0.0.0.0", port=SERVER_PORT, debug=False, use_reloader=False)


# ── Startup ───────────────────────────────────────────────────────────────────
# If no cached data yet, kick off the first fetch in the background
data_exists = any(
    os.path.exists(os.path.join(DATA_DIR, f))
    for f in ("docs.json", "blog.json", "projects.json", "youtube.json")
)
if not data_exists:
    log.info("No cached data found — running initial fetch")
    _background_refresh()
else:
    log.info("Cached data found — regenerating HTML from cache")
    generate_html.main()

threading.Thread(target=_start_flask, daemon=True).start()

# ── Hand control to App Lab ───────────────────────────────────────────────────
App.run()
