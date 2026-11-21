#!/usr/bin/env python3
"""Add or update a referral link. Run:  .venv/bin/python add_link.py
It asks five questions, saves links.json and rebuilds the site.
The link then shows on /offers/ and "How we earn" at once.
To show it at the end of a page, add its key to that page's `cta:` line in content/."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
path = ROOT / "links.json"
links = json.loads(path.read_text())


def ask(q, default=""):
    a = input(f"{q}{' [' + default + ']' if default else ''}: ").strip()
    return a or default


print("Current links:", ", ".join(links) or "none")
key = re.sub(r"[^a-z0-9]", "", ask("Short key, lowercase, one word (example: venturex)").lower())
if not key:
    sys.exit("No key given.")
old = links.get(key, {})
name = ask("Product name as readers know it", old.get("name", ""))
url = ask("Your referral link", old.get("url", ""))
if not url.startswith("https://"):
    sys.exit("The link must start with https://")
button = ask("Button text", old.get("button", f"See the {name} offer"))
offer = ask("What the reader gets (say the date you checked; offers change)", old.get("offer", ""))
we_get = ask("What you get", old.get("we_get", "If you sign up, the person who runs this site earns a reward."))
if not (name and offer):
    sys.exit("Name and offer are needed.")
links[key] = {"name": name, "url": url, "button": button, "offer": offer, "we_get": we_get}
path.write_text(json.dumps(links, indent=2, ensure_ascii=False) + "\n")
subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
print(f"\nSaved '{key}'. It is on the Offers page in the local build.")
print("Check the program's terms allow the link on a public website, then run ./publish.sh to put it live.")
