# Project worksheet: valuing the option to store maize (agriBORA)

**Goal.** Build one Jupyter notebook that answers a real financial question
with course tools, validates the answer on data, and meets the Erdős Fall 2026
project requirements. This worksheet tells you what each notebook section
should do, which course lecture and `quantkit` function it uses, and what you
have to write yourself. It does not contain the notebook.

**Files** (paths relative to the repo root, `erdos_project/`)

| File | What it is |
|---|---|
| `quantkit.py` | Cleaned, tested course functions |
| `test_quantkit.py` | 28 tests; from the repo root, run `python -m unittest -v test_quantkit` before you start |
| `docs/agribora_worksheet.md` | This file |

Put the project notebook in the repo root, next to `quantkit.py`, so it can
simply `import quantkit as qk`.

---

## 1. The question

agriBORA runs certified warehouses in Kenya. A farmer who stores maize there
can sell at any week they choose instead of at harvest, but waiting costs
money: storage fees, some spoilage, and the interest on any loan taken against
the stored grain.

> **Financial question:** for a farmer holding maize at harvest, what is the
> option to delay the sale worth, and what week-by-week rule ("sell once the
> price reaches X in week w") captures that value? Does the rule beat simply
> selling at harvest on historical prices?

This is an **American-style option** with the payoff "the price when you sell",
a carrying cost, and a seasonal price drift. It is solved with the same
backward-induction tree as the American put in Lecture 9.

### The one modeling idea to get right (Lectures 5 and 7)

Black–Scholes and the risk-neutral tree price an option **as if it can be
hedged**: delta hedging removes the drift, so the drift is replaced by `r`
(Lecture 7). If you price storage that way, holding grain only makes sense when
the price is expected to grow faster than `r` plus the storage cost under the
*risk-neutral* measure, which for a hedgeable asset is never true. The answer
would always be "sell now".

A Kenyan smallholder generally **cannot** hedge maize. Check whether a liquid
exchange-traded maize contract exists for this market; if it does not, say so
in the write-up. Without a hedge, the decision depends on the **real-world
expected price path**, which for maize is seasonal. So in this project:

* `drift` = the estimated real-world seasonal growth rate of the maize price;
* `r` = the farmer's opportunity cost of money (e.g. the loan rate on a
  warehouse receipt), used for discounting;
* `holding_cost` = storage fees + spoilage, as a proportional rate per year.

`qk.binomial_optimal_stopping` takes these three inputs separately for this
reason. Explaining this contrast in your write-up is a strong signal of
understanding the course: it is exactly where the textbook model stops
applying.

---

## 2. Data

From the Zindi page (log in and accept the rules to download; the rules state
the data is open source):

| File | Contents | Use |
|---|---|---|
| `agriBORA_maize_prices.csv` | Weekly white-maize B2B transaction prices, Oct 2023 – Oct 2025 | The series the competition forecasts; short |
| `kamis_maize_prices.csv` (+ `_raw`) | KAMIS market prices 2021 – Jul 2025, many markets, white/yellow/mixed maize | Longer history for seasonality and volatility |
| `agriBORA_maize_prices_weeks_46_to_51.csv` | Weeks 46–51 of 2025 | Holdout |
| `agriBORA_Final_Weeks_maize_price.csv` | Final scoring weeks | Holdout for the forecast check |
| `StarterNotebook.ipynb` | Zindi starter code | Loading and submission format |

Target counties: **Kiambu, Kirinyaga, Mombasa, Nairobi, Uasin-Gishu**.
2025 has an ISO week 53, which Zindi asks you to label as week 1.

I could not open the CSVs (they need a Zindi login), so check the column names
and **price units** yourself (per kg vs per 90 kg bag, wholesale vs retail)
before combining the two sources.

---

## 3. Notebook sections

Each step lists the course lecture (numbering as in the course notes), the
`quantkit` functions to call, and the new code you write.

### Step 0 — Setup
* Create `data/raw/` (downloaded files, untouched) and `data/processed/`.
  `data/` is in `.gitignore`: the repo ships download instructions, not the
  data files.
* `import quantkit as qk`; fix a seed: `rng = np.random.default_rng(2026)`.
* Record where every file came from (the README needs it).

### Step 1 — Load and clean prices (Lecture 3a)
* **New code:** load both sources, keep white maize, choose wholesale,
  aggregate to one price per county per ISO week, convert units, and handle
  gaps (forward-fill at most one or two weeks; drop longer gaps and say so).
* Plot each county's series. Mark harvest periods you can see in the data.
* Output: a tidy DataFrame `week_start × county`.

