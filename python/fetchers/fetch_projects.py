"""
fetch_projects.py — Scraper for projecthub.arduino.cc
"""

import sys, os, json, logging, re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PROJECTHUB_URLS, PROJECTHUB_MAX_ITEMS, DATA_DIR

log = logging.getLogger(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ArduinoSalesHubBot/1.0)"}
BASE_URL = "https://projecthub.arduino.cc"


def _scrape_page(url: str) -> list[dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        log.warning("fetch_projects: GET %s failed — %s", url, exc)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    for card in soup.select("article, .project-card, .ph-card, [class*='project']"):
        a = card.find("a", href=True)
        heading = card.find(["h2", "h3", "h4"])
        if not (a and heading):
            continue
        title = heading.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        href = a["href"]
        full_url = href if href.startswith("http") else BASE_URL + href
        views_el = card.find(class_=re.compile(r"view|count|stat", re.I))
        views_text = views_el.get_text(strip=True) if views_el else ""
        meta = f"projecthub.arduino.cc · {views_text}" if views_text else "projecthub.arduino.cc"
        items.append({"title": title, "meta": meta, "tag": "Project", "url": full_url})

    if not items:
        for a in soup.find_all("a", href=re.compile(r"/projects/"), string=True):
            title = a.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            href = a["href"]
            full_url = href if href.startswith("http") else BASE_URL + href
            items.append({"title": title, "meta": "projecthub.arduino.cc", "tag": "Project", "url": full_url})

    return items


def fetch() -> list[dict]:
    all_items: list[dict] = []
    seen: set[str] = set()
    for url in PROJECTHUB_URLS:
        for item in _scrape_page(url):
            if item["url"] not in seen:
                seen.add(item["url"])
                all_items.append(item)
    log.info("fetch_projects: %d unique projects found", len(all_items))
    return all_items[:PROJECTHUB_MAX_ITEMS]


def save(items: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "projects.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": datetime.now(timezone.utc).isoformat(), "items": items}, f, ensure_ascii=False, indent=2)
    log.info("fetch_projects: saved %d items → %s", len(items), out_path)
