# The value of waiting to sell: maize storage as an American option

Course project for the Erdős Institute *Quantitative Methods in Finance*
(Fall 2026). **Status: in progress** — the toolkit and plan are in place;
the analysis notebook is not written yet.

**Question.** A Kenyan farmer storing maize in a certified warehouse can sell
in any week instead of at harvest, at the cost of storage fees, spoilage and
interest. What is that option to delay worth, what week-by-week sell rule
captures it, and does the rule beat selling at harvest on historical prices?

**Approach.** Estimate a seasonal price drift and volatility from weekly maize
prices, test the GBM assumptions on the data, value the storage decision with a
binomial optimal-stopping tree (an American option whose payoff is the sale
price), check the tree with Monte Carlo, and backtest the resulting sell rule
on real price history. See [`docs/agribora_worksheet.md`](docs/agribora_worksheet.md).

## Repository

| Path | Contents |
|---|---|
| `quantkit.py` | Option pricing, simulation and statistics functions used in the project |
| `test_quantkit.py` | 28 unit tests for `quantkit.py` |
| `docs/agribora_worksheet.md` | Step-by-step project plan |

## Running the tests

Requires Python 3.10+, NumPy, SciPy and pandas.

```bash
python -m unittest -v test_quantkit
```

## Data

Prices come from the Zindi
[agriBORA Commodity Price Forecasting Challenge](https://zindi.world/competitions/agribora-commodity-price-forecasting-challenge)
(weekly agriBORA white-maize prices, Oct 2023 – Oct 2025, and KAMIS market
prices, 2021 – Jul 2025). Download them from the competition's Data tab (Zindi
login required) into `data/raw/`. Data files are not committed to this
repository.

## Acknowledgements

The functions in `quantkit.py` are cleaned-up, tested versions of code from the
Erdős Institute *Quantitative Methods in Finance* course notebooks.