### Step 2 — Returns and volatility (Lecture 3a)
* `qk.log_returns(prices)` on the weekly DataFrame.
* `qk.annualized_vol(r, periods_per_year=52)` per county.
* `qk.rolling_vol(r, window=13, periods_per_year=52)` (13 weeks ≈ a quarter).
* Question to answer: is volatility stable, or does it jump around harvest?

### Step 3 — Test the GBM assumptions (Lecture 8)
* `qk.test_normality(r)` per county. Report skewness, excess kurtosis and
  p-values. With ~100–200 weekly points the tests have limited power; say so.
* `qk.ljung_box(r, lags=8)` for momentum, and `qk.ljung_box(abs(r), lags=8)`
  for volatility clustering.
* **New code — seasonality:** average log return by calendar week (or month)
  across years, with standard errors (`qk.mc_estimate` on each group gives mean
  and SE). Plot it. **This plot is the core evidence for the project**: if
  there is no seasonal pattern, there is no reason to store.

### Step 4 — Build the price model (Lectures 4 and 11b)
* **Seasonal drift (new code):** estimate the expected log growth for each
  calendar week from the longer KAMIS history. Average across years, then
  smooth (a centered rolling mean, or a few sine/cosine terms) because a few
  years per week is noisy. Annualize: `drift_week × 52`.
* **Volatility:** start with the constant `annualized_vol` from Step 2.
* **Check the model by simulating it:** `qk.gbm_paths(S0, sigma, t, r,
  n_steps, n_sims, mu=drift_path - r, rng=rng)`. Note `gbm_paths` adds `r` to
  `mu`, so pass `drift - r` to get a total drift of `drift`. Compare the
  simulated spread of 13- and 26-week price changes with the historical
  spread. Are history's moves inside the simulated 5–95% band about 90% of
  the time?
* *Optional (Lecture 11b):* two volatility regimes. Classify weeks as
  low/high volatility from the rolling vol, estimate how long each regime
  lasts, set `alpha`, `beta` = 1 / mean duration (in years), and simulate with
  `qk.markov_vol_states(...)` feeding a `sigma` array into `qk.gbm_paths`.

### Step 5 — Forecast check against the competition (validation)
* The model's 1- and 2-week forecast is the expected price,
  `S_t × exp(sum of drift × dt)` over the next one or two weeks.
* **New code:** a rolling-origin backtest. At each week, use only data up to
  that week, forecast one and two weeks ahead, and record the error.
* Score with the competition's metrics, MAE and RMSE, against two baselines:
  (a) last price, and (b) last price × last year's same-week change.
* Score once on the released holdout files. If Zindi still accepts
  submissions for the closed competition, submit for an official score;
  otherwise report your holdout score and say it is unofficial.
* The point is not to win the leaderboard. It is to show that the seasonal
  drift you will use for valuation actually forecasts.

### Step 6 — Value the storage option (Lecture 9)
```python
value, sell_prices = qk.binomial_optimal_stopping(
    S0=price_at_harvest,          # current price
    sigma=sigma,                  # Step 2 / 4
    t=horizon_weeks / 52,         # e.g. 26 weeks of possible storage
    n_steps=horizon_weeks * k,    # k steps per week, e.g. k = 4
    payoff=lambda S: S,           # selling earns the price
    r=loan_rate,                  # discount rate
    drift=np.repeat(weekly_drift, k),   # seasonal path starting at the harvest week
    holding_cost=storage_rate + spoilage_rate,
    return_exercise=True,
)
option_value = value - price_at_harvest
```
* **Inputs to look up and cite:** warehouse storage fees (convert a per-bag
  fee into a proportional rate: fee per year ÷ price), a loss rate for
  certified storage (the competition text says traditional post-harvest
  losses reach 40%; warehouses should be far lower), and a Kenyan lending rate
  for warehouse-receipt loans. Each one is an assumption; label it.
* **Sell rule:** for step `i`, `sell_prices[i]` lists the tree prices at which
  selling is optimal. Its minimum, plotted against the week, is the boundary
  "sell once the price is at least this". Plot it against the seasonal
  average price.
* If you see `ValueError: CRR probability outside [0, 1]`, raise `k`: the
  seasonal drift is too steep for the step size.
* **Sanity checks, copied from the tests:**
  * if drift ≤ `r + holding_cost` in every week, value = S0 (sell now);
  * if drift is far above it, value = S0·e^{(drift − r − cost)t} (store to the end);
  * the value converges as `k` grows (try k = 1, 2, 4, 8).

### Step 7 — Check the tree with Monte Carlo (Lecture 2)
* Simulate paths from the same model (`qk.gbm_paths`, same drift and σ) and
  apply the Step 6 sell rule along each path.
* Discount each path's net revenue (price × e^{−holding_cost·τ} × e^{−r·τ})
  and use `qk.mc_estimate` to get mean ± SE.
