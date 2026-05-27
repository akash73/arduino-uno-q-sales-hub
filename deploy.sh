#!/bin/bash
# Deploy Sales Hub to Arduino UNO Q
# Usage: bash deploy.sh

set -e
APP="/home/arduino/ArduinoApps/arduino-uno-q-sales-hub"
SRC="/Users/andrea/Documents/antigravity/sales hub/Sales Hub/arduino-uno-q-sales-hub"

echo "→ Pushing Python files..."
adb push "$SRC/python/main.py"                          "$APP/python/main.py"
adb push "$SRC/python/generate_html.py"                 "$APP/python/generate_html.py"
adb push "$SRC/python/fetchers/fetch_docs.py"           "$APP/python/fetchers/fetch_docs.py"

echo "→ Pushing corrected docs.json..."
adb push "$SRC/python/data/docs.json"                   "$APP/python/data/docs.json"

echo "→ Removing cached index.html..."
adb shell rm -f "$APP/python/www/index.html"

echo "→ Restarting app process..."
adb shell "pkill -f 'python.*main.py' || true"

echo "→ Waiting for restart..."
sleep 5

echo "→ Done! Opening page..."
open "http://10.130.22.178:8080"
