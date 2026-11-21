# Writer brief for Worth the Fee (itsworththefee.com)

Worth the Fee is a small, honest consumer site. Each page answers ONE narrow question about a travel card or program, shows its sources, and says who should skip the product. Today is 2026-11-20.

## Research rules

- Facts must be current as of November 2026. Card terms changed a lot in 2025-2026. Do NOT rely on memory: search and read.
- First read the existing fact sheets in `research/` (`amex.md`, `chase-rakuten.md`). Reuse facts already confirmed there, and stay consistent with them. Only research what they do not cover.
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
checked: 2026-11-20
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
  `amex-platinum-worth-it-occasional-flyer`, `amex-platinum-credits-real-value`, `amex-platinum-hawaii-trip`, `amex-platinum-for-golfers`, `amex-referral-offer-how-it-works`, `amex-platinum-vs-sapphire-reserve-hawaii`, `chase-sapphire-preferred-one-trip-a-year`, `sapphire-preferred-vs-reserve-light-traveler`, `rakuten-amex-points-instead-of-cash`, `rakuten-50-bonus-how-it-works`.
  Link only to those or to slugs in your own list.
- Quotes from sources: at most one short quote per page, under 15 words, with the source named.

## When you finish

Reply with a short report: the files you wrote, every "not confirmed" item, and every place sources disagreed. Nothing else.
