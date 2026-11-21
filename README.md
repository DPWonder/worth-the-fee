# Worth the Fee

Static site at https://itsworththefee.com answering narrow questions about travel cards and programs.

- Build: `python3 -m venv .venv && .venv/bin/pip install markdown && .venv/bin/python build.py` (writes `docs/`, served by GitHub Pages).
- Pages: `content/*.md` (frontmatter: title, slug, description, cta, checked). Referral links: `links.json`.
- Unpublished drafts: `drafts/`. Fact sheets behind the pages: `research/`.
- Visit counting: `analytics.html` (Google Analytics 4). Events: `referral_click` (button on a page), `referral_redirect` (the /go/ page).
- After adding pages: build, push, then ping IndexNow with the list in `urls.txt`.

Rules the referral programs set:
- Chase: fewer than 10 applications a month through the link, or Chase may pay nothing that month.
- Rakuten: link only on pages we own; no paid ads to it; nothing disparaging about Rakuten.
- Airbnb: referral links must not be published on commercial websites. Keep it off this site.
- Amex: sharing by email must use Amex's own "Refer by Email" form.
