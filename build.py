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
    "rakuten": {"slug": "rakuten", "label": "Rakuten",
                "blurb": "Cash back or Amex points, and how the sign-up bonus really works."},
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
    meta["topic"] = meta["cta"][0] if meta["cta"] else "amex"
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


def layout(title, description, content, path, extra_head="", noindex=False, og_type="website"):
    canonical = SITE + path
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    topic_nav = "".join(f'<a href="{BASE}{t["slug"]}/">{esc(t["label"])}</a>' for t in TOPICS.values())
    topic_foot = "".join(f'<li><a href="{BASE}{t["slug"]}/">{esc(t["label"])}</a></li>' for t in TOPICS.values())
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
<meta name="twitter:card" content="summary">
<link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml">
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
<nav aria-label="Topics">{topic_nav}<a href="{BASE}about/">About</a></nav>
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
            "dateModified": checked, "datePublished": checked,
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
        related = [p for p in pages if p["topic"] == pg["topic"] and p["slug"] != pg["slug"]][:3]
        rel_html = ""
        if related:
            rel_html = '<section class="related"><h2>Related questions</h2><div class="qgrid">' + "".join(qcard(p) for p in related) + "</div></section>"
        disclosure = ""
        if pg["cta"]:
            disclosure = (f'<p class="disclosure">This page ends with a referral link. We earn points or cash if you sign up '
                          f'through it. <a href="{BASE}disclosure/">How we earn</a>.</p>')
        content = (
            f'<div class="wrap narrow"><nav class="crumbs" aria-label="Breadcrumb"><a href="{BASE}">Home</a> <span>/</span> '
            f'<a href="{BASE}{topic["slug"]}/">{esc(topic["label"])}</a></nav>'
            f'<article class="prose"><h1>{esc(pg["title"])}</h1>'
            f'<p class="meta"><span>Facts checked {nice}</span><span>{pg["minutes"]} min read</span>'
            f'<span><a href="{BASE}how-we-check-facts/">How we check facts</a></span></p>'
            f'{disclosure}<div class="answer"><p class="eyebrow">The short answer</p>{answer_html}</div>'
            f'{body_html}{cta_html(pg["cta"])}</article>{rel_html}</div>'
        )
        write(path + "index.html", layout(f'{pg["title"]} | {NAME}', pg["description"], content, path, head, og_type="article"))

    # topic hubs
    for key, t in TOPICS.items():
        items = [p for p in pages if p["topic"] == key or key in p["cta"]]
        content = (f'<div class="wrap"><section class="hubhead"><p class="eyebrow">Topic</p><h1>{esc(t["label"])}</h1>'
                   f'<p class="lede">{esc(t["blurb"])}</p></section>'
                   f'<div class="qgrid">{"".join(qcard(p) for p in items)}</div></div>')
        write(t["slug"] + "/index.html", layout(f'{t["label"]}: is it worth it? | {NAME}', t["blurb"], content, t["slug"] + "/"))

    # home
    tcards = "".join(
        f'<a class="tcard" href="{BASE}{t["slug"]}/"><strong>{esc(t["label"])}</strong><span>{esc(t["blurb"])}</span>'
        f'<span class="more">{sum(1 for p in pages if p["topic"] == k or k in p["cta"])} questions &rarr;</span></a>'
        for k, t in TOPICS.items())
    home = f"""<section class="hero"><div class="wrap">
<p class="eyebrow">Independent. Sourced. Dated.</p>
<h1>Is it worth the fee?</h1>
<p class="lede">Travel cards and programs sell a big number. We work out what it is worth for the way <em>you</em> travel, and we say so when the answer is no.</p>
<div class="tgrid">{tcards}</div>
</div></section>
<section class="how"><div class="wrap">
<h2>How every page works</h2>
<div class="feats">
<div><span class="num">1</span><h3>One question per page</h3><p>Each page answers a single, narrow question in its first two sentences.</p></div>
<div><span class="num">2</span><h3>Every number has a source</h3><p>Fees, credits and rules link to where we found them, with the date we checked.</p></div>
<div><span class="num">3</span><h3>"No" is an answer</h3><p>Every page says who should skip the card or program. Most people are not the target customer.</p></div>
</div></div></section>
<section class="all"><div class="wrap"><h2>All questions</h2>
<div class="qgrid">{"".join(qcard(p) for p in pages)}</div></div></section>"""
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
<script>try{{if(window.gtag)gtag('event','referral_click',{{link:'{k}',transport_type:'beacon'}});}}catch(e){{}}</script>
<meta http-equiv="refresh" content="1;url={url}"></head>
<body><main><div class="wrap narrow"><p style="margin-top:80px">Opening {esc(v["name"])}. If nothing happens, <a rel="sponsored nofollow" href="{url}">continue here</a>.</p></div></main></body></html>"""
        write(f"go/{k}/index.html", page)

    write("404.html", layout(f"Page not found | {NAME}", "Page not found.",
                             f'<div class="wrap narrow"><article class="prose"><h1>Page not found</h1><p><a href="{BASE}">See all questions</a>.</p></article></div>',
                             "404.html", noindex=True))

    statics = ["", "about/", "how-we-check-facts/", "disclosure/", "privacy/", "contact/"] + [t["slug"] + "/" for t in TOPICS.values()]
    urls = [(u, today) for u in statics] + [(p["slug"] + "/", p.get("checked", today)) for p in pages]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /go/\n\nSitemap: {SITE}sitemap.xml\n")
    llms = (f"# {NAME}\n\n> {TAGLINE} Each page answers one question in its first two sentences, cites its sources and "
            f"gives the date it was checked. Some pages end with a disclosed referral link.\n\n")
    for k, t in TOPICS.items():
        llms += f"## {t['label']}\n\n" + "".join(
            f'- [{p["title"]}]({SITE}{p["slug"]}/): {p["description"]}\n' for p in pages if p["topic"] == k) + "\n"
    llms += f"## About\n\n- [How we check facts]({SITE}how-we-check-facts/)\n- [How we earn]({SITE}disclosure/)\n"
    write("llms.txt", llms)
    (ROOT / "urls.txt").write_text("\n".join(SITE + u for u, _ in urls) + "\n")
    print(f"built {len(pages)} pages -> {OUT}")


if __name__ == "__main__":
    build()
