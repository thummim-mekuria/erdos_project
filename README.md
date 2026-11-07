# The value of waiting to sell: maize storage in Uasin-Gishu, Kenya

Course project for the Erdős Institute *Quantitative Methods in Finance* (Fall 2026).

*Inspired by the Zindi [agriBORA Commodity Price Forecasting Challenge](https://zindi.africa/competitions/agribora-commodity-price-forecasting-challenge)
(forecasting Kenyan maize prices). This project starts from that setting (the challenge's KAMIS
prices fill gaps in the longer WFP series used here) but asks the decision question behind a
forecast: is it worth storing grain to sell later, and when?*

**Question.** A Uasin-Gishu (Eldoret) farmer holding maize after the October–December harvest can
sell now or store the grain — in a certified warehouse such as agriBORA's agriGHALA, or on the
farm — and sell later. Storing costs interest, fees and (on-farm) losses. What is the option to
wait worth, when should the farmer sell, and does storing beat selling at harvest on real prices?

**Answer (short).** Eldoret prices rise from the December–January harvest to a May–July peak in
15 of 17 seasons (≈ +34% to June on average). Valued as an American-style optimal-stopping problem
with the real-world seasonal drift (maize cannot be hedged in Kenya), storing until **June** is
worth ≈ **+27%** of the December price in a certified warehouse (15% loan rate, fees) and ≈ +18%
on-farm (20%/yr losses). On 17 real seasons with no look-ahead, warehouse storage gained +28% on
average (95% CI 7–52%) and won 13 of 17 seasons, but lost 28–57% in the two worst seasons. Under
GBM with proportional costs the optimal rule depends only on the calendar; a price-threshold rule
tested out of sample never improved on it. Full summary: [`docs/executive_summary.md`](docs/executive_summary.md).

## Repository

| Path | Contents |
|---|---|
| **`maize_storage_option.ipynb`** | **The project notebook** (Steps 1–9: data, seasonality tests, seasonal drift, volatility and GBM checks, forecast validation, storage value, Monte Carlo check, backtest, sensitivities) |
| `docs/executive_summary.md` | Executive summary |
| `docs/agribora_worksheet.md` | Project plan, cost inputs with sources, course mapping |
| `quantkit.py`, `test_quantkit.py` | Course functions (Black–Scholes, trees, optimal stopping, simulation, Heston, statistics), 38 unit tests |
| `data/make_data.py` | Builds the cleaned price series from the raw downloads |
| `data/processed/wfp_monthly_wholesale.csv` | Cleaned monthly Eldoret wholesale price, 2006-01 → 2025-06 |
| `data/processed/model_params.json` | Fitted model parameters (written by the notebook) |
| `data/nairobi_uasingishu/` | Two-county extracts of the raw sources |
| `data/README.md` | Data sources, licenses, every cleaning and splicing decision |
| `figures/` | `make_figures.py`, `seasonality.py` and the figures they produce |

## Reproducing the analysis

Requires Python 3.10+ with NumPy, SciPy, pandas, matplotlib and Jupyter.

```bash
python -m unittest -v test_quantkit        # 38 tests
python figures/seasonality.py              # seasonality tests + figure
python figures/make_figures.py             # price-history figure
jupyter nbconvert --to notebook --execute maize_storage_option.ipynb   # or run it in Jupyter / VS Code
```

The cleaned data needed by the notebook is committed. To rebuild it from scratch, download the raw
files (below) into `data/raw/` and `data/external/`, then run `python data/make_data.py`.

## Data

* **WFP Kenya food prices** (Humanitarian Data Exchange, CC BY-IGO), Eldoret town monthly
  wholesale maize, 2006–2025: <https://data.humdata.org/dataset/wfp-food-prices-for-kenya>
* **KAMIS market prices and agriBORA prices** from the Zindi
  [agriBORA Commodity Price Forecasting Challenge](https://zindi.africa/competitions/agribora-commodity-price-forecasting-challenge)
  (rules: data is open source); KAMIS Eldoret Main Market fills five WFP gaps.
* Cost inputs (warehouse fees, loss rates, loan rates, harvest calendar) and their sources are
  listed in `docs/agribora_worksheet.md` §3.
* **Full citations for all data and sources: [`docs/references.md`](docs/references.md).**

## Acknowledgements

`quantkit.py` contains cleaned-up, tested versions of methods from the Erdős Institute
*Quantitative Methods in Finance* course notebooks. AI tools (Claude) were used for coding,
data work and drafting; all results were checked against the notebook outputs.
