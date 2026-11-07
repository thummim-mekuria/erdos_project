# Executive summary — The value of waiting to sell: maize storage in Uasin-Gishu, Kenya

*Erdős Institute, Quantitative Methods in Finance, Fall 2026 — Thummim Mekuria*

## Problem

Smallholder maize farmers in Uasin-Gishu (Eldoret), Kenya's main maize-producing region, usually
sell at harvest (October–December), when prices are lowest. Certified warehouses such as
agriBORA's agriGHALA (Eldoret, opened Dec 2024) let farmers store grain safely and borrow against
it, so they can sell later. **What is the option to wait worth, when should the farmer sell, and
does storing actually beat selling at harvest after interest, fees and losses?**

## Data

19 years of monthly wholesale maize prices for Eldoret (WFP / HDX, 2006–2025; five gaps filled
from KAMIS, which WFP republishes): 225 of 234 months. Cost inputs from published sources: loan
rate 15%/yr (Central Bank of Kenya average lending rate, 2025), warehouse fee ≈ 3%/yr plus a
1.5% one-off charge (Warehouse Receipt System tariff), losses 0% in an insured certified warehouse
vs 20%/yr on-farm (Kenyan storage-loss surveys, range 10–36%).

## Method

1. **Seasonality tests:** Kruskal–Wallis across months, a random-phase permutation test on the
   annual cycle, and a sign test on the harvest-to-lean-season rise.
2. **Price model:** GBM with a seasonal drift (annual harmonic fitted by least squares, number of
   harmonics chosen by leave-one-year-out cross-validation) and constant volatility estimated from
   de-seasonalized returns; the typical (median) growth converted to the expected (mean) growth
   the tree needs (a σ²/2 correction, from Jensen's inequality for a lognormal).
3. **Valuation:** the storage decision as an American-style optimal-stopping problem solved on a
   binomial lattice (dynamic programming), using the **real-world** drift because maize cannot be hedged in
   Kenya (no exchange-traded maize futures), with interest as the discount rate and fees + losses
   as a holding cost.
4. **Validation:** out-of-sample forecast test vs a random walk; Monte Carlo check of the tree; a
   backtest on 17 real seasons with the model re-estimated each season using only earlier data;
   an out-of-sample test of a price-threshold sell rule; bump-and-reprice sensitivities.

## Findings

* **The seasonal cycle is strong and stable.** Prices rose from the December–January harvest
  level to May–July in 15 of 17 seasons (sign test p = 0.001; permutation p = 0.0002); the expected
  rise to June is ≈ 34%. The seasonal model beats a random walk at a 3-month horizon out of sample
  (absolute log error 15.1% vs 18.6%; bootstrap CI excludes zero).
* **Value of storing (model):** ≈ **+27%** of the December price in a certified warehouse, ≈ +18%
  on-farm at 20%/yr losses. The best time to sell is **June**.
  At 40 KSh/kg this is ≈ KSh 950 per 90-kg bag in a warehouse vs ≈ KSh 630 on-farm.
* **The "option" is a calendar decision.** Because the payoff is the price and all costs are
  proportional to it, under GBM the tree value equals the best fixed sale month exactly — waiting
  has no value beyond timing, and no price-dependent rule exists. A price-threshold rule
  ("sell early if the price is X% above its usual path"), chosen on earlier seasons only, never
  selected an early sale: the data agrees with the calendar rule.
* **Real seasons (no look-ahead):** warehouse storage gained **+28% on average** (median +17%,
  95% CI 7–52%) and beat selling at harvest in 13 of 17 seasons; excluding the 2022–23 drought
  spike the mean is still +25%. On-farm storage gained +15% (CI −2% to 33%). The two worst seasons
  lost 28–57%.
* **Break-evens:** warehouse storage keeps paying up to a loan rate of ≈ 53% (history) – 68%
  (model); on-farm storage up to a loss rate of ≈ 45–60%/yr.

**Interpretation for agriBORA:** the economic case for certified storage is mainly the removal of
on-farm losses — interest and fees are small relative to the ≈ 30% seasonal rise. Storing to June
pays on average and in most years, but farmers should expect occasional large losses; receipt
financing (which avoids distress sales) makes it possible to hold through the season.

## Limitations and failure modes

* One wholesale market (Eldoret); agriBORA B2B prices run ≈ 10–25% below wholesale, farm-gate prices lower still.
* Monthly data (decisions checked monthly), 9 missing months, only 17 seasons — the confidence
  intervals are wide.
* Costs are 2020–2026 point estimates applied to 2006–2025 prices; per-bag fees approximated as
  proportional.
* Shocks are fat-tailed, cluster in volatility, and show year-to-year mean reversion; GBM ignores
  these. The backtest on real price paths is the check against model error.
* A risk-neutral farmer is assumed; a risk-averse farmer would store less because of the bad years.
* Policy shocks (duty-free import windows, NCPB purchases) are not modelled and can dominate a
  season.

## What I learned

The textbook risk-neutral pricing does not apply when the underlying cannot be hedged; the
real-world drift has to be estimated and validated. And a model can be "correct" yet degenerate:
with a linear payoff and proportional costs, an American-option tree reduces to a calendar rule —
something worth recognising rather than hiding.
