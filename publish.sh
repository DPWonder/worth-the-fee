#!/bin/sh
# Checks every page, rebuilds, publishes to itsworththefee.com and tells Bing.
set -e
cd "$(dirname "$0")"
.venv/bin/python check.py
.venv/bin/python build.py
git add -A
git commit -q -m "${1:-Update site}" || echo "Nothing new to commit."
git push -q origin main
.venv/bin/python - <<'PY'
import json, urllib.request
urls = [l.strip() for l in open("urls.txt") if l.strip()]
key = "7c1e5b0a9d4f4e3aa6b2c8d91f0e4a57"
body = json.dumps({"host": "itsworththefee.com", "key": key,
                   "keyLocation": f"https://itsworththefee.com/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
print("Search engines notified:", urllib.request.urlopen(req).status, f"({len(urls)} pages)")
PY
echo "Published. The live site updates in about a minute."
