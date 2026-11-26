#!/usr/bin/env python3
"""Reads today's headline cash back rate for each store from Rakuten's own store pages,
keeps a daily history in research/rakuten-rates.csv, and writes the tracker page
content/rakuten-cash-back-rates-today-by-store.md. Run once a day before build.py."""
import csv
import datetime
import html
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).parent
HIST = ROOT / "research" / "rakuten-rates.csv"
PAGE = ROOT / "content" / "rakuten-cash-back-rates-today-by-store.md"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")

# (store name, Rakuten store address, our page slug or "")
STORES = [
    ("Adidas", "adidas.com", "rakuten-adidas-cash-back-how-it-works"),
    ("Apple", "apple.com", "rakuten-apple-cash-back-how-it-works"),
    ("Best Buy", "bestbuy.com", "rakuten-best-buy-cash-back-how-it-works"),
    ("Chewy", "chewy.com", "rakuten-chewy-cash-back-how-it-works"),
    ("Dick's Sporting Goods", "dickssportinggoods.com", "rakuten-dicks-sporting-goods-cash-back-how-it-works"),
    ("eBay", "ebay.com", "rakuten-ebay-cash-back-how-it-works"),
    ("Home Depot", "homedepot.com", "rakuten-home-depot-cash-back-how-it-works"),
    ("Kohl's", "kohls.com", "rakuten-kohls-cash-back-how-it-works"),
    ("Lowe's", "lowes.com", "rakuten-lowes-cash-back-how-it-works"),
    ("Macy's", "macys.com", "rakuten-macys-cash-back-how-it-works"),
    ("Nike", "nike.com", "rakuten-nike-cash-back-how-it-works"),
    ("Nordstrom", "nordstrom.com", "rakuten-nordstrom-cash-back-how-it-works"),
    ("Old Navy", "oldnavy.com", "rakuten-old-navy-cash-back-how-it-works"),
    ("Samsung", "samsung.com", "rakuten-samsung-cash-back-how-it-works"),
    ("Sephora", "sephora.com", "rakuten-sephora-cash-back-how-it-works"),
    ("Target", "target.com", "rakuten-target-cash-back-how-it-works"),
    ("Ulta", "ulta.com", "rakuten-ulta-cash-back-how-it-works"),
    ("Walmart", "walmart.com", "rakuten-walmart-cash-back-how-it-works"),
    ("Wayfair", "wayfair.com", "rakuten-wayfair-cash-back-how-it-works"),
    ("Expedia", "expedia.com", "rakuten-expedia-booking-com-cash-back"),
    ("Booking.com", "booking.com", "rakuten-expedia-booking-com-cash-back"),
    ("Dell", "dell.com", "rakuten-laptop-cash-back-dell-hp-lenovo"),
    ("HP", "hp.com", "rakuten-laptop-cash-back-dell-hp-lenovo"),
    ("Lenovo", "lenovo.com", "rakuten-laptop-cash-back-dell-hp-lenovo"),
    ("Gap", "gap.com", "rakuten-gap-cash-back-how-it-works"), ("Lululemon", "lululemon.com", "rakuten-lululemon-cash-back-how-it-works"), ("Etsy", "etsy.com", "rakuten-etsy-cash-back-how-it-works"),
    ("Temu", "temu.com", "rakuten-temu-cash-back-how-it-works"), ("Shein", "shop/sheinside", "rakuten-shein-cash-back-how-it-works"), ("Petco", "petco.com", "rakuten-petco-cash-back-how-it-works"),
    ("PetSmart", "petsmart.com", "rakuten-petsmart-cash-back-how-it-works"), ("Staples", "staples.com", "rakuten-staples-cash-back-how-it-works"),
    ("Priceline", "priceline.com", "rakuten-priceline-cash-back-how-it-works"), ("Hotels.com", "shop/hotels", "rakuten-hotels-com-cash-back-how-it-works"),
    ("Vrbo", "vrbo.com", "rakuten-vrbo-cash-back-how-it-works"), ("Viator", "viator.com", "rakuten-viator-cash-back-how-it-works"), ("CVS", "cvs.com", "rakuten-cvs-cash-back-how-it-works"),
    ("Walgreens", "walgreens.com", "rakuten-walgreens-cash-back-how-it-works"), ("JCPenney", "jcpenney.com", "rakuten-jcpenney-cash-back-how-it-works"),
    ("Bloomingdale's", "bloomingdales.com", "rakuten-bloomingdales-cash-back-how-it-works"), ("Saks Fifth Avenue", "saksfifthavenue.com", "rakuten-saks-fifth-avenue-cash-back-how-it-works"),
    ("Neiman Marcus", "neimanmarcus.com", "rakuten-neiman-marcus-cash-back-how-it-works"), ("Dyson", "dyson.com", "rakuten-dyson-cash-back-how-it-works"),
    ("Crocs", "crocs.com", "rakuten-crocs-cash-back-how-it-works"), ("Under Armour", "underarmour.com", "rakuten-under-armour-cash-back-how-it-works"),
    ("The North Face", "thenorthface.com", "rakuten-the-north-face-cash-back-how-it-works"), ("Columbia", "columbiasportswear.com", "rakuten-columbia-cash-back-how-it-works"),
    ("Academy Sports", "shop/academysportsoutdoors", "rakuten-academy-sports-cash-back-how-it-works"), ("StubHub", "stubhub.com", "rakuten-stubhub-cash-back-how-it-works"),
    ("Sam's Club", "samsclub.com", "rakuten-sams-club-cash-back-how-it-works"), ("Costco", "costco.com", "rakuten-costco-cash-back-how-it-works"),
    ("Amazon", "amazon.com", "does-rakuten-work-on-amazon"),
    ("Instacart", "instacart.com", "rakuten-instacart-cash-back-how-it-works"), ("DoorDash", "doordash.com", "rakuten-doordash-cash-back-how-it-works"),
    ("Uber", "uber.com", "rakuten-uber-cash-back-how-it-works"), ("Banana Republic", "bananarepublic.com", "rakuten-banana-republic-cash-back-how-it-works"),
    ("J.Crew", "jcrew.com", "rakuten-j-crew-cash-back-how-it-works"), ("Anthropologie", "anthropologie.com", ""),
    ("Bath & Body Works", "bathandbodyworks.com", ""), ("Victoria's Secret", "victoriassecret.com", "rakuten-victorias-secret-cash-back-how-it-works"),
    ("Williams Sonoma", "williams-sonoma.com", ""), ("Pottery Barn", "potterybarn.com", ""),
    ("Ace Hardware", "acehardware.com", "rakuten-ace-hardware-cash-back-how-it-works"), ("Office Depot", "officedepot.com", "rakuten-office-depot-cash-back-how-it-works"),
    ("GameStop", "gamestop.com", ""), ("Newegg", "newegg.com", "rakuten-newegg-cash-back-how-it-works"),
    ("Zappos", "zappos.com", "rakuten-zappos-cash-back-how-it-works"), ("DSW", "dsw.com", "rakuten-dsw-cash-back-how-it-works"), ("Foot Locker", "footlocker.com", "rakuten-foot-locker-cash-back-how-it-works"),
    ("New Balance", "newbalance.com", "rakuten-new-balance-cash-back-how-it-works"), ("Skechers", "skechers.com", "rakuten-skechers-cash-back-how-it-works"),
    ("Carter's", "carters.com", "rakuten-carters-cash-back-how-it-works"), ("H&M", "hm.com", "rakuten-hm-cash-back-how-it-works"), ("Levi's", "shop/levis", "rakuten-levis-cash-back-how-it-works"),
    ("Ray-Ban", "ray-ban.com", "rakuten-ray-ban-cash-back-how-it-works"), ("Sonos", "sonos.com", "rakuten-sonos-cash-back-how-it-works"), ("Bose", "bose.com", ""),
    ("Tractor Supply", "shop/tractorsupplycompany", "rakuten-tractor-supply-cash-back-how-it-works"), ("Michaels", "michaels.com", ""),
    ("JOANN", "joann.com", ""), ("Hilton", "hilton.com", "rakuten-hilton-cash-back-how-it-works"), ("Marriott", "shop/marriotthotelsandresorts", "rakuten-marriott-cash-back-how-it-works"),
    ("IHG", "ihg.com", "rakuten-ihg-cash-back-how-it-works"), ("Hertz", "hertz.com", ""), ("Avis", "avis.com", "rakuten-avis-cash-back-how-it-works"),
    ("TurboTax", "turbotax.com", "rakuten-turbotax-cash-back-how-it-works"), ("Verizon", "verizon.com", "rakuten-verizon-cash-back-how-it-works"), ("AT&T", "att.com", "rakuten-att-cash-back-how-it-works"),
]


