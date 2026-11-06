# Data

## `raw/` — agriBORA Commodity Price Forecasting Challenge (Zindi)

Source: <https://zindi.africa/competitions/agribora-commodity-price-forecasting-challenge>
(downloaded 2026-11-06; zip dated 2026-01-14). Files are unmodified.

| File | Contents |
|---|---|
| `agriBORA_maize_prices.csv` | agriBORA weekly B2B wholesale price of dry white maize by county, 2023-10 → 2025-10 (239 rows) |
| `agriBORA_maize_prices_weeks_46_to_51.csv` | Same, weeks 46–51 of 2025 for the 5 target counties |
| `agriBORA_Final_Weeks_maize_price.csv` | Held-out truth: 2025 week 52 and 2026 week 1 (private leaderboard) |
| `kamis_maize_prices.csv` | KAMIS market-level maize prices (wholesale, retail, supply volume), cleaned by the organisers, 2021-05 → 2025-07 |
| `kamis_maize_prices_raw.csv` | Same KAMIS data before cleaning |
| `SampleSubmission.csv` | Submission format (county × week, RMSE and MAE targets) |

Prices are KSh per kg. Target counties: Kiambu, Kirinyaga, Mombasa, Nairobi, Uasin-Gishu.

Known issues: `kamis_maize_prices.csv` has 829 exact duplicate rows, some zero
prices, and outliers up to 3500 (likely per-bag rather than per-kg entries).

### License and attribution

The challenge rules state: *"Data Sharing: Open source"* and *"You are allowed
to access and, use and share challenge data for the competition. for any
commercial, non-commercial, research or education purposes, by open source."*

Data provided by **agriBORA** via **Zindi** (challenge partner: Digital Africa).
KAMIS series originate from the **Kenya Agricultural Market Information System**,
Ministry of Agriculture, Livestock, Fisheries and Cooperatives (<https://kamis.kilimo.go.ke>).

The challenge's `StarterNotebook.ipynb` is not included; download it from Zindi.
