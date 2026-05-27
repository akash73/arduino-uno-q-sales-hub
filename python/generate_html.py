"""
generate_html.py (App Lab version)
Reads JSON data files and writes a self-contained index.html.
Identical to the standalone version but adds a "Refresh now" button
that POSTs to /refresh on the Flask server.
"""

import sys
import os
import json
import logging
from datetime import datetime, timezone
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_DIR, WWW_DIR, HTML_FILE, YOUTUBE_PLAYLIST_ID, SOCIAL_LINKS

log = logging.getLogger(__name__)

# ── Fallback data ─────────────────────────────────────────────────────────────

FALLBACK_DOCS = [
    {"title": "Getting started with Arduino UNO Q",           "meta": "docs.arduino.cc · Official overview",     "tag": "Docs",  "url": "https://docs.arduino.cc/hardware/uno-q/"},
    {"title": "UNO Q User Manual",                            "meta": "docs.arduino.cc · Full user guide",       "tag": "Docs",  "url": "https://docs.arduino.cc/tutorials/uno-q/user-manual/"},
    {"title": "App Lab — Getting Started",                    "meta": "docs.arduino.cc · Recently updated",      "tag": "New",   "url": "https://docs.arduino.cc/software/app-lab/tutorials/getting-started/"},
    {"title": "UNO Q as a Single-Board Computer",             "meta": "docs.arduino.cc · SBC mode guide",        "tag": "Docs",  "url": "https://docs.arduino.cc/tutorials/uno-q/single-board-computer/"},
    {"title": "Custom AI Models for App Lab",                 "meta": "docs.arduino.cc · AI integration",        "tag": "New",   "url": "https://docs.arduino.cc/software/app-lab/tutorials/ai-models/"},
    {"title": "UNO Q datasheet (PDF)",                        "meta": "docs.arduino.cc · Full specs ABX00162",   "tag": "Docs",  "url": "https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf"},
    {"title": "Arduino App CLI — command line management",    "meta": "docs.arduino.cc · CLI reference",         "tag": "Docs",  "url": "https://docs.arduino.cc/software/app-lab/tutorials/cli"},
    {"title": "Connect to UNO Q via SSH",                     "meta": "docs.arduino.cc · Remote access",         "tag": "Docs",  "url": "https://docs.arduino.cc/tutorials/uno-q/ssh/"},
    {"title": "UNO Q Power Specifications",                   "meta": "docs.arduino.cc · Power & hardware",      "tag": "Docs",  "url": "https://docs.arduino.cc/tutorials/uno-q/power-specification/"},
    {"title": "Connect UNO Q to the Arduino Cloud",           "meta": "docs.arduino.cc · Cloud integration",     "tag": "Docs",  "url": "https://docs.arduino.cc/tutorials/uno-q/arduino-cloud/"},
]
FALLBACK_BLOG = [
    {"title": "Introducing Arduino UNO Q",                    "meta": "blog.arduino.cc · May 15, 2026",  "tag": "UNO Q",  "url": "https://blog.arduino.cc/category/arduino/uno-q/"},
    {"title": "AppLab: deploying AI models on UNO Q",         "meta": "blog.arduino.cc · May 3, 2026",   "tag": "AppLab", "url": "https://blog.arduino.cc/category/arduino/app-lab/"},
    {"title": "Edge AI with Modulino and UNO Q",              "meta": "blog.arduino.cc · Apr 20, 2026",  "tag": "AppLab", "url": "https://blog.arduino.cc/category/arduino/app-lab/"},
    {"title": "UNO Q in industrial IoT applications",         "meta": "blog.arduino.cc · Apr 5, 2026",   "tag": "UNO Q",  "url": "https://blog.arduino.cc/category/arduino/uno-q/"},
    {"title": "Dual-brain architecture explained",            "meta": "blog.arduino.cc · Mar 18, 2026",  "tag": "UNO Q",  "url": "https://blog.arduino.cc/category/arduino/uno-q/"},
    {"title": "Getting the most out of AppLab",               "meta": "blog.arduino.cc · Mar 2, 2026",   "tag": "AppLab", "url": "https://blog.arduino.cc/category/arduino/app-lab/"},
    {"title": "Building a smart factory node with UNO Q",     "meta": "blog.arduino.cc · Feb 14, 2026",  "tag": "UNO Q",  "url": "https://blog.arduino.cc/category/arduino/uno-q/"},
    {"title": "UNO Q power management deep dive",             "meta": "blog.arduino.cc · Feb 1, 2026",   "tag": "UNO Q",  "url": "https://blog.arduino.cc/category/arduino/uno-q/"},
    {"title": "Modulino sensors: hands-on review",            "meta": "blog.arduino.cc · Jan 22, 2026",  "tag": "AppLab", "url": "https://blog.arduino.cc/category/arduino/app-lab/"},
    {"title": "From prototype to production with UNO Q",      "meta": "blog.arduino.cc · Jan 10, 2026",  "tag": "UNO Q",  "url": "https://blog.arduino.cc/category/arduino/uno-q/"},
]
FALLBACK_PROJECTS = [
    {"title": "AI Projects with UNO Q",                       "meta": "projecthub.arduino.cc · LLM & Agents",  "tag": "Project", "url": "https://projecthub.arduino.cc/uid03055/ai-projects-with-uno-q-ebadc6"},
    {"title": "UNO Q Arcade Cabinet (RetroArch)",             "meta": "projecthub.arduino.cc · Gaming",        "tag": "Project", "url": "https://projecthub.arduino.cc/jcarolinares/39dd389d-d36f-48ab-9434-058abf6039b1"},
    {"title": "Desk Robot with AI Chat & Videotronic OS",     "meta": "projecthub.arduino.cc · Robotics",      "tag": "Project", "url": "https://projecthub.arduino.cc/Tishin/uno-q-desk-robot-with-full-ai-chat-and-videotronic-os-phase-1-caea81"},
    {"title": "Real-time Ultrasonic Sonar with Web UI",       "meta": "projecthub.arduino.cc · Sensors",       "tag": "Project", "url": "https://projecthub.arduino.cc/robuinlabs/arduino-uno-q-radar-project-build-a-real-time-ultrasonic-sonar-with-web-interface-ffbb9d"},
    {"title": "Greetings from Arduino UNO Q",                 "meta": "projecthub.arduino.cc · Starter",       "tag": "Project", "url": "https://projecthub.arduino.cc/leocavagnis/greetings-from-arduino-uno-q-6a403b"},
    {"title": "UNO Q Local Weather Station",                  "meta": "projecthub.arduino.cc · IoT",           "tag": "Project", "url": "https://projecthub.arduino.cc/Arduino_Genuino/arduino-uno-q-local-weather-station-b771ee"},
    {"title": "Inverted Pendulum: PID Control + UI",          "meta": "projecthub.arduino.cc · Control",       "tag": "Project", "url": "https://projecthub.arduino.cc/Arduino_Genuino/arduino-uno-q-inverted-pendulum-pid-ui-e8833f"},
    {"title": "Modulino LED Matrix — Pixel Canvas",           "meta": "projecthub.arduino.cc · Display",       "tag": "Project", "url": "https://projecthub.arduino.cc/mario-r/uno-q-modulino-led-matrix-pixel-canvas-6a663e"},
    {"title": "Gemini Voice Assistant for Smart Home",        "meta": "projecthub.arduino.cc · Voice AI",      "tag": "Project", "url": "https://projecthub.arduino.cc/volt-23/talk-to-your-house-a-gemini-powered-voice-assistant-on-arduino-uno-q-0d3a37"},
    {"title": "Connect to UNO Q via ADB",                     "meta": "docs.arduino.cc · Developer tools",     "tag": "Project", "url": "https://docs.arduino.cc/tutorials/uno-q/adb"},
]
FALLBACK_YOUTUBE: list[dict] = []

