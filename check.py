#!/usr/bin/env python3
"""Checks every page in content/ against the site's writing rules. Exit 1 on any problem."""
import re
import sys
from pathlib import Path

from build import LINKS, TOPICS, faq_pairs, parse

ROOT = Path(__file__).parent
HYPE = r"\b(best|amazing|ultimate|unlock|unlocks|game-chang\w*|must-have|hack|hacks|no-brainer|incredible)\b"
BRITISH = r"\b(programme|programmes|traveller|travellers|authorised|cheque|centre|licence|favour|colour|cancelled|organis\w+)\b"
BAD_URL = r"(referyourchasecard|rakuten\.com/r/|americanexpress\.com/en-us/referral/|airbnb\.com/rp/)"

pages = [parse(p) for p in sorted((ROOT / "content").glob("*.md"))]
slugs = {p["slug"] for p in pages}
problems = []
for p in pages:
    s, body = p["slug"], p["body"]

    def bad(msg):
        problems.append(f"{s}: {msg}")

    for k in ("title", "slug", "description", "checked"):
        if not p.get(k):
            bad(f"missing {k}")
    if len(p.get("description", "")) > 160:
        bad(f"description {len(p['description'])} chars")
    if not p["cta"]:
        bad("no cta")
    words = len(body.split())
    # the rate tracker is written by rates.py and grows by one table row per tracked store
    if (words < 430 or words > 1300) and s != "rakuten-cash-back-rates-today-by-store":
        bad(f"{words} words")
    # strip source list and link targets before word checks
    main = body.split("## Sources")[0]
    text = re.sub(r"\]\([^)]*\)", "]", main)
    text = re.sub(r"\bBest (Buy|Offer|Western)\b", "STORE", text)
    for m in re.finditer(HYPE, text, re.I):
        ctx = text[max(0, m.start() - 30):m.end() + 20].replace("\n", " ")
        bad(f"hype word '{m.group(0)}' in: …{ctx}…")
    for m in re.finditer(BRITISH, text, re.I):
        bad(f"British spelling '{m.group(0)}'")
    if re.search(BAD_URL, body):
        bad("contains a referral URL")
    if re.search(r"\b(click here|apply now|sign up today|you should apply)\b", text, re.I):
        bad("call to action in body")
    if re.search(r"\b(I|we) (tested|tried|used|recommend)\b", text):
        bad("first-person claim")
    if "## Sources" not in body:
        bad("no Sources section")
    elif len(re.findall(r"\]\(https?://", body.split("## Sources")[1])) < 2:
        bad("fewer than 2 sources")
    if len(faq_pairs(body)) != 3:
        bad(f"{len(faq_pairs(body))} quick answers parsed")
    if "not financial advice" not in body:
        bad("no advice disclaimer")
    for target in re.findall(r"\]\((/[^)#]*)\)", body):
        t = target.strip("/")
        if t not in slugs and t not in {x["slug"] for x in TOPICS.values()} | {"about", "disclosure", "how-we-check-facts", "offers"}:
            bad(f"broken internal link {target}")
    first = body.split("\n\n", 1)[0]
    if first.startswith("#") or len(first.split()) < 12:
        bad("first paragraph is not a standalone answer")

print(f"{len(pages)} pages checked, {len(problems)} problems")
for x in problems:
    print(" -", x)
sys.exit(1 if problems else 0)
