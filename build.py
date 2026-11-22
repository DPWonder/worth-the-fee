#!/usr/bin/env python3
"""Builds the Worth the Fee site: content/*.md -> docs/ (static HTML)."""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

import markdown

import og

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
DOMAIN = "itsworththefee.com"
BASE = "/"
SITE = f"https://{DOMAIN}/"
NAME = "Worth the Fee"
EMAIL = f"hello@{DOMAIN}"
TAGLINE = "Straight answers on whether a travel card or program is worth it for you."
INDEXNOW_KEY = "7c1e5b0a9d4f4e3aa6b2c8d91f0e4a57"
ANALYTICS = (ROOT / "analytics.html").read_text() if (ROOT / "analytics.html").exists() else ""
VERIFY = (ROOT / "verify.html").read_text() if (ROOT / "verify.html").exists() else ""

LINKS = json.loads((ROOT / "links.json").read_text())
TOPICS = {
    "amex": {"slug": "amex-platinum", "label": "Amex Platinum",
             "blurb": "The $895 card: who gets their money back, and who does not."},
    "chase": {"slug": "chase-sapphire", "label": "Chase Sapphire",
              "blurb": "Preferred or Reserve, for people who travel a few times a year."},
    "amexcards": {"slug": "amex-cards", "label": "Other Amex cards", "nav": "Amex cards",
                  "blurb": "Gold, Delta, Hilton, Marriott and Blue Cash: which fee pays off, and for whom."},
    "rakuten": {"slug": "rakuten", "label": "Rakuten",
                "blurb": "Cash back or Amex points, and how the sign-up bonus really works."},
    "trips": {"slug": "hawaii-and-golf-trips", "label": "Hawaii & golf trips", "nav": "Trips",
              "blurb": "Points, lounges, hotel credits and bag fees for a Hawaii week or a golf trip."},
    "compare": {"slug": "card-comparisons", "label": "Card comparisons", "nav": "Comparisons",
                "blurb": "Two cards side by side, with the sums for the way you spend and travel."},
    "points": {"slug": "using-points", "label": "Using points", "nav": "Points",
               "blurb": "What Amex and Chase points are worth, where to move them, and when to pay cash."},
}

LIVE_TOPICS = set()

# Fee calculator data: (credit, dollars per year at face value, note). Sources: the credit pages in content/.
CALC = {
    "amex": {"card": "Amex Platinum", "fee": 895, "more": "amex-platinum-credits-real-value", "credits": [
        ("Hotel credit (prepaid Fine Hotels + Resorts, The Hotel Collection or Airbnb Luxe via Amex Travel)", 600, "$300 each half-year"),
        ("Resy restaurants", 400, "$100 per quarter"),
        ("Digital entertainment (streaming)", 300, "$25 per month"),
        ("lululemon", 300, "$75 per quarter"),
        ("Equinox membership", 300, "yearly"),
        ("CLEAR+ membership", 219, "yearly"),
        ("Airline incidental fees", 200, "one airline you pick; not tickets"),
        ("Uber Cash", 200, "$15 per month, $35 in December"),
        ("Oura ring", 200, "hardware only"),
        ("Walmart+ membership", 155, "$12.95 per month plus tax"),
        ("Uber One membership", 120, "yearly"),
        ("Global Entry or TSA PreCheck", 30, "$120 once every 4 years"),
    ]},
    "reserve": {"card": "Chase Sapphire Reserve", "fee": 795, "cta": "chase", "more": "chase-sapphire-reserve-credits-real-value", "credits": [
        ("Travel credit", 300, "any travel purchase, each account year"),
        ("The Edit hotels", 500, "$250 per prepaid stay of two nights or more"),
        ("Dining (Exclusive Tables restaurants on OpenTable)", 300, "$150 each half-year"),
        ("StubHub and viagogo", 300, "$150 each half-year, through 2027"),
        ("DoorDash promos", 420, "$35 a month in three separate promos"),
        ("DashPass membership", 120, "Chase's stated value"),
        ("Lyft", 120, "$10 a month, through September 2027"),
        ("Peloton membership", 120, "$10 a month, through 2027"),
        ("Apple TV and Apple Music", 324, "Chase's stated value"),
        ("Global Entry, TSA PreCheck or NEXUS", 30, "$120 once every 4 years"),
    ]},
    "preferred": {"card": "Chase Sapphire Preferred", "fee": 95, "cta": "chase", "more": "chase-sapphire-preferred-one-trip-a-year", "credits": [
        ("Hotel credit (hotel stays bought through Chase Travel)", 100, "each account year"),
        ("DashPass membership", 120, "only if you would pay for it"),
    ]},
}

