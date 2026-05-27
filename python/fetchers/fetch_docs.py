"""
fetch_docs.py
Scrapes the Arduino UNO Q documentation index page and returns a list of
doc page items to display on the Sales Hub.

Each item dict:
  {
    "title": str,
    "meta":  str,   # short subtitle / description
    "tag":   "Docs" | "New",
    "url":   str,
  }
"""

import sys
import os
import json
import logging
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DOCS_URL, DOCS_MAX_ITEMS, DATA_DIR

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ArduinoSalesHubBot/1.0; "
        "+https://github.com/arduino/sales-hub)"
    )
}

FALLBACK_ITEMS = [
    {"title": "Getting started with Arduino UNO Q",         "meta": "docs.arduino.cc · Official overview",   "tag": "Docs", "url": "https://docs.arduino.cc/hardware/uno-q/"},
    {"title": "UNO Q User Manual",                          "meta": "docs.arduino.cc · Full user guide",      "tag": "Docs", "url": "https://docs.arduino.cc/tutorials/uno-q/user-manual/"},
    {"title": "App Lab — Getting Started",                  "meta": "docs.arduino.cc · Recently updated",     "tag": "New",  "url": "https://docs.arduino.cc/software/app-lab/tutorials/getting-started/"},
    {"title": "UNO Q as a Single-Board Computer",           "meta": "docs.arduino.cc · SBC mode guide",       "tag": "Docs", "url": "https://docs.arduino.cc/tutorials/uno-q/single-board-computer/"},
    {"title": "Custom AI Models for App Lab",               "meta": "docs.arduino.cc · AI integration",       "tag": "New",  "url": "https://docs.arduino.cc/software/app-lab/tutorials/ai-models/"},
    {"title": "UNO Q datasheet (PDF)",                      "meta": "docs.arduino.cc · Full specs ABX00162",  "tag": "Docs", "url": "https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf"},
    {"title": "Arduino App CLI — command line management",  "meta": "docs.arduino.cc · CLI reference",        "tag": "Docs", "url": "https://docs.arduino.cc/software/app-lab/tutorials/cli"},
    {"title": "Connect to UNO Q via SSH",                   "meta": "docs.arduino.cc · Remote access",        "tag": "Docs", "url": "https://docs.arduino.cc/tutorials/uno-q/ssh/"},
    {"title": "UNO Q Power Specifications",                 "meta": "docs.arduino.cc · Power & hardware",     "tag": "Docs", "url": "https://docs.arduino.cc/tutorials/uno-q/power-specification/"},
    {"title": "Connect UNO Q to the Arduino Cloud",         "meta": "docs.arduino.cc · Cloud integration",    "tag": "Docs", "url": "https://docs.arduino.cc/tutorials/uno-q/arduino-cloud/"},
]


UNO_Q_PATH_PATTERNS = (
    "/tutorials/uno-q/",
    "/hardware/uno-q/",
    "/software/app-lab/tutorials/",
)


def _scrape(url: str, max_items: int) -> list[dict]:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    candidates = []

    # Strategy 1: structured cards
    for card in soup.select("article, .content-card, .tutorial-card, li.content-item"):
        a = card.find("a", href=True)
        heading = card.find(["h2", "h3", "h4", "p"])
        if a and heading:
            title = heading.get_text(strip=True)
            href = a["href"]
            if title and len(title) > 5:
                candidates.append((title, href))

    # Strategy 2: any link whose path points to a real doc/tutorial page
    if not candidates:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(pat in href for pat in UNO_Q_PATH_PATTERNS):
                # skip bare index pages — we want sub-pages with a second segment
                path = href.split("?")[0].rstrip("/")
                segments = [s for s in path.split("/") if s]
                if len(segments) < 3:          # e.g. /tutorials/uno-q has only 2
                    continue
                title = a.get_text(strip=True)
                if title and len(title) > 5:
                    candidates.append((title, href))

    seen: set[str] = set()
    items: list[dict] = []
    for title, href in candidates:
        if title in seen:
            continue
        seen.add(title)
        full_url = href if href.startswith("http") else f"https://docs.arduino.cc{href}"
        tag = "New" if "app-lab" in full_url else "Docs"
        items.append({"title": title, "meta": "docs.arduino.cc · Official documentation",
                      "tag": tag, "url": full_url})
        if len(items) >= max_items:
            break

    return items


MIN_SCRAPED = 5   # require at least this many results before trusting the scraper


def fetch() -> list[dict]:
    try:
        items = _scrape(DOCS_URL, DOCS_MAX_ITEMS)
        if len(items) >= MIN_SCRAPED:
            log.info("fetch_docs: scraped %d items", len(items))
            return items
        log.warning("fetch_docs: scraper returned %d items (< %d) — using fallback",
                    len(items), MIN_SCRAPED)
    except Exception as exc:
        log.warning("fetch_docs: scrape failed (%s) — using fallback", exc)
    return FALLBACK_ITEMS[:DOCS_MAX_ITEMS]


def save(items: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "docs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": datetime.now(timezone.utc).isoformat(), "items": items}, f, ensure_ascii=False, indent=2)
    log.info("fetch_docs: saved %d items → %s", len(items), out_path)
