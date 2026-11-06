# Project worksheet: valuing the option to store maize in Uasin-Gishu

*Revised 2026-11-06. Scope narrowed to Uasin-Gishu (Eldoret) wholesale prices;
data, storage costs and course content (through Fall 2026 L12) updated.*

**Goal.** One Jupyter notebook that answers a real financial question with
course tools, validates the answer on data, and meets the Erdős Fall 2026
project requirements (§6). This worksheet says what each notebook section
does, which lecture and `quantkit` function it uses, what is already done, and
what is new code. It is not the notebook.

**Files** (relative to the repo root `erdos_project/`)

| File | What it is |
|---|---|
| `quantkit.py`, `test_quantkit.py` | Cleaned, tested course functions; 38 tests (`python -m unittest -v test_quantkit`) |
| `data/processed/wfp_monthly_wholesale.csv` | **The price series** (county = `Uasin-Gishu`): Eldoret monthly wholesale, KSh/kg, 2006-01 → 2025-06 |
| `data/nairobi_uasingishu/agribora_weekly.csv` | agriBORA's own Uasin-Gishu weekly prices, 2023-10 → 2026-01 |
| `data/nairobi_uasingishu/kamis.csv` | KAMIS market-level rows (Eldoret Main etc.), 2021-05 → 2025-07 |
| `data/make_data.py`, `data/README.md` | How the series was built; sources and licenses |
| `figures/seasonality.py` | Seasonality tests + figure (Step 3, done) |
| `figures/make_figures.py` | Price-history figures |

Put the notebook in the repo root so it can `import quantkit as qk`.

---

## 1. The question

agriBORA runs a certified warehouse in **Eldoret** (agriGHALA, opened Dec
2024). A Uasin-Gishu farmer who deposits maize there can sell in any month,
and can borrow against the warehouse receipt instead of selling at harvest.
Waiting costs money: storage fees, interest, and (outside a warehouse) losses.

> **Financial question:** for a Uasin-Gishu farmer holding maize after the
> October–December harvest, what is the option to delay the sale worth, and
> what month-by-month rule ("sell once the price reaches X in month m")
> captures it? Does that rule beat selling at harvest on 17+ seasons of real
> Eldoret prices, after realistic costs? How does the answer change between
> warehouse storage and on-farm storage?

This is an **American-style option** whose payoff is "the price when you sell",
with a carrying cost and a seasonal drift, solved by the same backward
induction as the Lecture 9 American put.

### The one modeling idea to get right (Lectures 5, 7)

Risk-neutral pricing assumes the option can be hedged, which replaces the
drift by `r` — and then storing never pays. **Maize in Kenya cannot be
hedged:** the only licensed derivatives exchange, NSE NEXT, lists index and
single-stock futures, not maize [S9]; KOMEX, the national commodity exchange,
provides spot price benchmarks and plans futures "at a later stage" [S8, S10].
So the decision uses the **real-world** seasonal price path:

* `drift` = estimated real-world seasonal growth rate of the Eldoret price;
* `r` = the farmer's cost of money (loan rate against the receipt), for discounting;
* `holding_cost` = storage fees + losses, as a proportional rate per year.

`qk.binomial_optimal_stopping` takes these separately for exactly this
reason. Explaining this is where the project goes beyond the textbook model.

---

## 2. Data (done)

**Prices.** Eldoret town monthly wholesale price, KSh/kg, 2006-01 → 2025-06:
225 of 234 months present (missing 2020-04/05, 2023-12, 2024-01,
2024-10 → 2025-01, 2025-03). Built from three WFP series plus five months of
KAMIS Eldoret Main, which matches WFP where both exist (median ratio 1.00) —
WFP republishes KAMIS. Details in `data/README.md`.

**Known features to handle in the notebook**

* **Inflation:** the level rises ≈ 13 → 35 KSh/kg over 2006–2021. Either
  deflate by Kenya CPI (KNBS, monthly) and use a real `r`, or stay nominal
  throughout. Don't mix a real drift with a nominal loan rate.
