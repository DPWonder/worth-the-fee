# Writer brief for Worth the Fee (itsworththefee.com)

Worth the Fee is a small, honest consumer site. Each page answers ONE narrow question about a travel card or program, shows its sources, and says who should skip the product. Today is 2026-11-21.

## Research rules

- Facts must be current as of November 2026. Card terms changed a lot in 2025-2026. Do NOT rely on memory: search and read.
- First read the existing fact sheets in `research/` (all `.md` files there; start with the ones for your cards). Reuse facts already confirmed there, and stay consistent with them. Only research what they do not cover.
- Prefer the provider's own pages. Many (americanexpress.com, some chase.com) block fetches; then use The Points Guy, One Mile at a Time, Frequent Miler, Upgraded Points, AwardWallet, NerdWallet, Doctor of Credit, and cross-check two sources.
- If sources disagree, say so on the page. If you cannot confirm something, write "not confirmed" or leave it out. Never invent a number.
- Append what you newly confirm to a NEW fact sheet `research/<your-batch-name>.md`, each line ending with its source URL. Do not edit the other fact sheets.

## Page format

Write each page to `content/<slug>.md`. Do not touch existing files in `content/`. Start with exactly this frontmatter:

```
---
title: <the question, as a plain headline, in American English>
slug: <the slug given in your list>
description: <one sentence, under 155 characters, that answers the question>
topic: <the topic key given in your list>
cta: <the cta keys given in your list>
checked: 2026-11-21
---
```

Then the body:

- The first paragraph answers the question in one or two sentences. It is shown in a highlighted "short answer" box, so it must stand alone.
- Then one line: "This page is information, not financial advice."
- 500 to 800 words. `##` subheadings. A table wherever numbers compare.
- A "## Who should skip it" section (or equivalent) on every page.
- End with "## Quick answers": exactly 3 pairs, each written as a bold question line `**Question?**` followed by the answer on the next line.
- Then "## Sources": a list of markdown links for the URLs used on that page.

## Writing rules (strict)

