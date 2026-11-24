# Worth the Fee

Static site at https://itsworththefee.com answering narrow questions about travel cards and programs.

- Build: `python3 -m venv .venv && .venv/bin/pip install markdown && .venv/bin/python build.py` (writes `docs/`, served by GitHub Pages).
- Pages: `content/*.md` (frontmatter: title, slug, description, cta, checked). Referral links: `links.json` (a link's optional `top` line is shown beside the first button on each page; when an offer check changes `offer`, re-check and re-date `top` too).
- Unpublished drafts: `drafts/`. Fact sheets behind the pages: `research/`.
- Visit counting: `analytics.html` (Google Analytics 4). Events: `referral_click` (button on a page), `referral_redirect` (the /go/ page).
- After adding pages: build, push, then ping IndexNow with the list in `urls.txt`.

Rules the referral programs set:
- Chase: fewer than 10 applications a month through the link, or Chase may pay nothing that month.
- Rakuten: link only on pages we own; no paid ads to it; nothing disparaging about Rakuten.
- Airbnb: referral links must not be published on commercial websites. Keep it off this site.
- Amex: sharing by email must use Amex's own "Refer by Email" form.

## Add a referral link

1. `.venv/bin/python add_link.py` and answer five questions (key, name, link, what the reader gets, what you get).
2. To show it at the end of pages, add its key to the `cta:` line of those pages in `content/`.
3. `./publish.sh "Add <name> link"` checks every page, rebuilds, publishes and notifies search engines.

The link appears on `/offers/` and "How we earn" without step 2. Read the program's terms first: some (Airbnb) do not allow links on public websites.

## Program rules found 2026-11-24

- **TopCashback** (referral terms, section 7): a link on our own website needs a cookie notice, a Cookies page and a Privacy page (all in place: `analytics.html`, `/cookies/`, `/privacy/`); say we are in the Refer a Friend program and get a reward; no paid ads; never show the link beside any other TopCashback new-member incentive. Its general terms cap bonuses "earned through commercial means" at $5 per referral without written consent, so expect $5, not the advertised amount.
- **Chase checking refer-a-friend** (key `chasechecking`): $50 per account opened, 10 a year ($500). No website rule seen on the program page. Bonuses are reportable income.
- **Ibotta: NOT on the site.** Its Terms of Use (section 6 and the conduct rules) bar publishing a referral code on a public website and any commercial use of the referral program; breach can close the account. Dom's code is for people he knows only.
