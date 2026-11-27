# Owner log

Each day: the verdict, the one change made, and the number that should move.

## 2026-11-25

- Google, per day: 11-21 87 views / 0 clicks; 11-22 1,085 / 7; 11-23 2,871 / 10; 11-24 4,400 / 12. Click rate 0.3%, average position about 19.
- Weakest step: being clicked in the results. Store pages sit at positions 7 to 10; card pages at 15 to 70.
- Changes made, first readable 11-27 or 11-28: (1) store pages' search titles carry the rate read that day; (2) store pages carry a rate history table; (3) 39 store pages added in one afternoon (175 to 214 pages); (4) three TopCashback pages; (5) the morning job writes 5 store pages, 2 before-joining pages and 1 unanswered-query page a day.
- To judge: did click rate on store pages rise after 11-25? Did the 39 new pages get impressions within two days as earlier store pages did, or did Google hold them back?

## 2026-11-26

- Google's data still ends 11-24 (4,399 views / 12 clicks that day; 7 days: 8,442 views, 29 clicks, 0.3% click rate, position 18.9). So yesterday's changes (rate in search titles, rate history, 39 store pages) cannot be judged yet; first readable 11-27 or 11-28.
- Analytics, all-time: 149 users, 158 sessions; 33 from search, 6 from ChatGPT (2 yesterday), 0 from Medium, Bluesky or Pinterest. Referral clicks still 4 from 2 people; none new.
- Weakest step is unchanged: being clicked in the results. Change made today: the four store pages with the most views and the Black Friday page re-read and re-dated the day before Black Friday, so their search titles and descriptions carry today's rate; 5 more store pages (JCPenney, DoorDash, Uber, Hilton, Marriott), 2 before-joining pages, 1 page for the top unanswered query.
- Finding: JCPenney, DoorDash and Uber pay nothing on Rakuten today. The pages say so and what works instead.
- To judge tomorrow: clicks and click rate on store pages for 11-25 and 11-26 against 0.3%; whether ChatGPT visits keep rising.
- Also 11-26 (from the owner's chat): added `/rakuten-rate-history/` with a downloadable CSV and Dataset markup, linked from every store page and `llms.txt`, as the thing other sites and AI assistants can cite. A one-time job on Tue 12-01 10:30 AM writes to at most 5 cash back writers about it from team@. To judge: any visit with a referrer other than search or an assistant, and replies in the team@ inbox, from 12-02.

## 2026-11-26, afternoon run

- Google's data still ends 11-24: 11-21 87 views / 0 clicks; 11-22 1,085 / 7; 11-23 2,871 / 10; 11-24 4,399 / 12. Seven days: 8,442 views, 29 clicks, click rate 0.3%, position 18.9. Nothing new since this morning, so the 11-25 changes (rate in store search titles, rate history, 39 store pages) still cannot be judged; first readable 11-27 or 11-28.
- By kind of page: Rakuten store and holiday pages sit at positions 7 to 10 and took 20 of the 29 clicks (Best Buy 4 of 565 views, Walmart 3 of 162, Black Friday 2 of 771, Kohl's 2 of 115, Cyber Monday 2 of 74, the best rate at 2.7%). Card pages sit at 15 to 70 and took 4 clicks from about 4,000 views. The biggest single search, "rakuten best buy", was shown 172 times at position 8.8 with no click.
- Analytics: last 7 days 155 sessions, of which 115 are direct at 1 second (not people); 33 from search, 6 from ChatGPT, 1 referral. Today so far: 2 from ChatGPT, 1 from search, 1 referral. Referral clicks still 4 from 2 people. Nothing from Medium, Bluesky or Pinterest.
- Weakest step, unchanged: being clicked in the results. The pages are shown; they sit low on page one, and the search snippet already gives the answer.
- Change made: `build.py` now adds a table to the Black Friday page (the most-shown page) and the Cyber Monday page (the best click rate): every tracked store's headline Rakuten rate on each day from November 24, with a count of how many rose, fell or stayed (on 11-26: 35 higher, 6 lower, 28 the same, 8 with no cash back, of 73 stores). It adds a column by itself each day through November 30 and links every store page from the two pages. Reason: these two pages meet the four days of the year when these searches peak, and no other site shows which stores really raised their rate and on which day.
- Morning job steered: through 11-30 it re-reads and re-dates both holiday pages every day (the Cyber Monday page's answer was still dated 11-23).
- Number that should move: views and clicks on `/rakuten-black-friday-cash-back-2026/` and `/rakuten-cyber-monday-cash-back-2026/` for 11-27 to 11-30 against 771 views / 2 clicks and 74 / 2 so far; readable from 11-29, complete on 12-02. Also any ChatGPT visit landing on either page.
- Not done on purpose: no second change to store-page titles or descriptions while the 11-25 title test is unread.
- Confirmed live at 1:11 PM: both pages return 200 and show the table.

## 2026-11-27 (Black Friday), daily run

- Google: 11-24 is still the last full day (4,399 views / 12 clicks); 11-25 shows 346 / 1 so far, a partial day. Seven days: 8,788 views, 30 clicks, 0.3%, position 19.1. The 11-25 title test still cannot be judged.
- Analytics, all-time: 190 users, 201 sessions; search 41 (was 33), ChatGPT 17 (was 6), nothing from Medium, Bluesky or Pinterest. Referral clicks 8 from 6 people (was 4 from 2): the first day they doubled.
- Weakest step, unchanged: being clicked in the results. Change made today (live about 3:55 PM): Black Friday and Cyber Monday pages re-read and re-dated to today, titles now start with the words people type; Best Buy, Target, Walmart, Kohl's re-read; the step-by-step and is-it-legit pages rebuilt for people who have not joined; 8 new pages.
- Finding: Bath & Body Works, GameStop, Michaels, Anthropologie and Bose pay nothing on Rakuten today (two are "Coupons Only", three have no store page). `rates.py` cannot read "Coupons Only" titles, so those two get no daily reading.
- To fix next run: `chase-sapphire-preferred-rental-car-insurance` carries claim deadlines of 20 and 90 days; Chase's Guide to Benefits read today says 100 days to report and 365 for documents. Re-read and correct.
- Number that reads it tomorrow: clicks on the two holiday pages for 11-26 and 11-27 against 786 views / 2 clicks and 79 / 2; referral clicks against 8.