def fetch(store):
    name, addr, slug = store
    url = f"https://www.rakuten.com/{addr}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            head = r.read(200000).decode("utf-8", "ignore")
    except Exception:
        return None
    m = re.search(r"<title>([^<]*)</title>", head)
    if not m:
        return None
    title = html.unescape(m.group(1))
    r = re.search(r"&\s+((?:Up to\s+)?[\d.]+%\s+Cash Back|No Cash Back|(?:Up to\s+)?\$[\d.]+\s+Cash Back)", title, re.I)
    if not r:
        return None
    rate = re.sub(r"\s+", " ", r.group(1))
    rate = rate[0].upper() + rate[1:]
    rate = re.sub(r"\.0+%", "%", rate).replace(" Cash Back", "").replace("No", "None")
    return name, addr, slug, rate


def pct(rate):
    m = re.search(r"([\d.]+)%", rate)
    return float(m.group(1)) if m else 0.0


def main():
    today = datetime.date.today()
    with ThreadPoolExecutor(8) as ex:
        got = [g for g in ex.map(fetch, STORES) if g]
    if len(got) < 20:
        raise SystemExit(f"only {len(got)} stores read; page left as it was")

    hist = []
    if HIST.exists():
        hist = list(csv.DictReader(HIST.open()))
    hist = [h for h in hist if h["date"] != today.isoformat()]
    for name, addr, slug, rate in got:
        hist.append({"date": today.isoformat(), "store": name, "rate": rate})
    HIST.parent.mkdir(exist_ok=True)
    with HIST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "store", "rate"])
        w.writeheader()
        w.writerows(hist)

    days = sorted({h["date"] for h in hist})
    prev_day = days[-2] if len(days) > 1 else None
    prev = {h["store"]: h["rate"] for h in hist if h["date"] == prev_day}
    first_day = days[0]
    long_date = f"{today:%B} {today.day}, {today.year}"
    short_date = f"{today:%B} {today.day}"

    got.sort(key=lambda g: (-pct(g[3]), g[0].lower()))
    rows, changes = [], []
    for name, addr, slug, rate in got:
        label = f"[{name}](/{slug}/)" if slug else name
        was = prev.get(name)
        if not was:
            change = "First reading"
        elif was == rate:
            change = "Same"
        else:
            change = f"Was {was.lower()}"
            changes.append(f"- **{name}:** {was.lower()} on {prev_day[5:].replace('-', '/')}, {rate.lower()} today.")
        rows.append(f"| {label} | {rate} | {change} |")

    none = [g[0] for g in got if g[3] == "None"]
    top = [g for g in got if pct(g[3]) > 0][:5]
    top_txt = ", ".join(f"{g[0]} ({g[3].lower()})" for g in top)
    n = len(got)
    if changes:
        change_block = "\n".join(changes)
    elif prev_day:
        change_block = "No store on this list changed its headline rate since the last reading."
    else:
        change_block = "This is the first day of readings, so there is nothing to compare yet. Changes will be listed here from tomorrow."
    none_txt = (", ".join(none) + ".") if none else "None of the stores on this list."

    PAGE.write_text(f"""---
title: Rakuten cash back rates today, by store ({short_date})
slug: rakuten-cash-back-rates-today-by-store
description: The headline Rakuten cash back rate at {n} large stores, read from Rakuten's store pages on {long_date}, with what changed since the last reading.
topic: rakuten
cta: rakuten
checked: {today.isoformat()}
---

On {long_date}, the highest headline Rakuten rates among {n} large stores read were {top_txt}. The table below lists every store read, the rate shown on its Rakuten page that day, and whether it moved since the last reading.

This page is information, not financial advice. Rates change daily, and sometimes within a day, so the rate on Rakuten at the moment you activate is the one that counts.

## Rates read on {long_date}

"Up to" means the top rate applies to some categories or brands only; most items usually earn less. "None" means the store has a Rakuten page but it showed no cash back that day.

| Store | Headline rate | Since last reading |
|---|---|---|
{chr(10).join(rows)}

## What changed since the last reading

{change_block}

Readings on this page started on {first_day[5:].replace('-', '/')}/{first_day[:4]}. Each reading is the headline rate in the title of the store's own page on Rakuten, taken once in the morning, Pacific time.

## Stores showing no cash back today

{none_txt}

A store can drop to no cash back for a day or a season and come back later. A store that is missing from the table either has no page on Rakuten or its page could not be read today; that is not confirmed either way.

## How to read an "up to" rate

The headline is the ceiling, not the typical rate. A store page on Rakuten lists the rate for each category, and the exclusions sit in the terms below that list. Three things decide what a purchase earns:

- **The category.** Electronics, gift cards and sale items are often set lower than the headline, or at nothing.
- **The exclusions.** Many stores exclude gift cards, some brands, and orders paid with certain coupons.
- **The order of steps.** Cash back is tied to activating first, through a Rakuten link, the app or the browser extension, then buying in the same session.

A worked example: at a store with "up to 10%" where the item's category is set at 2%, a $200 order earns $4.00, not $20.00. Taxes and shipping do not count.

For the full steps, see [how Rakuten works, step by step](/how-does-rakuten-work-step-by-step/). For the days around Thanksgiving, see [Rakuten on Black Friday](/rakuten-black-friday-cash-back-2026/) and [Rakuten on Cyber Monday](/rakuten-cyber-monday-cash-back-2026/). Card rewards come on top; see [stacking with card rewards](/rakuten-stack-with-credit-card-rewards/).

## When the money arrives

A purchase usually shows as pending within days, then is confirmed after the store's return window. Rakuten pays four times a year. See [when Rakuten pays](/rakuten-when-do-you-get-paid/) and, if an order never shows, [what to do when cash back did not track](/rakuten-missing-cash-back-what-to-do/).

## Who should skip it

- You are buying from a store showing "None" today. There is nothing to earn there until the rate returns.
- The item is in an excluded category. The store's Rakuten page lists these.
- Another discount beats the rate. A coupon code not listed on Rakuten can void the cash back, so compare the two before choosing.
- You expect to return the item. Returned orders lose their cash back.

## Quick answers

**Which store has the highest Rakuten rate today?**
Among the stores read on {long_date}, the highest headline rates were {top_txt}. These are ceilings; most items earn less.

**How often do Rakuten rates change?**
Daily, and sometimes during the day. This page is read once each morning, so check the store's Rakuten page before buying.

**Why does a store show no cash back?**
Stores set their own rates and can pause them. Today these showed none: {none_txt}

## Sources

- [Rakuten: all stores](https://www.rakuten.com/stores/all)
- [Rakuten: Why didn't I earn cash back?](https://www.rakuten.com/help/article/why-didnt-i-earn-cash-back-360036367393)
- [Rakuten: When will I get paid?](https://www.rakuten.com/help/article/when-will-i-get-paid-360002117667)
- [Rakuten: Terms and conditions](https://www.rakuten.com/help/article/terms-conditions)
""")
    print(f"{n} stores read; {len(changes)} changed; {len(none)} with no cash back")
    for g in got:
        print(f"  {g[0]}: {g[3]}")


if __name__ == "__main__":
    main()
