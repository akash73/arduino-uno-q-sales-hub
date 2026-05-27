"""
fetch_blog.py — RSS feed reader for blog.arduino.cc
"""

import sys, os, json, logging
from datetime import datetime, timezone
import feedparser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import BLOG_FEEDS, BLOG_MAX_ITEMS, DATA_DIR

log = logging.getLogger(__name__)


def _parse_date(entry) -> datetime:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def fetch() -> list[dict]:
    all_items: list[dict] = []
    for feed_cfg in BLOG_FEEDS:
        url, tag = feed_cfg["url"], feed_cfg["tag"]
        try:
            d = feedparser.parse(url)
            for entry in d.entries:
                dt = _parse_date(entry)
                all_items.append({
                    "title": entry.get("title", "(no title)").strip(),
                    "meta":  f"blog.arduino.cc · {dt.strftime('%b %-d, %Y')}",
                    "tag":   tag,
                    "url":   entry.get("link", "https://blog.arduino.cc/"),
                    "_sort_dt": dt.timestamp(),
                })
            log.info("fetch_blog: %d entries from %s", len(d.entries), url)
        except Exception as exc:
            log.warning("fetch_blog: failed to fetch %s — %s", url, exc)

    all_items.sort(key=lambda x: x["_sort_dt"], reverse=True)
    seen: set[str] = set()
    result: list[dict] = []
    for item in all_items:
        if item["url"] in seen:
            continue
        seen.add(item["url"])
        result.append({k: v for k, v in item.items() if k != "_sort_dt"})
        if len(result) >= BLOG_MAX_ITEMS:
            break
    return result


def save(items: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "blog.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": datetime.now(timezone.utc).isoformat(), "items": items}, f, ensure_ascii=False, indent=2)
    log.info("fetch_blog: saved %d items → %s", len(items), out_path)
