# Video script — 5 minutes, matched to the slide deck (maize_storage.pdf, 5 slides)

≈ 720 spoken words, conversational: ≈ 5 minutes at a natural pace (4.8–5.3 min).
The full 12-slide version is `docs/video_script.md`.

Suggested slide-text changes (see notes): slide 3 second headline; slide 5 headline.

---

## Slide 1 — Title + price history  *(figure 01)*

Maize is Kenya's staple food, and Uasin-Gishu is one of the places it's grown most. Farmers there
harvest between October and December — exactly when prices are lowest — and most sell right away. They
need the cash, and grain kept at home can lose up to a third of its weight in a year. But in Eldoret,
agriBORA now runs a warehouse, agriGHALA, where farmers can store grain safely and borrow against it.
So my question was: if you're holding maize after the harvest, is it worth waiting to sell — and when?

Waiting pays off if the price rises by more than it costs you to wait. That cost has two parts:
interest on the money you're waiting for — about 15% a year in Kenya — and storage: about 3% a year in
a warehouse, or around 20% of the grain lost on the farm. What we don't know is how much the price will
rise. That's what this chart is for: nineteen years of monthly Eldoret prices from the World Food
Programme and Kenya's market information system. The project grew out of a Zindi price-forecasting
challenge.

## Slide 2 — Monthly prices 2006–2025  *(figure 02)*

So does the price really rise after harvest? Each line here is one season, December to November. On the
left are the actual prices — all over the place from year to year. But on the right I've divided each
season by its own harvest price, and a pattern jumps out: prices climb from January, peak around June,
and fall back as the next harvest arrives.

And it's not a fluke. In fifteen of seventeen seasons, the price in May to July beat the harvest price —
about a one-in-a-thousand chance if there were no real pattern.

## Slide 3 — The model  *(figures 03 and 04)*

To use this, I need a model. The top plot shows the average price change in each month, with a single
sine wave fitted through it. Prices rise fastest in March and April and stop rising after June, so the
price tops out about six months after harvest — around 34% above December. And the curve really
predicts: on data it hadn't seen, it cut three-month forecast errors from 19% to 15%.

Prices don't follow the curve exactly, so I add a random part on top — a random walk in the log price,
called geometric Brownian motion. Its volatility is about 0.4 a year, roughly like a single risky stock.
And as the bottom plot shows, it's highest in shock years — when prices shoot up, like 2011 and 2022,
and when they crash afterwards, like 2010 and 2018.

## Slide 4 — The binomial tree  *(figure 08)*

Now I can ask: when should you sell? In finance this is an American option — you can sell at any time,
and you want the best moment. I solve it on a binomial tree: each month the price goes up or down, with
odds set by the seasonal cycle, and working backwards from the end of the season, every point asks:
sell now, or wait another month?

Here's what comes out. Every node says "wait" — all the way to June. Then in June, every node says
"sell", whatever the price. That's because the expected rise depends only on the month, and every cost
scales with the price — so the best decision is just a date on the calendar. Unlike a normal option,
volatility adds nothing here.

## Slide 5 — Gains and break-evens  *(figure 07)*

So what's it worth? After all costs, waiting until June gains about 27% in a warehouse and 18% on the
farm. To check this against reality, I replayed the decision on seventeen real seasons, using only what
a farmer would have known at the time. Warehouse storage won in thirteen of them, with an average gain
of 28% — still 25% without the 2022 drought spike. But two bad seasons lost 28 to 57%. And these plots
show storage keeps paying up to about 50% interest, or 45% on-farm losses a year — so the warehouse's
real value is removing losses.

The limits: one market, seventeen seasons, and no model of government interventions. What I learned:
option pricing usually assumes you can hedge, and with no maize futures in Kenya you can't — so you
have to estimate the real price path. And a fairly sophisticated model boiled down to a simple idea:
storage pays when the price rises faster than the cost of waiting.

---

### Notes on slide text

* **Slide 3, "Year-to-year volatility tracks droughts":** not supported as stated — volatility is
  highest in years of large price shocks in either direction (2010 and 2018 were price falls; the
  2017 drought year had only middling volatility), and drought data was not part of the analysis.
  Suggested: *"Volatility is highest in shock years: sharp rises and the falls after them."*
* **Slide 3, "peaking 6 months from harvest":** correct for the price level (June); the top plot shows
  the monthly change, which peaks in March–April — the voiceover explains this.
* **Slide 5, "up to 35% gain … regardless of whether … warehouse or on the farm":** 35% is the
  warehouse case at a 5% interest rate; at realistic costs the gains are ≈ 27% (warehouse) vs ≈ 18%
  (on-farm). Suggested: *"Waiting until June gains ≈ 27% in a warehouse and ≈ 18% on the farm — and
  keeps paying up to ≈ 50% interest or ≈ 45% annual losses."*
* **Recommended sixth slide (between 4 and 5):** figure 06, realized gain by season — the main
  validation, currently only in the voiceover. If added, move the "To check this against reality…" sentences
  from slide 5 onto it.
* **Slide 1:** add the inequality with i ≈ 15%, c ≈ 3% (warehouse) / 20% (on-farm) as a caption, a
  source line (WFP / KAMIS via HDX; inspired by the Zindi agriBORA challenge) and your name.
* **Slide 4:** add a title, e.g. *"Optimal rule: sell at the end of June, whatever the price."*
* **Closing:** limitations and lessons are required in the video; they are in the slide-5 voiceover,
  or add a short closing slide with 3–4 bullets.

---

### Sources (for slide captions and the video description; not spoken)

**Price data**
* World Food Programme (2026). *Kenya – Food Prices* [data set], Humanitarian Data Exchange (HDX),
  dataset e0d3fba6-f9a2-45d7-b949-140c455197ff, last updated 4 Nov 2026, CC BY-IGO.
  https://data.humdata.org/dataset/wfp-food-prices-for-kenya — Eldoret town wholesale maize, 2006–2025.
* Zindi & agriBORA (2025–26). *agriBORA Commodity Price Forecasting Challenge* [data set]
  (KAMIS market prices, Kenya Ministry of Agriculture), Zindi.
  https://zindi.africa/competitions/agribora-commodity-price-forecasting-challenge — fills 5 missing months.

**Cost inputs**
* Interest rate (≈ 15%/yr): Central Bank of Kenya average commercial-bank lending rate, May 2025
  (15.44%) and Dec 2025 (14.8%), as reported by HapaKenya (2 Jul 2025) and Business Daily.
* Storage fees and storage, loans, harvest calendar: Kenduiywo, B. et al. (2026). *Enabling
  private-sector innovation in agricultural storage: Lessons from the agriGHALA warehouse receipt
  model in Kenya*. CIAT / agriBORA / P4G policy brief. https://hdl.handle.net/10568/182900 ;
  Warehouse Receipt System tariff as reported by People Daily (n.d.).
* On-farm losses: De Groote, H., Muteti, F. N., & Bruce, A. Y. (2023). On-farm storage loss estimates
  of maize in Kenya using community survey methods. *Journal of Stored Products Research* 102, 102107.
  https://doi.org/10.1016/j.jspr.2023.102107

**Suggested one-line caption for slide 1:**
*Data: WFP Kenya Food Prices (HDX, CC BY-IGO); KAMIS via the Zindi agriBORA Commodity Price
Forecasting Challenge.*

Full references: `docs/references.md`.
