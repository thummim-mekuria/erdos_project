# Video script — 5-minute version

Eight slides, ≈ 680 spoken words (≈ 5 minutes). Figures are in `figures/notebook/`.
The full 12-slide version is `docs/video_script.md`.

---

## 1 — The question  *(title; figure 01)*

Kenyan farmers harvest maize between October and December, when prices are lowest, and most sell
straight away: they need cash, and grain stored at home loses up to a third of its weight a year.
In Eldoret, agriBORA's agriGHALA warehouse now lets farmers store insured grain and borrow against
it. So: is waiting worth it, and when should they sell? This project was inspired by a Zindi
maize-price challenge; I asked the decision question behind the forecast.

## 2 — One inequality  *(equation)*

Selling at month t instead of December pays if the expected price ratio, P_t over P_0, times e to
the minus (i plus c) t, is greater than one. Here i is the interest rate — the cost of waiting for
your money, about 15% a year in Kenya — and c is the holding cost: about 3% a year in a warehouse,
or about 20% a year of grain lost on the farm. Only the expected price rise has to be estimated
from data.

## 3 — Is there a seasonal cycle?  *(figure 02)*

I used 19 years of monthly wholesale prices for Eldoret. On the left, each season's actual prices;
on the right, each season relative to its own harvest price. A common shape appears: prices climb
from January, peak around June, and fall back at the next harvest. In 15 of 17 seasons the price was
higher in May to July than at harvest — a sign test gives p of 0.001.

## 4 — The model  *(figure 03)*

I fit the seasonal pattern with a single sine wave, chosen by cross-validation, and model the rest
as a random walk in the log price — geometric Brownian motion — with a volatility of about 0.40.
The curve predicts prices it has not seen: three months ahead it cuts the forecast error from 19%
to 15%. It implies a typical rise of about 34% from December to June.

## 5 — When to sell, and what it is worth  *(figure 08, then 05)*

Choosing when to sell is an optimal stopping problem — an American-style option. I solve it on a
binomial tree by working backwards from November. Every node waits until June and sells in June,
whatever the price: because the payoff and all costs are proportional to the price, the decision
depends only on the calendar. Waiting until June is worth about 27% of the December price in a
warehouse, and 18% on the farm.

## 6 — Does it work on real seasons?  *(figure 06)*

Then I replayed the decision on 17 real seasons, using only information available at the time.
Warehouse storage beat selling at harvest in 13 of 17 seasons, with an average gain of 28% after
interest and fees — 95% interval 7 to 52%. But the bad seasons are real: two of them lost 28 to
57%. A price-dependent rule — selling early when prices run ahead — never helped.

## 7 — Costs, and how this compares  *(figure 07)*

Warehouse storage keeps paying up to an interest rate of about 53 to 68% a year; on the farm, up to
losses of about 45 to 60% a year. Compared with stocks: the average gain per unit of risk is similar
to a stock index, but maize has a predictable seasonal rise that storage costs and credit limits keep
from being traded away. And unlike a normal option, volatility adds no value here — the option to
wait collapses to a calendar rule.

## 8 — Limitations and what I learned

Limitations: one wholesale market, only 17 seasons, recent cost estimates applied to two decades of
prices, and no model of government interventions. What I learned: option pricing assumes you can
hedge; when you cannot, you must estimate the real price path. A sophisticated model can reduce to a
simple principle — here, cost of carry. And the most convincing evidence came from the simplest test:
replaying real seasons.