* The mean should match the tree value within about 2 SE (discretization
  makes it slightly lower). This is the course's standard "check the
  numerical method against an independent one" step.

### Step 8 — Backtest on real price history (the main validation, Lecture 8)
* **New code:** for every county and every harvest season in the data, start
  at the harvest week and run three strategies on the actual price path:
  1. sell at harvest;
  2. sell at a fixed calendar week (e.g. the historically most expensive week);
  3. the tree's sell rule, **re-estimated using only data before that
     season** (no look-ahead).
* Compare net revenue per kg after storage, spoilage and interest. Report
  mean, spread and worst case across county-seasons.
* With about 4 seasons × 5 counties you have about 20 observations; bootstrap
  the difference between strategies 3 and 1 for a confidence interval, and
  say plainly if it includes zero.

### Step 9 — Sensitivities, the "Greeks" of storage (Lecture 6)
* Finite differences of the option value with respect to σ ("vega"),
  `holding_cost`, `r`, and the size of the seasonal drift. Use the same
  bump-and-reprice method as the Lecture 6 numerical Greeks.
* Plot the boundary for a few storage costs. Where does storage stop being
  worth it? That break-even storage fee is a concrete number agriBORA could
  use.

### Step 10 — Optional extensions
* **Model risk (validation track):** evaluate the Step 6 rule on paths from
  the regime-switching model in Step 4. How much value is lost if volatility
  is wrong?
* **Many counties:** correlated shocks across counties with
  `qk.correlated_normals(corr, size)`, using the correlation of county
  returns, and a question about where to sell, net of transport cost.
* **Risk aversion:** the valuation assumes a farmer who cares only about the
  expected outcome. A risk-averse farmer would discount uncertain gains, so
  show how the rule changes if they do.

---

## 4. Course map

| Step | Lecture(s) | `quantkit` | New code |
|---|---|---|---|
| 1 Data | 3a | — | Loading, cleaning, units, weekly aggregation |
| 2 Returns/vol | 3a | `log_returns`, `annualized_vol`, `rolling_vol` | — |
| 3 Assumption tests | 8 | `test_normality`, `ljung_box`, `mc_estimate` | Seasonality by calendar week |
| 4 Price model | 4, 11b | `gbm_paths`, `markov_vol_states` | Seasonal drift estimate, coverage check, regime estimation |
| 5 Forecast check | 2 | — | Rolling-origin backtest, MAE/RMSE, baselines |
| 6 Storage option | 9 | `binomial_optimal_stopping` | Input research, boundary plot |
| 7 MC check | 2 | `gbm_paths`, `mc_estimate` | Apply rule along paths |
| 8 Historical backtest | 8 | — | Strategy simulator, bootstrap |
| 9 Sensitivities | 6 | `binomial_optimal_stopping` | Bump-and-reprice loop |
| 10 Extensions | 3b, 11b | `correlated_normals`, `markov_vol_states` | As chosen |

Not used here (but tested and available): Black–Scholes prices and Greeks,
`bs_implied_vol`, `american_put`, `american_call`. The European/American
option functions are a good way to explain the tree in your write-up: show
that `binomial_optimal_stopping` reproduces `american_put` before you change
its payoff to "sell the grain".

---

## 5. How this meets the Fall 2026 requirements

| Requirement | Where it is met |
|---|---|
| Clearly stated financial question | Section 1 |
| Appropriate method | American-option tree with seasonal drift (Steps 4, 6) |
| Real data | agriBORA + KAMIS prices (Steps 1–3) |
| Validation / benchmarking | Forecast scores vs baselines (5), tree vs MC (7), historical backtest vs simple rules (8) |
| Financial interpretation | Option value in KES/kg, sell rule, break-even storage fee (6, 9) |
| Assumptions, limitations, failure modes | Section 6 below |
| Beyond models taught in class | Seasonal real-world drift and carry cost in an optimal-stopping problem; GBM and Heston are not the point of the project |

**Deliverables:** a GitHub repo containing the notebook, `quantkit.py`, the
tests and a README with data download steps; a 1–2 page executive summary
(question, method, main numbers, limitations); a short video.

---

## 6. Limitations to state up front

* Short history: about 2 years of agriBORA prices and 4–5 of KAMIS, so the
  seasonal drift is estimated from a handful of seasons. Quantify the
  uncertainty (Step 3 SEs, Step 8 bootstrap).
* Transaction (B2B) and market prices are not farm-gate prices.
* Fixed per-bag fees are approximated as proportional costs.
* Lognormal weekly moves and constant volatility are tested in Step 3, not
  assumed; report where they fail.
* No hedge, so the value is a decision value for a farmer who cares only about
  the expected outcome, not a market price.
* Policy shocks (import duties, government purchases) are not modeled and can
  dominate a season.
