# Project worksheet: the value of storing maize in Uasin-Gishu

*Final version, 2026-11-06. Describes what `maize_storage_option.ipynb` does, why, and with
which inputs. Results quoted here come from the notebook.*

**Files** (relative to the repo root `erdos_project/`)

| File | What it is |
|---|---|
| `maize_storage_option.ipynb` | **The project notebook** (Steps 1–9 + conclusions) |
| `docs/executive_summary.md` | Executive summary |
| `quantkit.py`, `test_quantkit.py` | Cleaned, tested course functions; 38 tests (`python -m unittest -v test_quantkit`) |
| `data/processed/wfp_monthly_wholesale.csv` | The price series: Eldoret monthly wholesale, KSh/kg, 2006-01 → 2025-06 |
| `data/make_data.py`, `data/README.md` | How the series was built; sources and licenses |
| `figures/` | `seasonality.py`, `make_figures.py`, `storage_tree.py` and their figures |

---

## 1. The question

agriBORA runs a certified warehouse in **Eldoret** (agriGHALA, opened Dec 2024). A Uasin-Gishu
farmer who deposits maize there can sell in any month and can borrow against the warehouse
receipt instead of selling at harvest. Waiting costs money: interest, storage fees, and
(outside a warehouse) losses.

> **Financial question:** for a Uasin-Gishu farmer holding maize after the October–December
> harvest, what is the option to delay the sale worth, when should the grain be sold, and does
> storing beat selling at harvest on real Eldoret prices after realistic costs — in a
> certified warehouse and on the farm?

### From first principles: cost of carry

Storing grain is worth it exactly when the expected price rise exceeds the cost of carrying the
grain (the classic theory of storage):

$$ \text{store from December to month } m \iff
\mathbb{E}\!\left[\frac{P_m}{P_{\text{Dec}}}\right] e^{-(r + \text{fee} + \text{loss})\,t_m} > 1 . $$

Everything in the notebook estimates or tests one side of this inequality: the left-hand
price rise (Steps 2–5), the right-hand costs (§3), and whether the inequality held on real
seasons (Step 8). The binomial tree (Step 6) solves the same problem as an American-style
option, the course's method for "when should I exercise?".

### The one modelling idea to get right

Risk-neutral pricing assumes the position can be hedged, which replaces the drift by `r` — and
then storing never pays. **Maize in Kenya cannot be hedged:** the only licensed derivatives
exchange, NSE NEXT, lists index and single-stock futures, not maize [S9]; KOMEX provides spot
price benchmarks and plans futures "at a later stage" [S8, S10]. So the decision uses the
**real-world** seasonal drift, with `r` = the farmer's loan rate for discounting and
`holding_cost` = fees + losses. `qk.binomial_optimal_stopping` takes these separately for
this reason.

---

## 2. Data

Eldoret town monthly wholesale price, nominal KSh/kg, 2006-01 → 2025-06: 225 of 234 months
present. Built from three WFP series plus five months of KAMIS Eldoret Main, which matches WFP
where both exist (median ratio 1.00 — WFP republishes KAMIS). Details in `data/README.md`.

* **Nominal prices throughout:** the loan rate is nominal, so a nominal drift is consistent with
  it and no CPI series is needed.
* **One calibration, 2006–2025**, including the 2022–23 drought spike; the backtest reports
  results per season so its influence is visible.
* agriBORA's own B2B prices run ≈ 10–25% below wholesale; the analysis is in relative terms
  (% of the December price), so it carries over, but levels in KSh are wholesale.

---

## 3. Inputs from outside the price data

| Input | Base case | Range (Step 9) | Source / reasoning |
|---|---|---|---|
| **Start month** | **December** | — | Uasin-Gishu harvest Oct–Nov [S6]; agriGHALA brief: harvest Oct–Dec, lean season May–Aug [S1 p.4]; Eldoret price low is Dec–Jan (Step 2) |
| **Horizon** | sell at the end of any month Jan → Nov | — | next harvest from October |
| **Storage fee** | **3%/yr** + 1.5% one-off | — | WRS: KSh 48/90-kg bag first month, KSh 9/month after [S2]; private warehouse KSh 70 then 10 [S3]. At 40 KSh/kg (3,600/bag) KSh 9/month ≈ 3%/yr |
| **Losses, certified warehouse** | **0%** | — | agriGHALA deposits insured; grain accepted at ≤ 13.5% moisture, fumigated [S1 p.5] |
| **Losses, on-farm** | **20%/yr** | 0 – 60%/yr | Kenya on-farm storage loss ≈ 36%/yr (survey; authors note it is high) [S4]; 20–36% [S5]; agriGHALA Q1 2026 implies ≈ 15% avoided [S1 p.10] |
| **Loan rate `r`** | **15%/yr** | 5 – 45%/yr | CBK average lending rate 15.4% (May 2025), 14.8% (Dec 2025) [S7]; AFC ≈ 10% [S11]; receipt loans up to 70% of grain value [S1 p.5] |
| **Sanity check** | — | — | agriGHALA 2022 example: KSh 3,500/bag in April → 6,000–6,500 in July, ≈ KSh 1,100/bag costs, net ≈ +40% [S1 p.4] — a spike year, consistent with Step 8's 2022 season |

