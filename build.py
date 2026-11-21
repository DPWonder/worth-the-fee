#!/usr/bin/env python3
"""Builds the Worth the Fee site: content/*.md -> docs/ (static HTML)."""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
BASE = "/worth-the-fee/"
SITE = "https://dpwonder.github.io/worth-the-fee/"
NAME = "Worth the Fee"
TAGLINE = "Straight answers on whether a travel card or programme is worth it for you."
INDEXNOW_KEY = "7c1e5b0a9d4f4e3aa6b2c8d91f0e4a57"
ANALYTICS = (ROOT / "analytics.html").read_text() if (ROOT / "analytics.html").exists() else ""

LINKS = json.loads((ROOT / "links.json").read_text())
TOPICS = [
    ("amex", "Amex Platinum"),
    ("chase", "Chase Sapphire"),
    ("rakuten", "Rakuten cash back"),
]


def esc(s):
    return html.escape(s, quote=True)


def parse(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"no frontmatter: {path}")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    meta["cta"] = [c.strip() for c in meta.get("cta", "").split(",") if c.strip()]
    body = m.group(2).strip()
    # drop a leading H1 that repeats the title
    body = re.sub(r"^# .*\n+", "", body)
    meta["body"] = body
    return meta


def faq_pairs(body):
    """Pull question/answer pairs out of the 'Quick answers' section."""
    m = re.search(r"^## Quick answers\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    if not m:
        return []
    block = m.group(1).strip()
    pairs = []
    for q, a in re.findall(r"\*\*(.+?\?)\*\*\s*\n?(.+?)(?=\n\s*\n\*\*|\n\*\*|\Z)", block, re.S):
        pairs.append((q.strip(), " ".join(a.split())))
    if not pairs:
        for q, a in re.findall(r"^### (.+?\?)\s*\n(.+?)(?=^### |\Z)", block, re.S | re.M):
            pairs.append((q.strip(), " ".join(a.split())))
    return pairs


def plain(md_text):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md_text)
    return re.sub(r"[*_`]", "", t)


def cta_html(keys):
    if not keys:
        return ""
    boxes = []
    for k in keys:
        link = LINKS[k]
        boxes.append(
            f'<div class="cta"><h3>{esc(link["name"])}</h3>'
            f'<p>{esc(link["offer"])}</p>'
            f'<p><a class="btn" rel="sponsored nofollow" href="{BASE}go/{k}/">{esc(link["button"])}</a></p>'
            f'<p class="fine">This is a referral link. {esc(link["we_get"])} It costs you nothing extra.</p></div>'
        )
    return '<section class="ctas" aria-label="Referral links">' + "".join(boxes) + "</section>"


def layout(title, description, content, path, extra_head="", noindex=False):
    canonical = SITE + path
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="{BASE}style.css">
{extra_head}
</head>
<body>
<header class="site"><a class="brand" href="{BASE}">{NAME}</a>
<nav><a href="{BASE}">All questions</a><a href="{BASE}about/">How this site works</a></nav></header>
<main>
{content}
</main>
<footer class="site">
<p>{NAME} is run by one cardholder, not by a bank. Some links are referral links: if you sign up through one, the person who runs this site earns points or cash. That never changes what a page says. <a href="{BASE}about/">How this site works</a>.</p>
<p>Information only, not financial, tax or legal advice. Offers and rules change; check the provider's page before you decide.</p>
</footer>
{ANALYTICS}
</body>
</html>
"""


def write(path, text):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("")
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)

    pages = [parse(p) for p in sorted((ROOT / "content").glob("*.md"))]
    md = markdown.Markdown(extensions=["tables", "sane_lists"])

    for pg in pages:
        md.reset()
        body_html = md.convert(pg["body"])
        body_html = body_html.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
        body_html = re.sub(r'<a href="(https?://[^"]+)"', r'<a rel="noopener" href="\1"', body_html)
        checked = pg.get("checked", str(date.today()))
        nice = date.fromisoformat(checked).strftime("%B %-d, %Y")
        path = pg["slug"] + "/"
        ld = [{
            "@context": "https://schema.org", "@type": "Article",
            "headline": pg["title"], "description": pg["description"],
            "dateModified": checked, "datePublished": checked,
            "mainEntityOfPage": SITE + path,
            "author": {"@type": "Organization", "name": NAME},
            "publisher": {"@type": "Organization", "name": NAME},
        }]
        pairs = faq_pairs(pg["body"])
        if pairs:
            ld.append({
                "@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": plain(q),
                                "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in pairs],
            })
        head = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld)
        disclosure = ""
        if pg["cta"]:
            disclosure = '<p class="disclosure">This page has a referral link at the end. The person who runs this site earns points or cash if you sign up through it.</p>'
        content = (
            f'<article><h1>{esc(pg["title"])}</h1>'
            f'<p class="meta">Facts checked {nice}</p>{disclosure}'
            f'{body_html}{cta_html(pg["cta"])}</article>'
        )
        write(path + "index.html", layout(f'{pg["title"]} | {NAME}', pg["description"], content, path, head))

    # home
    groups = []
    for key, label in TOPICS:
        items = [p for p in pages if p["cta"] and p["cta"][0] == key]
        if not items:
            continue
        lis = "".join(
            f'<li><a href="{BASE}{p["slug"]}/">{esc(p["title"])}</a><span>{esc(p["description"])}</span></li>'
            for p in items)
        groups.append(f"<h2>{esc(label)}</h2><ul class=\"qlist\">{lis}</ul>")
    home = f'<section class="hero"><h1>{NAME}</h1><p>{TAGLINE}</p><p class="meta">Each page answers one question, shows its sources, and says when the answer is no.</p></section>' + "".join(groups)
    write("index.html", layout(f"{NAME}: is that travel card or programme worth it?", TAGLINE, home, ""))

    # about
    rows = "".join(
        f'<tr><td>{esc(v["name"])}</td><td>{esc(v["we_get"])}</td></tr>' for v in LINKS.values())
    about = f"""<article><h1>How this site works</h1>
