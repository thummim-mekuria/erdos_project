# Video script — 5 minutes, matched to the slide deck (maize_storage.pdf, 5 slides)

≈ 620 spoken words: ≈ 4.5 minutes of speaking, ≈ 5 minutes with pauses.
The full 12-slide version is `docs/video_script.md`.

Suggested slide-text changes (see notes): slide 3 second headline; slide 5 headline.

---

## Slide 1 — Title + price history  *(figure 01)*

Maize is Kenya's staple food. Farmers in Uasin-Gishu, the main maize region, harvest between October
and December, when prices are lowest, and most sell straight away: they need cash, and grain kept at
home loses up to a third of its weight a year. In Eldoret, agriBORA's agriGHALA warehouse now lets
farmers store insured grain and borrow against it. So: is waiting to sell worth it, and when?

The answer comes down to one inequality. Selling in month t instead of December pays if the expected
price ratio, P_t over P_0, beats the cost of waiting: interest of about 15% a year — the cost of the
money you wait for — plus storage costs of about 3% a year in a warehouse, or about 20% of the grain
lost on the farm. This plot shows the data: 19 years of monthly Eldoret wholesale prices from the
World Food Programme and Kenya's market information system, with each December marked. The project was inspired by a Zindi price-forecasting challenge.

## Slide 2 — Monthly prices 2006–2025  *(figure 02)*

Each line is one season, December to November. On the left are actual prices, which differ a lot from
year to year. On the right, each season is divided by its own harvest price, and a common shape
appears: prices climb from January, peak around June, and fall back at the next harvest.

This is not noise. In 15 of 17 seasons, the price in May to July was above the harvest price — a sign
test gives p of 0.001 — and a permutation test confirms the annual cycle.

## Slide 3 — The model  *(figures 03 and 04)*

The top plot shows the average price change in each month, with a single sine wave fitted through it,
chosen by cross-validation. Prices rise fastest in March and April and stop rising after June — so the
price level peaks about six months after harvest, roughly 34% above December. On data it had not seen,
this curve cut three-month forecast errors from 19% to 15%.

Around that cycle, prices move randomly — I model the log price as a random walk, geometric Brownian
motion, with volatility of about 0.40 a year: like a single risky stock, about twice a stock index.
The bottom plot shows it is not constant: it is highest in shock years, both sharp rises like 2011 and
2022 and the falls that follow, like 2010 and 2018.

## Slide 4 — The binomial tree  *(figure 08)*

Choosing when to sell is an optimal stopping problem — in finance, an American option. I solve it on a
binomial tree: each month the price goes up or down, with odds set by the seasonal cycle, and working
backwards from November each node compares selling now with waiting.

Every node waits until June, and in June every node sells — whatever the price. Because the payoff
and every cost are proportional to the price, and the expected growth depends only on the month, the
best decision depends only on the calendar. Unlike a normal option, volatility adds no value here.
Selling in June is worth about 28% more than selling in December, before the warehouse's one-off fee.

## Slide 5 — Gains and break-evens  *(figure 07)*

Net of all costs, waiting until June gains about 27% in a warehouse and 18% on the farm, where losses
eat into the gain. Replaying the decision on 17 real seasons, using only information available at the
time, warehouse storage beat selling at harvest in 13 of them, with an average gain of 28% — still 25%
without the 2022–23 drought spike — though two bad seasons lost 28 to 57%. These plots show how far costs can rise: storage keeps paying up to an
interest rate of about 50%, or on-farm losses of about 45% a year. So the value of a certified
warehouse lies mainly in removing losses.

The limits: one wholesale market, 17 seasons, and no model of government interventions. What I
learned: option pricing assumes you can hedge — Kenyan maize has no futures, so the real price path has
to be estimated — and a sophisticated model can reduce to a simple principle, the cost of carry.

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
  validation, currently only in the voiceover. If added, move the "Replaying the decision…" sentences
  from slide 5 onto it.
* **Slide 1:** add the inequality with i ≈ 15%, c ≈ 3% (warehouse) / 20% (on-farm) as a caption, a
  source line (WFP / KAMIS via HDX; inspired by the Zindi agriBORA challenge) and your name.
* **Slide 4:** add a title, e.g. *"Optimal rule: sell at the end of June, whatever the price."*
* **Closing:** limitations and lessons are required in the video; they are in the slide-5 voiceover,
  or add a short closing slide with 3–4 bullets.