TAG_STYLES: dict[str, tuple[str, str]] = {
    "Docs":    ("#DDEEFF", "#1A5FA8"),
    "New":     ("#D6F5F0", "#007A68"),
    "UNO Q":   ("#E0F4F4", "#006B6E"),
    "AppLab":  ("#E0F4F4", "#006B6E"),
    "Article": ("#F0EFEB", "#5A5856"),
    "Project": ("#FEF0E6", "#B85B1A"),
    "Video":   ("#FDECEA", "#B03020"),
}
SECTION_BG   = {"docs": "#EFF5FD", "blog": "#EDF8F5", "projects": "#FEF5EE", "video": "#FDEEED"}
SECTION_ICON = {"docs": "📄", "blog": "📰", "projects": "🔧", "video": "▶️"}


MAX_ITEMS = 10


def _load_json(filename: str, fallback: list) -> tuple[list, str]:
    """Load items from a JSON data file, padding with fallback to always reach MAX_ITEMS."""
    path = os.path.join(DATA_DIR, filename)
    items: list = []
    fetched_at: str = ""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", [])
        fetched_at = data.get("fetched_at", "")
        if not items:
            log.warning("generate_html: %s is empty — using fallback", filename)
    except FileNotFoundError:
        log.warning("generate_html: %s not found — using fallback", filename)
    except Exception as exc:
        log.warning("generate_html: error reading %s (%s) — using fallback", filename, exc)

    # Pad with fallback items until we reach MAX_ITEMS (skip duplicates by URL)
    if len(items) < MAX_ITEMS:
        seen_urls = {i.get("url", "") for i in items}
        for fb in fallback:
            if len(items) >= MAX_ITEMS:
                break
            if fb.get("url", "") not in seen_urls:
                items.append(fb)
                seen_urls.add(fb.get("url", ""))

    return items[:MAX_ITEMS], fetched_at


