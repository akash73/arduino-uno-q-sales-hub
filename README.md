# Arduino UNO Q — Sales Hub

A web dashboard that aggregates all public content about the Arduino UNO Q product — docs, blog posts, community projects, and YouTube videos — into a single page for the Arduino sales team.

## What it does

- Scrapes and caches content from all UNO Q public sources once per day at 06:00
- Serves a local web page (port 8080) accessible from any browser on the office network
- Lets sales reps select items and copy a ready-to-send email message to share with customers

## Content sources

| Section | Source | Method |
|---|---|---|
| Documentation | docs.arduino.cc/hardware/uno-q | Scraping |
| Blog posts | blog.arduino.cc (UNO Q + AppLab feeds) | RSS |
| Community projects | projecthub.arduino.cc | Scraping |
| YouTube videos | Playlist PLT6rF_I5kknOOmiHEU8onj1X0Ad5BzaFr | YouTube Data API v3 |
| Social channels | Static links | — |

## Setup

1. Open the app in Arduino App Lab
2. Edit `python/config.py` and set your `YOUTUBE_API_KEY`
3. Click **Run** — the first fetch runs automatically on startup
4. Open `http://<board-ip>:8080` from any browser on the network

## Manual refresh

POST to `/refresh` or click the **Refresh now** button in the page header to trigger an immediate re-fetch of all sources.

## YouTube API key

Get a free key at https://console.cloud.google.com — enable **YouTube Data API v3** and create an API key. Until the key is set, the YouTube section falls back to the static placeholder data.
