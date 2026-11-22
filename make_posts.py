#!/usr/bin/env python3
"""Writes posts/queue.csv: one ready-to-post row per page for the brand's social profiles.
Order: calculator first, then comparisons, Rakuten stores, the rest. Each row carries the disclosure."""
import csv
from pathlib import Path

from build import SITE, TOPICS, parse

ROOT = Path(__file__).parent
TAG = "We earn from referral links on our site."
pages = [parse(p) for p in sorted((ROOT / "content").glob("*.md"))]
rank = {"compare": 0, "rakuten": 1, "points": 2, "chase": 3, "amex": 4, "amexcards": 5, "trips": 6}
pages.sort(key=lambda p: (rank.get(p["topic"], 9), p["slug"]))
rows = [{"url": SITE + "fee-calculator/", "image": SITE + "og/default.png", "board": "Annual fee calculator",
         "title": "Annual fee calculator: is the card worth it for you?",
         "pin_text": f"Score each credit by what you would really use and see what the fee costs you. {TAG}",
         "short_post": f"Is a $895 card worth it for you? Score each credit honestly and see the real cost. {SITE}fee-calculator/ ({TAG})"}]
for p in pages:
    url = SITE + p["slug"] + "/"
    rows.append({"url": url, "image": f'{SITE}og/{p["slug"]}.png', "board": TOPICS[p["topic"]]["label"],
                 "title": p["title"][:100], "pin_text": f'{p["description"]} Sources and date checked on the page. {TAG}',
                 "short_post": f'{p["title"]} {p["description"]} {url} ({TAG})'})
out = ROOT / "posts"
out.mkdir(exist_ok=True)
with open(out / "queue.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(len(rows), "posts ->", out / "queue.csv")