<p>{NAME} answers narrow questions about travel cards and travel programmes: the kind where the honest answer depends on how you travel, and is sometimes "no, skip it".</p>
<h2>Who runs it</h2>
<p>One person who holds the American Express Platinum Card and a Chase Sapphire card, and uses Rakuten. It is not run by a bank, a card issuer or a comparison company.</p>
<h2>How it earns</h2>
<p>Some pages end with a referral link. These are the ordinary refer-a-friend links that the companies give their own customers. If you sign up through one, this happens:</p>
<div class="tablewrap"><table><thead><tr><th>Link</th><th>What the site's owner gets</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>You pay nothing extra, and you can always go to the company's own site instead. A referral link never changes what a page says: several pages tell most readers not to sign up.</p>
<h2>How facts are checked</h2>
<p>Every number comes from the provider's own page or from a named source listed at the bottom of the page, with the date it was checked. Card offers, fees and local rules change often. Before you decide anything, read the provider's current terms.</p>
<h2>What this site is not</h2>
<p>It is information, not financial, tax or legal advice. It does not know your finances. Welcome offers vary from person to person, and the issuer decides who is approved.</p></article>"""
    write("about/index.html", layout(f"How this site works | {NAME}", "Who runs Worth the Fee, how it earns from referral links, and how facts are checked.", about, "about/"))

    # redirects
    for k, v in LINKS.items():
        url = esc(v["url"])
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow"><title>Opening {esc(v["name"])}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{BASE}style.css">
<script>window.__go="{k}";</script>{ANALYTICS}
<meta http-equiv="refresh" content="1;url={url}"></head>
<body><main><p>Opening {esc(v["name"])}. If nothing happens, <a rel="sponsored nofollow" href="{url}">continue here</a>.</p></main></body></html>"""
        write(f"go/{k}/index.html", page)

    write("404.html", layout(f"Page not found | {NAME}", "Page not found.", f'<article><h1>Page not found</h1><p><a href="{BASE}">See all questions</a>.</p></article>', "404.html", noindex=True))

    # sitemap, llms.txt
    today = str(date.today())
    urls = [("", today), ("about/", today)] + [(p["slug"] + "/", p.get("checked", today)) for p in pages]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    llms = f"# {NAME}\n\n> {TAGLINE} Each page answers one question, cites its sources and gives the date it was checked. Some pages end with a disclosed referral link.\n\n## Questions\n\n" + "".join(
        f'- [{p["title"]}]({SITE}{p["slug"]}/): {p["description"]}\n' for p in pages)
    write("llms.txt", llms)
    (ROOT / "urls.txt").write_text("\n".join(SITE + u for u, _ in urls) + "\n")
    print(f"built {len(pages)} pages -> {OUT}")


if __name__ == "__main__":
    build()