* **2022–23 drought spike:** peaks of 90.3 (Jul 2022) and 90.4 (Jun 2023),
  confirmed by KAMIS. Estimate with and without it (Step 4).
* **Price level:** agriBORA's own prices run ≈ 0.77× wholesale. Take the
  seasonal shape and volatility from WFP; optionally take today's price `S0`
  from `agribora_weekly.csv`. State the choice.

---

## 3. Inputs from outside the price data

Every number is an assumption with a source; vary each in Step 9.

| Input | Base case | Range for Step 9 | Source / reasoning |
|---|---|---|---|
| **Harvest / start month** | **December** (sell from Dec onward) | Nov – Jan | Uasin-Gishu harvest Oct–Nov [S6]; agriGHALA brief: harvest window Oct–Dec, lean season May–Aug [S1 p.4]; Eldoret price low is Dec–Jan (Step 3) |
| **Horizon** | 9 months (Dec → Aug) | 6 – 11 | Lean season ends Aug [S1]; next harvest Oct |
| **Storage fee** | **3%/yr** of value (+1.5% one-off first month) | 1.5 – 4.5%/yr | WRS: KSh 48/90-kg bag first month, KSh 9/month after [S2]; a private warehouse KSh 70 then 10 [S3]; NCPB KSh 3/50-kg bag/month [S3]. At 40 KSh/kg (3,600/bag) KSh 9/month = 3.0%/yr |
| **Losses, certified warehouse** | **0%** | 0 – 2%/yr | agriGHALA deposits are insured against loss; grain accepted only at ≤ 13.5% moisture, fumigated [S1 p.5] |
| **Losses, on-farm** (comparison) | **20%/yr** | 10 – 36%/yr | Kenya on-farm storage loss ≈ 36%/yr (community survey; authors note it is high vs other studies) [S4]; 20–36% [S5]; agriGHALA Q1 2026: 2,800 kg loss avoided on 18,669 kg stored (≈ 15%) [S1 p.10] |
| **Loan rate `r`** | **15%/yr** | 10 – 17% | CBK average commercial bank lending rate 15.4% (May 2025), 14.8% (Dec 2025) [S7]; AFC lends at ≈ 10% [S11]. Receipt loans up to 70% of grain value [S1 p.5] |
| **Total cost check** | — | — | agriGHALA worked example (2022): KSh 3,500/bag in April → 6,000–6,500 in July; ≈ KSh 1,100/bag storage + handling + financing; net ≈ +40% vs selling at harvest [S1 p.4]. Use it as a sanity check of Step 6's magnitude |

What the costs imply before any modelling: fees are small (≈ 3%/yr); the loan
rate (≈ 15%/yr) dominates in a warehouse, and losses dominate on-farm. The
seasonal rise from Dec–Jan to June averages ≈ 33% in ≈ 5 months (Step 3), so
storage plausibly pays in a warehouse and is marginal on-farm. The notebook
has to show whether this survives volatility and bad years.

---

## 4. Notebook sections

### Step 1 — Load and inspect (Lecture 3a) — *mostly done*
* Load `wfp_monthly_wholesale.csv`, keep `Uasin-Gishu`, index by month.
* Reproduce the price-history figure (`figures/make_figures.py`) and mark
  harvest (Oct–Dec) and lean (May–Aug) months.
* Decide nominal vs real (CPI) and apply it here.

### Step 2 — Returns and volatility (Lecture 3a)
* `qk.log_returns`, `qk.annualized_vol(r, periods_per_year=12)` —
  ≈ 43%/yr nominal over 2006–2025.
