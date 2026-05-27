"""
fetch_youtube.py — YouTube Data API v3 fetcher
"""

import sys, os, json, logging, re
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import YOUTUBE_API_KEY, YOUTUBE_PLAYLIST_ID, YOUTUBE_MAX_RESULTS, DATA_DIR

log = logging.getLogger(__name__)
PLAYLIST_URL = f"https://www.youtube.com/playlist?list={YOUTUBE_PLAYLIST_ID}"


def _fmt_duration(iso: str) -> str:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m:
        return ""
    h, mi, s = int(m.group(1) or 0), int(m.group(2) or 0), int(m.group(3) or 0)
    return f"{h}:{mi:02d}:{s:02d}" if h else f"{mi}:{s:02d}"


def _fmt_views(n: str) -> str:
    try:
        v = int(n)
    except (ValueError, TypeError):
        return ""
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M views"
    if v >= 1_000:
        return f"{v/1_000:.1f}k views"
    return f"{v} views"


def fetch() -> list[dict]:
    if YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
        log.warning("fetch_youtube: API key not set — returning empty list")
        return []
    try:
        from googleapiclient.discovery import build
    except ImportError:
        log.warning("fetch_youtube: google-api-python-client not installed")
        return []
    try:
        yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        pl = yt.playlistItems().list(part="contentDetails", playlistId=YOUTUBE_PLAYLIST_ID, maxResults=YOUTUBE_MAX_RESULTS).execute()
        ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
        if not ids:
            return []
        vids = yt.videos().list(part="snippet,contentDetails,statistics", id=",".join(ids)).execute()
        items = []
        for v in vids.get("items", []):
            snippet = v.get("snippet", {})
            meta_parts = ["YouTube"]
            dur = _fmt_duration(v.get("contentDetails", {}).get("duration", ""))
            views = _fmt_views(v.get("statistics", {}).get("viewCount", ""))
            if dur:   meta_parts.append(dur)
            if views: meta_parts.append(views)
            items.append({
                "title": snippet.get("title", "(no title)"),
                "meta":  " · ".join(meta_parts),
                "tag":   "Video",
                "url":   f"https://www.youtube.com/watch?v={v['id']}",
                "thumb": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            })
        log.info("fetch_youtube: fetched %d videos", len(items))
        return items
    except Exception as exc:
        log.warning("fetch_youtube: API call failed — %s", exc)
        return []


def save(items: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "youtube.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": datetime.now(timezone.utc).isoformat(), "playlist_url": PLAYLIST_URL, "items": items}, f, ensure_ascii=False, indent=2)
    log.info("fetch_youtube: saved %d items → %s", len(items), out_path)