- American spelling (program, traveler, authorized, check, center).
- Plain words, short sentences. No hype words: best, amazing, ultimate, unlock, game-changer, must-have, hack.
- Never promise a welcome offer amount. Say offers vary by applicant and change.
- Never tell the reader to apply. Lay out the sums.
- No referral links, no calls to action, no "click here" in the body. The site adds its own disclosed referral box from the `cta` line.
- No invented anecdotes, no "I" or "we tested". Do not mention who runs the site.
- Nothing disparaging about a company; state facts and limits neutrally.
- You may link to other pages on this site with a relative link such as `[what the credits are worth](/amex-platinum-credits-real-value/)`. Existing slugs:
  `amex-blue-cash-preferred-vs-everyday`, `amex-gold-card-worth-the-fee`, `amex-gold-vs-chase-sapphire-preferred`, `amex-membership-rewards-points-value`, `amex-once-per-lifetime-welcome-offer-rule`, `amex-platinum-airline-fee-credit-what-counts`, `amex-platinum-authorized-user-worth-195`, `amex-platinum-cell-phone-protection`, `amex-platinum-centurion-lounge-guest-rules`, `amex-platinum-credits-real-value`, `amex-platinum-digital-entertainment-credit-what-counts`, `amex-platinum-downgrade-or-cancel-options`, `amex-platinum-for-golfers`, `amex-platinum-global-entry-clear-credit`, `amex-platinum-hawaii-trip`, `amex-platinum-hotel-status-marriott-hilton-gold`, `amex-platinum-referral-vs-public-offer`, `amex-platinum-resy-credit-how-it-works`, `amex-platinum-uber-credit-worth-it`, `amex-platinum-vs-business-platinum`, `amex-platinum-vs-capital-one-venture-x`, `amex-platinum-vs-delta-skymiles-reserve`, `amex-platinum-vs-gold-which-fits`, `amex-platinum-vs-sapphire-reserve-hawaii`, `amex-platinum-welcome-offer-spending-requirement`, `amex-platinum-worth-it-occasional-flyer`, `amex-points-to-hawaii-best-uses`, `amex-points-vs-chase-points-which-are-worth-more`, `amex-referral-offer-how-it-works`, `amex-transfer-partners-which-are-worth-it`, `are-credit-card-welcome-bonuses-taxable`, `chase-5-24-rule-explained`, `chase-points-boost-explained`, `chase-points-to-hawaii-best-uses`, `chase-sapphire-bonus-eligibility-2026`, `chase-sapphire-preferred-first-travel-card`, `chase-sapphire-preferred-first-year-plan`, `chase-sapphire-preferred-for-disney-trip`, `chase-sapphire-preferred-foreign-transaction-fees-abroad`, `chase-sapphire-preferred-one-trip-a-year`, `chase-sapphire-preferred-referral-bonus-how-it-works`, `chase-sapphire-preferred-rental-car-insurance`, `chase-sapphire-preferred-travel-insurance`, `chase-sapphire-preferred-vs-capital-one-venture`, `chase-sapphire-preferred-vs-citi-strata-premier`, `chase-sapphire-preferred-vs-freedom-unlimited`, `chase-sapphire-referral-vs-public-offer`, `chase-sapphire-reserve-credits-real-value`, `chase-sapphire-reserve-lounge-access`, `chase-sapphire-reserve-vs-capital-one-venture-x`, `chase-sapphire-welcome-bonus-spending-requirement`, `chase-to-hyatt-transfer-change-2026`, `chase-transfer-partners-which-are-worth-it`, `delta-gold-vs-platinum-vs-reserve-amex`, `delta-skymiles-gold-amex-free-checked-bag-math`, `do-amex-and-chase-points-expire`, `does-applying-for-a-travel-card-hurt-credit-score`, `fine-hotels-resorts-hawaii-worth-it`, `fine-hotels-resorts-vs-hotel-collection`, `flying-with-golf-clubs-airline-fees`, `golf-trip-travel-insurance-credit-card`, `hawaii-airport-lounges-by-card`, `hawaii-trip-which-card-pays-for-itself`, `highest-amex-platinum-welcome-offer-how-to-check`, `hilton-surpass-vs-aspire-amex`, `how-many-points-for-a-flight-to-europe`, `how-many-points-for-a-flight-to-japan`, `hyatt-hotels-hawaii-points-cost`, `is-rakuten-cash-back-taxable`, `is-rakuten-legit-how-it-makes-money`, `marriott-bonvoy-brilliant-amex-worth-650`, `points-or-cash-when-to-pay-with-points`, `priority-pass-by-card-what-you-get`, `rakuten-50-bonus-how-it-works`, `rakuten-amex-points-instead-of-cash`, `rakuten-amex-points-worth-more-than-cash`, `rakuten-big-fat-check-vs-paypal`, `rakuten-black-friday-cash-back-2026`, `rakuten-browser-extension-safe-privacy`, `rakuten-golf-gear-cash-back`, `rakuten-hotels-flights-cash-back`, `rakuten-how-to-switch-to-amex-points`, `rakuten-in-store-cash-back-how-it-works`, `rakuten-missing-cash-back-what-to-do`, `rakuten-stack-with-credit-card-rewards`, `rakuten-vs-capital-one-shopping`, `rakuten-vs-topcashback`, `rakuten-when-do-you-get-paid`, `sapphire-preferred-vs-reserve-light-traveler`.
  Link only to those or to slugs in your own list.
- Quotes from sources: at most one short quote per page, under 15 words, with the source named.

## Checks

Do not run `build.py`. When your pages are written, run `.venv/bin/python check.py` from the project folder and fix every problem it lists for YOUR pages. Do not write a page that repeats an existing slug's question; link to that page.

## When you finish

Reply with a short report: the files you wrote, every "not confirmed" item, and every place sources disagreed. Nothing else.
