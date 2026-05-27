# ─────────────────────────────────────────────
#  Arduino UNO Q — Sales Hub  •  Configuration
# ─────────────────────────────────────────────
import os

# ── YouTube ──────────────────────────────────
# Get a free key at https://console.cloud.google.com
# Enable "YouTube Data API v3" → Create credentials → API key
YOUTUBE_API_KEY    = "AIzaSyDejNnCetqMy0WNRLtPN29vQ29AMRFd5rM"
YOUTUBE_PLAYLIST_ID = "PLT6rF_I5kknOOmiHEU8onj1X0Ad5BzaFr"
YOUTUBE_MAX_RESULTS = 10

# ── Docs ──────────────────────────────────────
DOCS_URL       = "https://docs.arduino.cc/hardware/uno-q/"
DOCS_MAX_ITEMS = 10

# ── Blog RSS feeds ────────────────────────────
BLOG_FEEDS = [
    {"url": "https://blog.arduino.cc/category/arduino/uno-q/feed/",   "tag": "UNO Q"},
    {"url": "https://blog.arduino.cc/category/arduino/app-lab/feed/", "tag": "AppLab"},
]
BLOG_MAX_ITEMS = 10

# ── Project Hub ───────────────────────────────
PROJECTHUB_URLS = [
    "https://projecthub.arduino.cc/?q=uno+q",
    "https://projecthub.arduino.cc/?q=uno-q",
]
PROJECTHUB_MAX_ITEMS = 10

# ── Social channels (static — no API needed) ─
SOCIAL_LINKS = [
    {"label": "YouTube",   "url": "https://www.youtube.com/arduino"},
    {"label": "Instagram", "url": "https://www.instagram.com/arduino.cc/"},
    {"label": "LinkedIn",  "url": "https://www.linkedin.com/company/arduino/"},
    {"label": "Facebook",  "url": "https://www.facebook.com/official.arduino"},
]

# ── Paths (all relative to python/) ──────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "data")
WWW_DIR   = os.path.join(BASE_DIR, "www")
HTML_FILE = os.path.join(WWW_DIR, "index.html")

# ── Web server ────────────────────────────────
SERVER_PORT = 8080

# ── Daily refresh time (24-h HH:MM) ──────────
REFRESH_TIME = "06:00"