---

## 4. Notebook steps and results

| Step | What it does (`quantkit` functions) | Result |
|---|---|---|
| **1 Data** | Load the series, plot it, define monthly log returns (none across gaps) | 225/234 months, 220 returns |
| **2 Seasonal cycle** | Each season vs its harvest level (actual price and %); Kruskal–Wallis, random-phase permutation test, sign test; monthly averages (`mc_estimate`) | Up from harvest to May–Jul in **15 of 17** seasons (p = 0.001); cycle p = 0.0002 |
| **3 Seasonal drift** (`least_squares`) | One annual wave fitted by least squares; number of waves by leave-one-year-out cross-validation | Expected rise **≈ +34% Dec → Jun**; one wave beats 12 raw monthly means out of sample |
| **4 Volatility / GBM checks** | σ from de-seasonalized returns; normality and Ljung–Box tests; past-year volatility; drift for the tree μ = 12g + σ²/2; simulation coverage check (`gbm_paths`) | σ ≈ 0.40; fat tails, year-to-year mean reversion (lag-12 ≈ −0.2), volatility clustering; 89–90% coverage |
| **5 Forecast check** | Rolling-origin 1- and 3-month forecasts vs random walk, raw monthly means, last year's change | 3-month error 15.1% vs 18.6% (random walk); bootstrap CI excludes 0 |
| **6 Storage value** (`binomial_optimal_stopping`, `american_put`) | Tree checked against the American put, then payoff = price, real-world drift, costs | Warehouse **+27%**, on-farm (20% loss) **+18%** of the Dec price; sell end of **June** |
| **7 Monte Carlo** (`gbm_paths`, `mc_estimate`) | Simulate, sell in June, compare with the tree | Within 1 SE |
| **8 Backtest** | 17 real seasons, model re-estimated each season with earlier data only; plus an out-of-sample price-threshold rule | Warehouse **+28%** (95% CI 7–52%), won 13/17; on-farm +15% (CI −2 to 33%); threshold rule never sold early |
| **9 Sensitivities** | Bump-and-reprice in loss rate and loan rate; break-evens (model and history) | Break-even loan rate ≈ 53–68%; on-farm loss rate ≈ 45–60%/yr |

**Key finding about the method.** With the price as payoff, costs proportional to the price, and
GBM, the tree value equals the best fixed sale month exactly: the "option" is a calendar
decision (sell in June), not a price-dependent rule. This is the cost-of-carry inequality above
evaluated month by month. The out-of-sample threshold test in Step 8 found no evidence that a
price-dependent rule would do better.

---

## 5. Not done (possible extensions)

* **Mean-reverting price model** (log price = seasonal level + AR(1)/OU deviation, Schwartz 1997),
  which would allow a genuinely price-dependent sell rule; the evidence for mean reversion
  within a season was only suggestive, and Step 8's threshold test did not favour it.
* **Stochastic or regime-switching volatility** (`qk.heston_paths`, `qk.markov_vol_states`) for
  model risk. Under GBM σ does not change the optimal rule, so the value would change only
  through the drift conversion.
* **Fixed per-bag fees** (instead of proportional), **risk aversion**, and **policy shocks**
  (import-duty waivers, NCPB purchases).

## 6. How this meets the Fall 2026 requirements

| Requirement | Where |
|---|---|
| Jupyter notebook | `maize_storage_option.ipynb` |
| Clearly stated financial question | §1; notebook introduction |
| Appropriate method | Cost of carry + American-style optimal stopping on a CRR tree with real-world seasonal drift (Steps 3, 4, 6) |
| Real data | 19 years of Eldoret prices + cited cost inputs |
| Validation | Seasonality tests (2), cross-validation (3), coverage check (4), out-of-sample forecasts (5), Monte Carlo (7), no-look-ahead backtest (8), 38 unit tests |
| Financial interpretation | Gain per bag, sell month, break-even loan and loss rates (6, 8, 9) |
| Assumptions, limitations, failure modes | Notebook conclusions; executive summary |

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