LOGO = ('<svg class="mark" viewBox="0 0 32 32" width="28" height="28" aria-hidden="true">'
        '<rect width="32" height="32" rx="9" fill="var(--ink)"/>'
        '<path d="M8 17.2l5 5L24.5 10" fill="none" stroke="var(--gold)" stroke-width="3.4" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>')
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="9" '
           'fill="#12233f"/><path d="M8 17.2l5 5L24.5 10" fill="none" stroke="#f4b740" stroke-width="3.4" '
           'stroke-linecap="round" stroke-linejoin="round"/></svg>')


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
    body = re.sub(r"^# .*\n+", "", m.group(2).strip())
    meta["body"] = body
    meta["topic"] = meta.get("topic") or (meta["cta"][0] if meta["cta"] else "amex")
    if meta["topic"] not in TOPICS:
        raise SystemExit(f"unknown topic {meta['topic']} in {path}")
    for c in meta["cta"]:
        if c not in LINKS:
            raise SystemExit(f"unknown cta {c} in {path}")
    meta["minutes"] = max(2, round(len(body.split()) / 220))
    return meta


def faq_pairs(body):
    m = re.search(r"^## Quick answers\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    if not m:
        return []
    block = m.group(1).strip()
    pairs = [(q.strip(), " ".join(a.split())) for q, a in
             re.findall(r"\*\*(.+?\?)\*\*\s*\n?(.+?)(?=\n\s*\n\*\*|\n\*\*|\Z)", block, re.S)]
    if not pairs:
        pairs = [(q.strip(), " ".join(a.split())) for q, a in
                 re.findall(r"^### (.+?\?)\s*\n(.+?)(?=^### |\Z)", block, re.S | re.M)]
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
            f'<div class="cta"><p class="eyebrow">Referral link</p><h3>{esc(link["name"])}</h3>'
            f'<p>{esc(link["offer"])}</p>'
            f'<p><a class="btn" rel="sponsored nofollow" data-go="{k}" href="{BASE}go/{k}/">{esc(link["button"])}</a></p>'
            f'<p class="fine">{esc(link["we_get"])} It costs you nothing extra. '
            f'<a href="{BASE}disclosure/">How we earn</a>.</p></div>'
        )
    return '<section class="ctas" aria-label="Referral links">' + "".join(boxes) + "</section>"


def mini_cta(keys):
    if not keys:
        return ""
    links = " ".join(
        f'<a class="btn small" rel="sponsored nofollow" data-go="{k}" data-pos="top" href="{BASE}go/{k}/">{esc(LINKS[k]["button"])}</a>'
        for k in keys)
    return (f'<p class="minicta"><span>Referral link{"s" if len(keys) > 1 else ""}: we earn if you sign up. '
            f'Read the page first.</span> {links}</p>')


def calc_link(pg):
    if not ({"amex", "chase"} & set(pg["cta"])):
        return ""
    anchor = "#amex" if pg["cta"][0] == "amex" else "#preferred"
    return (f'<p class="calclink">Not sure the fee pays off? <a href="{BASE}fee-calculator/{anchor}">Run your own numbers in the '
            f'annual fee calculator</a>.</p>')