def _tag_badge(tag: str) -> str:
    bg, color = TAG_STYLES.get(tag, ("#f0f0f0", "#555"))
    return f'<span class="tag" style="background:{bg};color:{color}">{escape(tag)}</span>'


def _item_card(item: dict, idx: int) -> str:
    title = escape(item.get("title", ""))
    meta  = escape(item.get("meta", ""))
    tag   = item.get("tag", "")
    key   = escape(json.dumps({"title": item.get("title", ""), "url": item.get("url", "")}))
    return f'''
    <div class="item-card" data-key='{key}' onclick="toggleItem(this)">
      <div class="item-body">
        <div class="item-title">{title}</div>
        <div class="item-meta">{meta}</div>
      </div>
      <div class="item-actions">
        {_tag_badge(tag)}
        <div class="checkbox"></div>
      </div>
    </div>'''


def _section_html(section_id, label, items, view_all_label, view_all_url) -> str:
    icon  = SECTION_ICON.get(section_id, "📌")
    bg    = SECTION_BG.get(section_id, "#f5f5f5")
    cards = "\n".join(_item_card(item, i) for i, item in enumerate(items))
    return f'''
  <section id="{section_id}" class="content-section">
    <div class="section-header">
      <div class="section-title-group">
        <div class="section-icon" style="background:{bg}">{icon}</div>
        <span class="section-label">{escape(label)}</span>
        <span class="section-count">{len(items)} items</span>
      </div>
      <a href="{escape(view_all_url)}" target="_blank" rel="noreferrer" class="view-all">
        {escape(view_all_label)} ↗
      </a>
    </div>
    <div class="items-grid">{cards}</div>
  </section>'''


def _last_updated(timestamps: list[str]) -> str:
    valid = []
    for ts in timestamps:
        if ts:
            try:
                valid.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
            except Exception:
                pass
    if not valid:
        return "today at 06:00"
    return max(valid).astimezone().strftime("%-d %b %Y at %H:%M")