* `qk.rolling_vol(r, window=12, periods_per_year=12)`. Is volatility higher
  in the lean season or in crisis years? (Feeds Step 4's regime option.)

### Step 3 — Test the GBM assumptions and the seasonal cycle (Lecture 8) — *seasonality done*
* `qk.test_normality(r)`, `qk.ljung_box(r, lags=12)`,
  `qk.ljung_box(abs(r), lags=12)`; report and say where GBM fails.
* **Seasonality (done, `figures/seasonality.py`):** Kruskal–Wallis across
  months p = 2e-5; annual sine cycle 6.7%/month, random-phase permutation
  p = 0.0002; price higher in May–Jul than Dec–Jan in **15 of 17** seasons
  (sign test p = 0.001); significant in both halves of the sample. Average
  path: +33% by June, falling back by November. The two down years (2010
  −30%, 2018 −15%) are the risk the option must price.

### Step 4 — Price model (Lectures 4, 11b; F26 L12 calibration)
* **Seasonal drift:** expected log return for each calendar month. Smooth it
  by fitting `a + Σ_k [b_k sin(2πkm/12) + c_k cos(2πkm/12)]` (k = 1, 2) with
  `scipy.optimize.least_squares` — the same tool L12 uses to calibrate Heston.
  Annualize: `drift_month × 12`.
* **Two calibrations:** (A) 2006–2021, (B) 2006–2025 incl. the 2022–23 spike.
  Carry both through Steps 6–8; the gap between them is a result.
* **Volatility:** constant σ from Step 2 to start.
* **Model check by simulation:** `qk.gbm_paths(S0, sigma, t, r, n_steps,
  n_sims, mu=drift_path - r, rng=rng)` (`gbm_paths` adds `r` to `mu`).
  Are historical 3- and 6-month changes inside the simulated 5–95% band
  about 90% of the time?
* *Optional, two regimes (L11b):* calm vs crisis volatility with
  `qk.markov_vol_states`, durations from Step 2's rolling vol.
* *Optional, stochastic volatility (F26 L12):* `qk.heston_paths` gives
  mean-reverting random variance. It takes a constant drift, so add the
  seasonal part by multiplying each path by
  `exp(cumulative seasonal drift − constant drift)`. Fit κ, θ, ξ by matching
  the level, persistence and spread of rolling variance — there are no
  options to calibrate to, which is worth saying.

### Step 5 — Out-of-sample forecast check (validation)
* Rolling origin, monthly: at each month use only earlier data to estimate
  the drift, forecast 1 and 3 months ahead as `S_t · exp(Σ drift · dt)`.
* MAE/RMSE vs baselines: (a) last price, (b) last price × last year's
  same-month change. The seasonal drift must beat (a) to be worth using.
* *Optional:* score the weekly agriBORA Uasin-Gishu holdout weeks (the
  Zindi target) with the monthly drift interpolated to weeks.

### Step 6 — Value the storage option (Lecture 9)
```python
value, sell_prices = qk.binomial_optimal_stopping(
    S0=price_in_december,
    sigma=sigma,
    t=9 / 12,                        # Dec -> Aug
    n_steps=9 * k,                   # k steps per month, e.g. k = 8
    payoff=lambda S: S,              # selling earns the price
    r=0.15,                          # loan rate (§3)
    drift=np.repeat(monthly_drift_from_dec, k),
    holding_cost=0.03 + loss_rate,   # fee + losses (§3)
    return_exercise=True,
)
option_value = value - price_in_december
```
* Run for **warehouse** (loss 0%) and **on-farm** (loss 20%), calibrations A
  and B. Report option value in KSh/kg and KSh per 90-kg bag.
* **Sell rule:** `min(sell_prices[i])` against month = the boundary "sell once
  the price is at least this". Plot it over the average seasonal path.
* Before changing the payoff, show the tree reproduces `qk.american_put`
  (the Lecture 9 check), then switch to "sell the grain".
* The one-off first-month fee is a fixed cost: subtract it from the store
  value rather than folding it into `holding_cost`.
* **Sanity checks (from the tests):** drift ≤ r + cost every month → value =
  S0; value converges as k grows (k = 2, 4, 8, 16).

### Step 7 — Check the tree with Monte Carlo (Lecture 2)
* Simulate with the same drift and σ, apply the Step 6 rule along each path,
  discount net revenue, `qk.mc_estimate` → mean ± SE. Should match the tree
  within ~2 SE (slightly lower: the rule is checked monthly).

### Step 8 — Historical backtest (main validation, Lecture 8)
* For every season (Dec 2006 → Aug 2025, ≈ 18 seasons), on the actual price
  path, net of fees, interest and losses:
  1. sell at harvest (Dec);
  2. sell in a fixed month (the historically best, e.g. June);
  3. the tree rule **re-estimated each season using only earlier seasons**
     (expanding window, no look-ahead).
* Report mean, spread and worst season per strategy, warehouse vs on-farm.
  Bootstrap the per-season difference (3 − 1) for a confidence interval and
  say plainly if it includes zero. Months with no price: the rule cannot
  sell then; carry to the next observed month and say so.

### Step 9 — Sensitivities, the "Greeks" of storage (Lecture 6; F26 L10)
* Bump-and-reprice the option value in σ, `r`, `holding_cost`, drift
  amplitude, start month and horizon, over the §3 ranges.
* **Break-even:** the loss rate (or loan rate) at which storage stops paying —
  a concrete number for agriBORA. Plot the sell boundary for a few costs.
* *Efficient pricing (F26 L10):* a sensitivity grid is thousands of trees.
  L10's trick — put every contract in one 2-D array and run a single
  backward-induction loop (`qk.american_vectorized`) — applies directly:
  write a vectorized `binomial_optimal_stopping` over parameter rows, test it
  against the scalar version, and time both. This is a clean "quant
  development" contribution.

### Step 10 — Optional extensions
* **Model risk:** apply the GBM-calibrated sell rule to paths from the
  regime-switching or Heston model (Step 4). How much value is lost when
  volatility is misspecified?
* **Risk aversion:** a farmer who dislikes the 2010/2018-type years would
  store less; show the rule under a concave utility.
* **Policy shocks:** mark NCPB purchase announcements and duty-free import
  windows on the backtest; the brief names unpredictable state intervention
  as the largest risk to warehouse economics [S1 p.8].

---

## 5. Course map

| Step | Lecture | `quantkit` | New code |
|---|---|---|---|
| 1 Data | 3a | — | CPI choice, plots |
| 2 Returns/vol | 3a | `log_returns`, `annualized_vol`, `rolling_vol` | — |
| 3 Tests | 8 | `test_normality`, `ljung_box` | Seasonality tests (done) |
| 4 Model | 4, 11b, F26 L12 | `gbm_paths`, `markov_vol_states`, `heston_paths` | Harmonic drift fit (`least_squares`), coverage check |
| 5 Forecast | 2 | — | Rolling-origin backtest |
| 6 Option | 9 | `binomial_optimal_stopping`, `american_put` | Boundary plot, warehouse vs on-farm |
| 7 MC check | 2 | `gbm_paths`, `mc_estimate` | Rule along paths |
| 8 Backtest | 8 | — | Strategy simulator, bootstrap |
| 9 Sensitivities | 6, F26 L10 | `american_vectorized` (pattern) | Bump-and-reprice; vectorized tree |
| 10 Extensions | 11b, F26 L12 | `markov_vol_states`, `heston_paths` | As chosen |

Not used (no traded maize options to calibrate to): Black–Scholes Greeks,
`bs_implied_vol` (F26 L11), `implied_vol_bisect`, `heston_call`/
`heston_calibrate`, `make_american_pricer`. Worth one sentence in the
write-up: these need option prices, which do not exist for Kenyan maize.

---

## 6. How this meets the Fall 2026 requirements

| Requirement (project instructions) | Where |
|---|---|
| Centered on Jupyter notebook(s) | One notebook, repo root |
| Clearly stated financial question | §1 |
| Appropriate method | Seasonal-drift American option tree (Steps 4, 6) |
| Real data | 19 years of Eldoret wholesale prices + cited cost inputs (§2–3) |
| Validation / benchmarking / testing | Forecast vs baselines (5), tree vs MC (7), out-of-sample backtest vs simple rules (8), 38 unit tests |
| Financial interpretation | Option value per bag, sell rule, break-even loss/loan rate (6, 9) |
| Assumptions, limitations, failure modes | §7 |
| Suggested direction it fits | Pricing ("what is it worth, how does it change") + Model Validation ("where does it fail"); "extending a model studied in class by relaxing one of its assumptions" (no hedging → real-world drift) |

**Deliverables:** annotated GitHub repo (notebook, code, data instructions,
README to reproduce); executive summary (problem, method, findings,
limitations); short video (question, methods, results, limitations, what you
learned). AI use is allowed, but you must be able to explain every method and
result.

---

## 7. Limitations to state up front

* **One market:** Eldoret wholesale, not farm-gate, not agriBORA's B2B price.
* **Monthly data:** the rule is checked monthly; within-month moves are ignored.
* **Spliced series:** three WFP series + KAMIS fills; 9 missing months; the
  2020 → 2021 "white" → "white, dry" link cannot be checked.
* **Costs are 2020–2026 point estimates** applied to 2006–2025 prices, and
  fixed per-bag fees are approximated as proportional.
* **Lognormal moves and constant σ** are tested (Step 3), not assumed.
* **No hedge:** the value is a decision value for a risk-neutral farmer, not
  a market price.
* **Policy shocks** (NCPB purchases, import-duty waivers) can dominate a
  season and are not modelled.

---

## Sources

* [S1] Kenduiywo, B. et al. (2026). *Enabling Private-Sector Innovation in Agricultural Storage: Lessons from the agriGHALA Warehouse Receipt Model in Kenya.* Policy brief, CIAT / agriBORA / P4G, May 2026. <https://hdl.handle.net/10568/182900>
* [S2] People Daily, "Warehouse receipt system opens stores to maize farmers." <https://peopledaily.digital/business/warehouse-receipt-system-opens-stores-to-maize-farmers> (fee schedule ≈ 2020; check WRS Council for current tariff)
* [S3] Standard, "Warehouses idle as Rift farmers opt to store their produce at home." <https://www.standardmedia.co.ke/counties/article/2001467107/warehouses-idle-as-rift-farmers-opt-to-store-their-produce-at-home> (private warehouse and NCPB rates)
* [S4] De Groote, H., Muteti, F. N., Bruce, A. Y. (2023). On-farm storage loss estimates of maize in Kenya using community survey methods. *J. Stored Products Research* 102, 102107. <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10285508/>
* [S5] Nation, WRI Africa food-loss report. <https://nation.africa/kenya/news/report-reveals-shocking-scale-of-food-loss-as-one-in-four-kenyans-struggle-to-put-food-on-the-table-5188220>
* [S6] The New Humanitarian / ReliefWeb, harvest timing by county (Trans Nzoia and Uasin Gishu Oct–Nov). <https://reliefweb.int/report/kenya/food-crisis-looms-following-low-rainfall-maize-region>; FAO GIEWS Kenya brief <https://cb.apps.fao.org/country.jsp?code=KEN>
* [S7] CBK average lending rates via press: <https://hapakenya.com/2025/07/02/kenyas-average-commercial-bank-lending-rate-dropped-to-15-44-in-may-2025>; Business Daily <https://www.businessdailyafrica.com/bd/economy/banks-lend-sh228bn-new-loans-to-businesses-households-5368368>
* [S8] The EastAfrican, "Kenya agricultural commodities exchange to go live in 2024." <https://www.theeastafrican.co.ke/tea/business/kenya-agricultural-commodities-exchange-to-go-live-in-2024-4433186>
* [S9] Capital Markets Authority, derivatives brochure. <https://cma.or.ke/download/15/brochures/5491/derivatives-brochure.pdf>
* [S10] Business Daily, Komex launch postponed. <https://www.businessdailyafrica.com/bd/economy/kenya-agricultural-commodities-exchange-goes-live-next-february--4432574>
* [S11] Business Daily, AFC MD interview (≈ 10% lending rate; date not shown). <https://www.businessdailyafrica.com/bd/corporate/boss-talk/afc-managing-director-george-kubai-on-unlocking-access-to-credit-for-kenyan-smallholder-farmer-5162832>