def layout(title, description, content, path, extra_head="", noindex=False, og_type="website", image="og/default.png"):
    canonical = SITE + path
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    live = [t for k, t in TOPICS.items() if k in LIVE_TOPICS]
    topic_nav = "".join(f'<a href="{BASE}{t["slug"]}/">{esc(t.get("nav", t["label"]))}</a>' for t in live)
    topic_foot = "".join(f'<li><a href="{BASE}{t["slug"]}/">{esc(t["label"])}</a></li>' for t in live)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
{robots}{VERIFY}
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}{image}">
<link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="{BASE}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}style.css">
{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap bar">
<a class="brand" href="{BASE}">{LOGO}<span>{NAME}</span></a>
<nav aria-label="Topics">{topic_nav}<a class="navoffers" href="{BASE}offers/">Offers</a></nav>
</div></header>
<main id="main">
{content}
</main>
<footer class="site"><div class="wrap">
<div class="fcols">
<div><a class="brand" href="{BASE}">{LOGO}<span>{NAME}</span></a>
<p>{TAGLINE}</p></div>
<div><h4>Topics</h4><ul>{topic_foot}</ul></div>
<div><h4>The site</h4><ul>
<li><a href="{BASE}about/">About</a></li>
<li><a href="{BASE}offers/">Current referral offers</a></li>
<li><a href="{BASE}fee-calculator/">Annual fee calculator</a></li>
<li><a href="{BASE}how-we-check-facts/">How we check facts</a></li>
<li><a href="{BASE}disclosure/">How we earn</a></li>
<li><a href="{BASE}privacy/">Privacy</a></li>
<li><a href="{BASE}contact/">Contact</a></li></ul></div>
</div>
<p class="legal"><strong>Disclosure:</strong> {NAME} is independent and is not a bank or card issuer. Some pages contain referral links. If you sign up through one, we earn points or cash from that company. It does not change what a page says, and it costs you nothing extra.</p>
<p class="legal">The content here is information only and is not financial, tax or legal advice. Offers, fees and rules change. Check the provider's own page before you decide. Opinions are ours alone and have not been reviewed or approved by any company mentioned.</p>
<p class="legal">&copy; {date.today().year} {NAME}</p>
</div></footer>
{ANALYTICS}
</body>
</html>
"""


def write(path, text):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def page_md(pg):
    return (f'# {pg["title"]}\n\nSource: {SITE}{pg["slug"]}/\nFacts checked: {pg.get("checked", "")}\n'
            f'Publisher: {NAME} (independent; some pages end with a disclosed referral link)\n\n{pg["body"]}\n')


def qcard(p):
    t = TOPICS[p["topic"]]
    return (f'<a class="qcard" href="{BASE}{p["slug"]}/"><span class="tag">{esc(t["label"])}</span>'
            f'<strong>{esc(p["title"])}</strong><span class="desc">{esc(p["description"])}</span>'
            f'<span class="more">Read the answer &rarr;</span></a>')


def simple_page(path, title, description, body_html):
    content = f'<div class="wrap narrow"><article class="prose"><h1>{esc(title)}</h1>{body_html}</article></div>'
    write(path + "index.html", layout(f"{title} | {NAME}", description, content, path))


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("")
    (OUT / "CNAME").write_text(DOMAIN + "\n")
    (OUT / "favicon.svg").write_text(FAVICON)
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    for extra in (ROOT / "static").glob("*") if (ROOT / "static").exists() else []:
        shutil.copy(extra, OUT / extra.name)

    pages = [parse(p) for p in sorted((ROOT / "content").glob("*.md"))]
    (OUT / "og").mkdir()
    shutil.copy(og.make("default", "Is that travel card or program worth the fee?", "Independent. Sourced. Dated."), OUT / "og" / "default.png")
    for p in pages:
        shutil.copy(og.make(p["slug"], p["title"], TOPICS[p["topic"]]["label"]), OUT / "og" / (p["slug"] + ".png"))
    slugs = [p["slug"] for p in pages]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        raise SystemExit(f"duplicate slugs: {dupes}")
    LIVE_TOPICS.update(p["topic"] for p in pages)
    md = markdown.Markdown(extensions=["tables", "sane_lists"])
    today = str(date.today())

    # article pages
    for pg in pages:
        md.reset()
        parts = pg["body"].split("\n\n", 1)
        answer_html = md.convert(parts[0])
        md.reset()
        body_html = md.convert(parts[1] if len(parts) > 1 else "")
        body_html = body_html.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
        body_html = re.sub(r'<a href="(https?://[^"]+)"', r'<a rel="noopener" target="_blank" href="\1"', body_html)
        checked = pg.get("checked", today)
        nice = date.fromisoformat(checked).strftime("%B %-d, %Y")
        path = pg["slug"] + "/"
        topic = TOPICS[pg["topic"]]
        ld = [{
            "@context": "https://schema.org", "@type": "Article",
            "headline": pg["title"], "description": pg["description"],
            "dateModified": checked, "datePublished": checked, "image": SITE + "og/" + pg["slug"] + ".png",
            "mainEntityOfPage": SITE + path,
            "author": {"@type": "Organization", "name": NAME, "url": SITE + "about/"},
            "publisher": {"@type": "Organization", "name": NAME, "url": SITE},
        }, {
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": topic["label"], "item": SITE + topic["slug"] + "/"},
                {"@type": "ListItem", "position": 3, "name": pg["title"], "item": SITE + path},
            ]}]
        pairs = faq_pairs(pg["body"])
        if pairs:
            ld.append({
                "@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": plain(q),
                                "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in pairs],
            })
        head = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld)
        same = [p for p in pages if p["topic"] == pg["topic"]]
        i = same.index(pg)
        related = (same[i + 1:] + same[:i])[:6]
        rel_html = ""
        if related:
            rel_html = '<section class="related"><h2>Related questions</h2><div class="qgrid">' + "".join(qcard(p) for p in related) + "</div></section>"
        disclosure = ""
        if pg["cta"]:
            disclosure = (f'<p class="disclosure">This page contains a referral link. We earn points or cash if you sign up '
                          f'through it. <a href="{BASE}disclosure/">How we earn</a>.</p>')
        content = (
            f'<div class="wrap narrow"><nav class="crumbs" aria-label="Breadcrumb"><a href="{BASE}">Home</a> <span>/</span> '
            f'<a href="{BASE}{topic["slug"]}/">{esc(topic["label"])}</a></nav>'
            f'<article class="prose"><h1>{esc(pg["title"])}</h1>'
            f'<p class="meta"><span>Facts checked {nice}</span><span>{pg["minutes"]} min read</span>'
            f'<span><a href="{BASE}how-we-check-facts/">How we check facts</a></span></p>'
            f'{disclosure}<div class="answer"><p class="eyebrow">The short answer</p>{answer_html}</div>{mini_cta(pg["cta"])}{calc_link(pg)}'
            f'{body_html}{cta_html(pg["cta"])}</article>{rel_html}</div>'
        )
        write(path + "index.html", layout(f'{pg["title"]} | {NAME}', pg["description"], content, path,
                                          head + f'<link rel="alternate" type="text/markdown" href="{BASE}{path}index.md">',
                                          og_type="article", image=f'og/{pg["slug"]}.png'))
        write(path + "index.md", page_md(pg))

    # topic hubs
    for key, t in TOPICS.items():
        items = [p for p in pages if p["topic"] == key]
        if not items:
            continue
        shorts = ""
        for p in items:
            md.reset()
            shorts += (f'<h3><a href="{BASE}{p["slug"]}/">{esc(p["title"])}</a></h3>'
                       + md.convert(p["body"].split("\n\n", 1)[0]))
        ld = {"@context": "https://schema.org", "@type": "ItemList", "name": t["label"],
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["title"], "url": SITE + p["slug"] + "/"}
                                  for i, p in enumerate(items)]}
        content = (f'<div class="wrap"><section class="hubhead"><p class="eyebrow">Topic</p><h1>{esc(t["label"])}</h1>'
                   f'<p class="lede">{esc(t["blurb"])}</p></section>'
                   f'<div class="qgrid">{"".join(qcard(p) for p in items)}</div></div>'
                   f'<div class="wrap narrow"><section class="prose shorts"><h2>{esc(t["label"])}: every short answer on one page</h2>'
                   f'<p class="fine">Each answer links to its full page, with sources and the date it was checked. '
                   f'This is information, not financial advice.</p>{shorts}</section></div>')
        write(t["slug"] + "/index.html", layout(f'{t["label"]}: is it worth it? | {NAME}', t["blurb"], content, t["slug"] + "/",
                                                f'<script type="application/ld+json">{json.dumps(ld)}</script>'))

    # home
    newest = sorted(pages, key=lambda p: (p.get("checked", ""), (ROOT / "content" / (p["slug"] + ".md")).stat().st_mtime), reverse=True)
    items = "".join(
        f"<item><title>{esc(p['title'])}</title><link>{SITE}{p['slug']}/</link><guid>{SITE}{p['slug']}/</guid>"
        f"<description>{esc(p['description'])}</description>"
        f"<pubDate>{date.fromisoformat(p.get('checked', today)).strftime('%a, %d %b %Y')} 00:00:00 GMT</pubDate></item>\n"
        for p in newest[:30])
    write("feed.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{NAME}</title>'
                      f"<link>{SITE}</link><description>{esc(TAGLINE)}</description>\n{items}</channel></rss>\n")
    tcards = "".join(
        f'<a class="tcard" href="{BASE}{t["slug"]}/"><strong>{esc(t["label"])}</strong><span>{esc(t["blurb"])}</span>'
        f'<span class="more">{sum(1 for p in pages if p["topic"] == k)} questions &rarr;</span></a>'
        for k, t in TOPICS.items() if any(p["topic"] == k for p in pages))
    home = f"""<section class="hero"><div class="wrap">
<p class="eyebrow">Independent. Sourced. Dated.</p>
<h1>Is it worth the fee?</h1>
<p class="lede">Travel cards and programs sell a big number. We work out what it is worth for the way <em>you</em> travel, and we say so when the answer is no.</p>
<p class="herocta"><a class="btn" href="{BASE}fee-calculator/">Try the annual fee calculator</a></p>
<div class="tgrid">{tcards}</div>
</div></section>
<section class="how"><div class="wrap">
<h2>How every page works</h2>
<div class="feats">
<div><span class="num">1</span><h3>One question per page</h3><p>Each page answers a single, narrow question in its first two sentences.</p></div>
<div><span class="num">2</span><h3>Every number has a source</h3><p>Fees, credits and rules link to where we found them, with the date we checked.</p></div>
<div><span class="num">3</span><h3>"No" is an answer</h3><p>Every page says who should skip the card or program. Most people are not the target customer.</p></div>
</div></div></section>
<section class="all newest"><div class="wrap"><h2>Newest answers</h2>
<div class="qgrid">{"".join(qcard(p) for p in newest[:6])}</div></div></section>
<section class="all"><div class="wrap"><h2>All questions</h2>
{"".join(f'<h3 class="grouphead"><a href="{BASE}{t["slug"]}/">{esc(t["label"])}</a></h3><div class="qgrid">' + "".join(qcard(p) for p in pages if p["topic"] == k) + "</div>" for k, t in TOPICS.items() if any(p["topic"] == k for p in pages))}
</div></section>"""
    org = {"@context": "https://schema.org", "@type": "Organization", "name": NAME, "url": SITE,
           "logo": SITE + "favicon.svg", "email": EMAIL}
    web = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE}
    write("index.html", layout(f"{NAME}: is that travel card or program worth it?", TAGLINE, home, "",
                               "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in (org, web))))

    # static pages
    rows = "".join(f'<tr><td>{esc(v["name"])}</td><td>{esc(v["we_get"])}</td></tr>' for v in LINKS.values())
    simple_page("about/", "About Worth the Fee",
                "Who runs Worth the Fee, what it covers and how it stays honest.", f"""
<p class="lede">{NAME} answers narrow questions about travel cards and travel programs: the kind where the honest answer depends on how you travel, and is sometimes "no, skip it".</p>
<h2>Who runs it</h2>
<p>{NAME} is a small independent site run by a cardholder who has paid these annual fees and wanted clearer sums than the marketing gives. It is not owned by a bank, a card issuer or a comparison company, and it does not take payment to feature or rank any product.</p>
<h2>How pages are made</h2>
<p>Pages are researched and drafted with the help of AI tools, then checked against the sources listed at the bottom of each page. Every number should trace to a named source. <a href="{BASE}how-we-check-facts/">How we check facts</a> explains the rules.</p>
<h2>How it earns</h2>
<p>Some pages end with an ordinary refer-a-friend link. <a href="{BASE}disclosure/">How we earn</a> lists every one and what we get.</p>
<h2>Get in touch</h2>
<p>Found a mistake or an out-of-date number? Write to <a href="mailto:{EMAIL}">{EMAIL}</a>. Corrections are the most useful mail we get.</p>""")
    simple_page("how-we-check-facts/", "How we check facts",
                "The rules Worth the Fee follows for sources, dates, corrections and what we will not claim.", f"""
<p class="lede">Card terms change several times a year. These are the rules every page follows.</p>
<h2>Sources</h2>
<ul><li>The provider's own page comes first: the card issuer, the program's terms, or its help center.</li>
<li>When the provider's page does not state something, we use established travel and finance publications and name them.</li>
<li>If two sources disagree, the page says so and does not pick one silently.</li>
<li>If we could not confirm something, the page says "not confirmed" or leaves it out.</li></ul>
<h2>Dates</h2>
<p>Every page shows the date its facts were last checked. A page that has not been checked recently may be out of date, so always confirm on the provider's site before you apply or sign up.</p>
<h2>What we will not do</h2>
<ul><li>Promise a welcome offer amount. Issuers set offers per applicant and change them often.</li>
<li>Tell you to apply. We lay out the sums and say who a product does not suit.</li>
<li>Hide a referral link. Every one is labeled where it appears.</li>
<li>Publish invented reviews, ratings or testimonials.</li></ul>
<h2>Corrections</h2>
<p>If you spot an error, write to <a href="mailto:{EMAIL}">{EMAIL}</a>. We fix confirmed errors and update the checked date.</p>
<h2>Not advice</h2>
<p>Pages are general information. They are not financial, tax or legal advice and do not take your circumstances into account.</p>""")
    simple_page("disclosure/", "How we earn",
                "Every referral link on Worth the Fee and what the site receives if you use it.", f"""
<p class="lede">{NAME} earns from refer-a-friend links. These are the ordinary links that companies give their own customers to share.</p>
<div class="tablewrap"><table><thead><tr><th>Link</th><th>What we get if you use it</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>What that means for you</h2>
<ul><li>You pay nothing extra. The company pays the reward.</li>
<li>You can always skip the link and go to the company's own site.</li>
<li>The offer you see through a referral link can be higher or lower than the public one. Compare both.</li>
<li>A referral link never decides what a page says. Several pages tell most readers not to sign up.</li></ul>
<h2>What we do not do</h2>
<p>We are not paid by any company to write about it, and no company reviews or approves our pages. We do not sell placement, rankings or ratings.</p>""")
    offer_boxes = "".join(
        cta_html([k]) + '<p class="fine">Related reading: ' + ", ".join(
            f'<a href="{BASE}{p["slug"]}/">{esc(p["title"])}</a>' for p in [p for p in pages if k in p["cta"]][:4]) + "</p>"
        for k in LINKS)
    simple_page("offers/", "Current referral offers",
                "Every referral link on Worth the Fee in one place, with what you get and what we get.", f"""
<p class="lede">Every refer-a-friend link on this site, in one place. Each box says what the offer was when we last checked and what we receive.</p>
<p class="disclosure">These are referral links. We earn points or cash if you sign up through one. Compare with the company's public offer first; it can be higher. <a href="{BASE}disclosure/">How we earn</a>.</p>
{offer_boxes}
<h2>Before you use one</h2>
<ul><li>Offers vary by applicant and change without notice. The company's page is the final word.</li>
<li>Read the page for that card or program first. Several tell most readers to skip it.</li>
<li>Do not apply for a card to earn a bonus you would have to overspend to reach.</li></ul>""")
    calc_js = json.dumps({k: {"card": v["card"], "fee": v["fee"], "cta": v.get("cta", k),
                              "button": LINKS[v.get("cta", k)]["button"], "more": BASE + v["more"] + "/",
                              "credits": v["credits"]} for k, v in CALC.items()})
    simple_page("fee-calculator/", "Annual fee calculator: is the card worth it for you?",
                "Tick the credits you would really use on the Amex Platinum, Sapphire Reserve or Sapphire Preferred and see what the fee costs you.", f"""
<p class="lede">Pick a card, then score each credit by how much of it you would spend anyway. The calculator shows what the annual fee really costs you.</p>
<p class="disclosure">This page contains referral links. We earn points or cash if you sign up through one. <a href="{BASE}disclosure/">How we earn</a>. Amounts were checked on {date.today().strftime("%B %-d, %Y")}; issuers change them.</p>
<div class="calc" id="calc">
<div class="calctabs" role="tablist">{"".join(f'<button type="button" data-card="{k}">{esc(v["card"])}</button>' for k, v in CALC.items())}</div>
<div id="calcrows"></div>
<div class="calcout" aria-live="polite"><p class="eyebrow">Your number</p><p id="calcsum"></p><p id="calcverdict"></p>
<p id="calccta"></p><p class="fine" id="calcmore"></p></div>
</div>
<noscript><p>The calculator needs JavaScript. The same sums are on <a href="{BASE}amex-platinum-credits-real-value/">the Amex Platinum credits page</a> and <a href="{BASE}chase-sapphire-reserve-credits-real-value/">the Sapphire Reserve credits page</a>.</p></noscript>
<h2>How to score a credit</h2>
<ul><li><strong>All of it:</strong> you already pay for this, in the pieces the credit comes in.</li>
<li><strong>Half:</strong> you would use it sometimes, or would pay less for it yourself.</li>
<li><strong>None:</strong> you would not buy this without the credit.</li></ul>
<h2>What it leaves out</h2>
<p>Lounges, hotel status, travel insurance, points earned and any welcome offer are not counted, because their value depends on how you travel. If the result is below zero, the gap is what you would pay each year for those. This page is information, not financial advice.</p>
<script>
(function(){{
var D={calc_js},cur=null,state={{}};
var rows=document.getElementById('calcrows');
function money(n){{return (n<0?'-':'')+'$'+Math.abs(Math.round(n)).toLocaleString('en-US');}}
function draw(k){{cur=k;state={{}};var c=D[k],h='';
 c.credits.forEach(function(r,i){{state[i]=0;
  h+='<div class="calcrow"><div><strong>'+r[0]+'</strong><span>Up to $'+r[1]+' a year. '+r[2]+'</span></div><div class="seg" data-i="'+i+'">'+
   '<button type="button" data-v="0" class="on">None</button><button type="button" data-v="0.5">Half</button><button type="button" data-v="1">All</button></div></div>';}});
 rows.innerHTML=h;
 document.querySelectorAll('.calctabs button').forEach(function(b){{b.classList.toggle('on',b.getAttribute('data-card')===k);}});
 sum();}}
function sum(){{var c=D[cur],tot=0;c.credits.forEach(function(r,i){{tot+=r[1]*state[i];}});
 var net=tot-c.fee;
 document.getElementById('calcsum').innerHTML='Credits you would use: <strong>'+money(tot)+'</strong> a year. Annual fee: <strong>'+money(c.fee)+'</strong>. Net: <strong>'+money(net)+'</strong>.';
 document.getElementById('calcverdict').textContent=net>=0?
  'On your numbers the credits alone cover the fee. Check each one again against what you really spent last year before you rely on it.':
  'On your numbers the '+c.card+' costs you '+money(-net)+' a year after credits. It is worth it only if lounges, status, insurance and points are worth that much to you.';
 document.getElementById('calccta').innerHTML='<a class="btn" rel="sponsored nofollow" data-go="'+c.cta+'" data-pos="calculator" href="{BASE}go/'+c.cta+'/">'+c.button+'</a>';
 document.getElementById('calcmore').innerHTML='Referral link: we earn if you are approved. <a href="'+c.more+'">How these credits work and who should skip the card</a>.';}}
rows.addEventListener('click',function(e){{var b=e.target.closest('button[data-v]');if(!b)return;var s=b.parentNode;
 state[s.getAttribute('data-i')]=parseFloat(b.getAttribute('data-v'));
 s.querySelectorAll('button').forEach(function(x){{x.classList.toggle('on',x===b);}});sum();
 try{{if(window.gtag&&!window._cu){{window._cu=1;gtag('event','calculator_use',{{card:cur}});}}}}catch(err){{}}}});
document.querySelector('.calctabs').addEventListener('click',function(e){{var b=e.target.closest('button[data-card]');if(b){{draw(b.getAttribute('data-card'));history.replaceState(null,'','#'+b.getAttribute('data-card'));}}}});
var h=location.hash.replace('#','');draw(D[h]?h:'amex');
}})();
</script>""")
    analytics_note = ("This site uses Google Analytics to count visits and button clicks. Google sets cookies and processes "
                      "data under its own privacy policy. You can block it with a browser setting or extension and the site "
                      "works the same." if ANALYTICS else "This site does not currently use an analytics service.")
    simple_page("privacy/", "Privacy",
                "What Worth the Fee collects about visitors and what it does not.", f"""
<p class="lede">Short version: we do not ask for your name, we do not run ads, and we do not sell data.</p>
<h2>What this site collects</h2>
<ul><li><strong>Visit statistics.</strong> We count page views and clicks on referral buttons so we know which pages are useful. If an analytics service is in use, it is named below.</li>
<li><strong>Email you send us.</strong> If you write to {EMAIL}, we keep your message so we can reply.</li></ul>
<p>We have no accounts, no comment forms and no newsletter.</p>
<h2>Analytics</h2>
<p>{analytics_note}</p>
<h2>When you click a referral link</h2>
<p>You leave this site and go to the company's own website. That company's privacy policy applies from then on. The company can tell that you arrived through our link; we are not told who you are, only (in some programs) that a referral succeeded.</p>
<h2>Other services</h2>
<p>The site is hosted on GitHub Pages and loads its typeface from Google Fonts. Both receive your IP address as part of delivering the page.</p>
<h2>Contact</h2>
<p>Questions about privacy: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>""")
    simple_page("contact/", "Contact",
                "How to reach Worth the Fee about a correction or a question.", f"""
<p class="lede">Write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<p>We read everything, and corrections come first. If a fee, credit or rule on a page is out of date, tell us which page and where you saw the new number.</p>
<p>We cannot give personal financial advice or tell you whether you will be approved for a card.</p>""")

    # redirects
    for k, v in LINKS.items():
        url = esc(v["url"])
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow"><title>Opening {esc(v["name"])}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{BASE}style.css">
{ANALYTICS}
<script>try{{if(window.gtag)gtag('event','referral_redirect',{{link:'{k}',transport_type:'beacon'}});}}catch(e){{}}</script>
<meta http-equiv="refresh" content="1;url={url}"></head>
<body><main><div class="wrap narrow"><p style="margin-top:80px">Opening {esc(v["name"])}. If nothing happens, <a rel="sponsored nofollow" href="{url}">continue here</a>.</p></div></main></body></html>"""
        write(f"go/{k}/index.html", page)

    write("404.html", layout(f"Page not found | {NAME}", "Page not found.",
                             f'<div class="wrap narrow"><article class="prose"><h1>Page not found</h1><p><a href="{BASE}">See all questions</a>.</p></article></div>',
                             "404.html", noindex=True))

    statics = ["", "offers/", "fee-calculator/", "about/", "how-we-check-facts/", "disclosure/", "privacy/", "contact/"] + [t["slug"] + "/" for k, t in TOPICS.items() if k in LIVE_TOPICS]
    urls = [(u, today) for u in statics] + [(p["slug"] + "/", p.get("checked", today)) for p in pages]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    ai_bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot-Extended', 'bingbot', 'CCBot']
    robots = "User-agent: *\nAllow: /\nDisallow: /go/\n\n" + "".join(
        f"User-agent: {b}\nAllow: /\nDisallow: /go/\n\n" for b in ai_bots) + f"Sitemap: {SITE}sitemap.xml\n"
    write("robots.txt", robots)
    llms = (f"# {NAME}\n\n> {TAGLINE} Each page answers one question in its first two sentences, cites its sources and "
            f"gives the date it was checked. Some pages end with a disclosed referral link.\n\n")
    for k, t in TOPICS.items():
        if k not in LIVE_TOPICS:
            continue
        llms += f"## {t['label']}\n\n" + "".join(
            f'- [{p["title"]}]({SITE}{p["slug"]}/): {p["description"]}\n' for p in pages if p["topic"] == k) + "\n"
    llms += f"## About\n\n- [Current referral offers]({SITE}offers/)\n- [Annual fee calculator]({SITE}fee-calculator/)\n- [How we check facts]({SITE}how-we-check-facts/)\n- [How we earn]({SITE}disclosure/)\n"
    llms += f"\nFull text of every page in one file: {SITE}llms-full.txt. Each page also has a Markdown copy at its URL plus index.md.\n"
    write("llms.txt", llms)
    write("llms-full.txt", f"# {NAME}: full text\n\n> {TAGLINE}\n\n" + "\n---\n\n".join(page_md(p) for p in pages))
    (ROOT / "urls.txt").write_text("\n".join(SITE + u for u, _ in urls) + "\n")
    print(f"built {len(pages)} pages -> {OUT}")


if __name__ == "__main__":
    build()