def build_html() -> str:
    docs_items,    docs_ts    = _load_json("docs.json",     FALLBACK_DOCS)
    blog_items,    blog_ts    = _load_json("blog.json",     FALLBACK_BLOG)
    project_items, project_ts = _load_json("projects.json", FALLBACK_PROJECTS)
    youtube_items, youtube_ts = _load_json("youtube.json",  FALLBACK_YOUTUBE)

    updated_str   = _last_updated([docs_ts, blog_ts, project_ts, youtube_ts])
    playlist_url  = f"https://www.youtube.com/playlist?list={YOUTUBE_PLAYLIST_ID}"

    docs_html     = _section_html("docs",     "Documentation",       docs_items[:10],    "Open docs site",      "https://docs.arduino.cc/hardware/uno-q/")
    blog_html     = _section_html("blog",     "Blog posts",          blog_items[:10],    "All UNO Q articles",  "https://blog.arduino.cc/category/arduino/uno-q/")
    projects_html = _section_html("projects", "Community projects",  project_items[:10], "Project Hub",         "https://projecthub.arduino.cc/")
    video_html    = _section_html("video",    "YouTube videos",      youtube_items[:10], "Full playlist",       playlist_url)

    social_links_html = "\n".join(
        f'<a href="{escape(s["url"])}" target="_blank" rel="noreferrer" class="social-btn">{escape(s["label"])} ↗</a>'
        for s in SOCIAL_LINKS
    )
    nav_pills = "\n".join(
        f'<a href="#{sid}" class="nav-pill">{label}</a>'
        for sid, label in [("docs","Documentation"),("blog","Blog posts"),("projects","Community projects"),("video","YouTube videos"),("social","Social")]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Arduino UNO Q — Sales Hub</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet" />
  <style>
    /* ── Reset & tokens ─────────────────────────────────────────
       Colours taken directly from www.arduino.cc
       Primary teal   : #00979d  (meta theme-color on arduino.cc)
       Dark nav bg    : #1a1a1a  (arduino.cc top bar)
       Accent orange  : #e47128  (store / buy-now CTAs)
    ──────────────────────────────────────────────────────────── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --teal:         #00979d;
      --teal-dark:    #007a80;
      --teal-light:   #d6f2f3;
      --teal-bg:      #f0fafb;
      --orange:       #e47128;
      --dark:         #1a1a1a;
      --dark-2:       #2d2d2d;
      --text-primary: #1b1b1b;
      --text-secondary:#5a5a5a;
      --text-muted:   #9a9a9a;
      --border:       #e5e5e5;
      --border-dark:  #cecece;
      --bg-page:      #f5f5f3;
      --bg-card:      #ffffff;
      --radius:       8px;
      --radius-sm:    5px;
      --shadow:       0 2px 12px rgba(0,0,0,.09), 0 1px 3px rgba(0,0,0,.05);
    }}
    body {{
      font-family: "Nunito", system-ui, -apple-system, sans-serif;
      background: var(--bg-page);
      min-height: 100vh;
      padding: 28px 16px 48px;
      color: var(--text-primary);
      line-height: 1.5;
    }}

    /* ── App shell ──────────────────────────────────────────── */
    #app {{
      max-width: 1080px;
      margin: 0 auto;
      background: var(--bg-card);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }}

    /* ── Top nav bar — dark like arduino.cc ─────────────────── */
    .hub-header {{
      padding: 0 24px;
      background: var(--dark);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 54px;
    }}
    .header-brand {{ display: flex; align-items: center; gap: 10px; }}
    .brand-logo {{
      width: 30px; height: 30px;
      background: var(--teal);
      border-radius: 6px;
      display: flex; align-items: center; justify-content: center;
      color: #fff; font-weight: 900; font-size: 15px; flex-shrink: 0;
    }}
    .brand-name {{
      font-weight: 800; font-size: 14px;
      color: #ffffff; letter-spacing: -0.2px;
    }}
    .brand-sub {{
      font-size: 11px; color: rgba(255,255,255,.4);
      margin-top: 1px; font-weight: 500;
    }}
    .header-right {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
    .nav-pills {{ display: flex; gap: 2px; }}
    .nav-pill {{
      font-size: 11px; font-weight: 700;
      padding: 5px 11px; border-radius: 20px;
      color: rgba(255,255,255,.55); text-decoration: none;
      transition: color .15s, background .15s;
    }}
    .nav-pill:hover {{ color: #fff; background: rgba(255,255,255,.1); }}
    .refresh-btn {{
      font-size: 11px; font-weight: 700; font-family: inherit;
      padding: 5px 13px; border-radius: 20px;
      border: 1.5px solid rgba(255,255,255,.22);
      color: rgba(255,255,255,.75);
      background: transparent; cursor: pointer;
      transition: background .15s, border-color .15s, color .15s;
    }}
    .refresh-btn:hover    {{ background: rgba(255,255,255,.1); border-color: rgba(255,255,255,.4); color: #fff; }}
    .refresh-btn:disabled {{ opacity: 0.3; cursor: not-allowed; }}

    /* ── Teal accent banner ─────────────────────────────────── */
    .hub-banner {{
      background: var(--teal);
      padding: 8px 24px;
      display: flex; align-items: center; justify-content: space-between;
    }}
    .hub-banner-text {{
      font-size: 11.5px; font-weight: 700;
      color: rgba(255,255,255,.92); letter-spacing: 0.1px;
    }}
    .hub-banner-badge {{
      font-size: 10px; font-weight: 800; letter-spacing: 0.5px;
      text-transform: uppercase;
      background: rgba(0,0,0,.15); color: #fff;
      padding: 2px 10px; border-radius: 20px;
    }}

    /* ── Content sections ───────────────────────────────────── */
    .content-section {{
      padding: 24px 28px 20px;
      border-bottom: 1px solid var(--border);
      background: #fff;
    }}
    .section-header {{
      display: flex; align-items: flex-end; justify-content: space-between;
      padding-bottom: 11px;
      border-bottom: 2px solid var(--text-primary);
      margin-bottom: 16px;
    }}
    .section-title-group {{ display: flex; align-items: center; gap: 10px; }}
    .section-icon {{ display: none; }}
    .section-label {{
      font-weight: 900; font-size: 18px;
      color: var(--text-primary); letter-spacing: -0.5px;
    }}
    .section-count {{
      font-size: 11px; font-weight: 700; color: var(--text-muted);
      background: #f0f0f0; padding: 2px 9px; border-radius: 20px;
    }}
    .view-all {{
      font-size: 12px; font-weight: 700;
      color: var(--teal); text-decoration: none;
      transition: opacity .15s;
    }}
    .view-all:hover {{ opacity: 0.65; }}
    .view-all::after {{ content: " ↗"; }}

    /* ── Items grid ─────────────────────────────────────────── */
    .items-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    /* Card — editorial left-border accent, like arduino.cc news items */
    .item-card {{
      padding: 11px 14px 11px 12px;
      border: 1px solid var(--border);
      border-left: 3px solid transparent;
      border-radius: var(--radius);
      background: #fff;
      cursor: pointer;
      display: flex; align-items: flex-start; justify-content: space-between; gap: 10px;
      transition: border-left-color .15s, background .15s, border-color .15s;
      user-select: none;
    }}
    .item-card:hover {{
      border-left-color: var(--teal);
      background: var(--teal-bg);
      border-color: var(--teal-light);
    }}
    .item-card.selected {{
      border-left-color: var(--teal);
      border-color: var(--teal-light);
      background: var(--teal-bg);
    }}
    .item-body {{ flex: 1; min-width: 0; }}
    .item-title {{
      font-weight: 700; font-size: 12.5px; color: var(--text-primary);
      margin-bottom: 4px; line-height: 1.38;
    }}
    .item-meta {{ font-size: 11px; color: var(--text-muted); font-weight: 600; }}
    .item-actions {{
      display: flex; flex-direction: column;
      align-items: flex-end; gap: 7px; flex-shrink: 0;
    }}

    /* Tags — styled like arduino.cc category chips */
    .tag {{
      font-size: 9px; font-weight: 800; letter-spacing: 0.6px;
      padding: 2px 7px; border-radius: var(--radius-sm);
      white-space: nowrap; text-transform: uppercase;
    }}
    .checkbox {{
      width: 16px; height: 16px; border-radius: 4px;
      border: 1.5px solid #d0d0d0; background: #fff;
      display: flex; align-items: center; justify-content: center;
      color: #fff; font-size: 9px; flex-shrink: 0;
      transition: background .15s, border-color .15s;
    }}
    .item-card.selected .checkbox {{
      background: var(--teal); border-color: var(--teal);
    }}
    .item-card.selected .checkbox::after {{ content: "✓"; font-weight: 900; }}

    /* ── Social section ─────────────────────────────────────── */
    #social {{
      padding: 22px 28px;
      border-bottom: 1px solid var(--border);
      background: #fff;
    }}
    .social-header {{
      display: flex; align-items: flex-end; justify-content: space-between;
      padding-bottom: 11px; border-bottom: 2px solid var(--text-primary);
      margin-bottom: 14px;
    }}
    .social-icon {{ display: none; }}
    .social-label {{
      font-weight: 900; font-size: 18px;
      color: var(--text-primary); letter-spacing: -0.5px;
    }}
    .social-links {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .social-btn {{
      font-size: 12px; font-weight: 700;
      padding: 7px 16px;
      border: 1.5px solid var(--border);
      border-radius: var(--radius); color: var(--text-secondary);
      text-decoration: none; background: #fafafa;
      transition: border-color .15s, color .15s, background .15s;
    }}
    .social-btn:hover {{
      border-color: var(--teal); color: var(--teal); background: var(--teal-bg);
    }}

    /* ── Share panel ─────────────────────────────────────────── */
    #share-panel {{
      margin: 20px 28px 28px;
      background: #fafafa;
      border-radius: var(--radius);
      padding: 20px 22px;
      border: 1.5px solid var(--border);
    }}
    .share-header {{
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 14px;
    }}
    .share-title {{
      font-weight: 900; font-size: 15px;
      color: var(--text-primary); letter-spacing: -0.3px;
    }}
    .share-count {{ font-size: 12px; font-weight: 700; color: var(--text-muted); }}
    .share-count.active {{ color: var(--teal); }}
    .email-preview {{
      background: #fff; border: 1.5px solid var(--border);
      border-radius: var(--radius);
      padding: 12px 16px; font-size: 12.5px; font-family: inherit;
      color: #c0c0c0; margin-bottom: 14px; min-height: 80px;
      line-height: 1.9; white-space: pre-wrap;
      transition: border-color .2s;
    }}
    .email-preview.has-content {{
      color: var(--text-primary); border-color: var(--teal-light);
    }}
    .share-actions {{ display: flex; gap: 8px; }}
    .share-btn {{
      flex: 1; padding: 9px;
      border-radius: var(--radius);
      border: 1.5px solid var(--border); background: #fff;
      font-size: 12px; font-weight: 700; font-family: inherit; cursor: pointer;
      color: var(--text-secondary);
      transition: border-color .15s, color .15s, background .15s;
    }}
    .share-btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
    .share-btn:not(:disabled):hover {{
      border-color: var(--teal); color: var(--teal); background: var(--teal-bg);
    }}
    .share-btn-primary {{
      flex: 0 0 auto; padding: 9px 22px;
      border-radius: var(--radius); border: none;
      background: var(--teal); color: #fff;
      font-size: 12px; font-weight: 800; font-family: inherit; cursor: pointer;
      letter-spacing: 0.2px; transition: background .15s;
    }}
    .share-btn-primary:disabled {{ opacity: 0.4; cursor: not-allowed; }}
    .share-btn-primary:not(:disabled):hover {{ background: var(--teal-dark); }}
  </style>
</head>
<body>
<div id="app">

  <header class="hub-header">
    <div class="header-brand">
      <div class="brand-logo">A</div>
      <div>
        <div class="brand-name">Arduino UNO Q — Sales Hub</div>
        <div class="brand-sub">For the Arduino sales team</div>
      </div>
    </div>
    <div class="header-right">
      <nav class="nav-pills">
        {nav_pills}
      </nav>
      <button class="refresh-btn" id="btn-refresh" onclick="triggerRefresh()">↺ Refresh</button>
    </div>
  </header>
  <div class="hub-banner">
    <span class="hub-banner-text" id="last-updated">Content updated {escape(updated_str)}</span>
    <span class="hub-banner-badge">Sales Hub</span>
  </div>

  {docs_html}
  {blog_html}
  {projects_html}
  {video_html}

  <section id="social">
    <div class="social-header">
      <span class="social-label">Social channels</span>
      <a href="https://www.arduino.cc" target="_blank" rel="noreferrer" class="view-all">arduino.cc</a>
    </div>
    <div class="social-links">{social_links_html}</div>
  </section>

  <div id="share-panel">
    <div class="share-header">
      <span class="share-title">📤 Share with a customer</span>
      <span class="share-count" id="sel-count">0 items selected</span>
    </div>
    <div class="email-preview" id="email-preview">
      Select content above to share — a ready-to-send message will appear here.
    </div>
    <div class="share-actions">
      <button class="share-btn"       id="btn-links" onclick="copyLinks()"  disabled>Copy links</button>
      <button class="share-btn"       id="btn-email" onclick="copyEmail()"  disabled>Copy email message</button>
      <button class="share-btn-primary" id="btn-clear" onclick="clearAll()"   disabled>Clear selection</button>
    </div>
  </div>

</div>

<script>
  const selected = new Map();

  function toggleItem(card) {{
    const key  = card.dataset.key;
    const data = JSON.parse(key);
    if (selected.has(key)) {{ selected.delete(key); card.classList.remove("selected"); }}
    else                   {{ selected.set(key, data); card.classList.add("selected"); }}
    updatePanel();
  }}

  function updatePanel() {{
    const items = [...selected.values()];
    const count = items.length;
    document.getElementById("sel-count").textContent = count + " item" + (count !== 1 ? "s" : "") + " selected";
    document.getElementById("sel-count").classList.toggle("active", count > 0);
    const preview = document.getElementById("email-preview");
    if (count === 0) {{ preview.textContent = "Select content above to share — a ready-to-send message will appear here."; preview.classList.remove("has-content"); }}
    else             {{ preview.textContent = buildEmail(items); preview.classList.add("has-content"); }}
    ["btn-links", "btn-email", "btn-clear"].forEach(id => document.getElementById(id).disabled = count === 0);
  }}

  function buildEmail(items) {{
    const lines = items.map(i => "• " + i.title + "\\n  " + i.url).join("\\n");
    return "Hi,\\n\\nI wanted to share some resources about the Arduino UNO Q that you might find useful:\\n\\n" + lines + "\\n\\nLet me know if you have any questions!";
  }}

  function copyLinks()  {{ copyToClipboard([...selected.values()].map(i => i.title + ": " + i.url).join("\\n"), "btn-links", "Copy links"); }}
  function copyEmail()  {{ copyToClipboard(buildEmail([...selected.values()]), "btn-email", "Copy email message"); }}

  function copyToClipboard(text, btnId, label) {{
    const done = () => {{ const b = document.getElementById(btnId); b.textContent = "✓ Copied!"; setTimeout(() => b.textContent = label, 2000); }};
    navigator.clipboard.writeText(text).then(done).catch(() => {{
      const ta = Object.assign(document.createElement("textarea"), {{value: text, style: "position:fixed;opacity:0"}});
      document.body.appendChild(ta); ta.select(); document.execCommand("copy"); document.body.removeChild(ta); done();
    }});
  }}

  function clearAll() {{ selected.clear(); document.querySelectorAll(".item-card.selected").forEach(c => c.classList.remove("selected")); updatePanel(); }}

  // ── Refresh button ─────────────────────────────────────────────────────────
  function triggerRefresh() {{
    const btn = document.getElementById("btn-refresh");
    const sub = document.getElementById("last-updated");
    btn.disabled = true;
    btn.textContent = "↺ Refreshing…";
    sub.textContent = "Fetching latest content — this takes about 30 seconds…";
    fetch("/refresh", {{method:"POST"}})
      .then(r => r.json())
      .then(() => {{
        sub.textContent = "Refresh started — reloading in 35 seconds…";
        setTimeout(() => window.location.reload(), 35000);
      }})
      .catch(() => {{
        btn.disabled = false;
        btn.textContent = "↺ Refresh";
        sub.textContent = "Refresh failed — is the board online?";
      }});
  }}
</script>
</body>
</html>"""


def main() -> None:
    os.makedirs(WWW_DIR, exist_ok=True)
    html = build_html()
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    log.info("generate_html: wrote %s (%d bytes)", HTML_FILE, len(html))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
