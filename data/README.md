# Data

All prices are wholesale dry maize in **KSh per kg** (per-90-kg bag prices divided by 90).
Target counties are the 5 scored in the Zindi challenge: Kiambu, Kirinyaga, Mombasa, Nairobi and Uasin-Gishu.

## Source comparison

| | **agriBORA** | **KAMIS (Zindi extract)** | **WFP / HDX** | **KNBS (KAMIS monthly)** |
|---|---|---|---|---|
| File(s) | `raw/agriBORA_*.csv` | `raw/kamis_maize_prices.csv` (+ `_raw`) | `external/wfp_food_prices_ken.csv`, `wfp_markets_ken.csv` | `external/knbs_kamis_monthly_wholesale_2012_2023.xlsx` (**local only, not in git**) |
| What it measures | B2B transaction prices on agriBORA's platform (**the forecast target**) | Government market-survey prices | WFP market monitoring; Kenyan series largely from the Ministry / KAMIS | KAMIS market prices, averaged by month |
| Range | 2023-10-02 → 2025-12-29 | 2021-05-24 → 2025-07-31 | **2006-01 → 2026-09** | 2012-01 → 2023-12 |
| Frequency | Weekly | Market-day observations, used as weekly | Monthly (dated the 15th) | Monthly |
| Granularity | County | Market (216 markets, 46 counties) | Market (24 markets, 14 counties) | Market (273 markets, 47 counties) |
| Rows (white/dry maize, wholesale) | 279 | 13,410 after removing duplicates | 2,018 | 4,846 |
| Other fields | none | Retail, supply volume; yellow and mixed maize | Retail, USD price, flour; latitude/longitude | ~170 other commodities; county and national averages |
| Original unit | KSh/kg | KSh/kg | KSh/kg or per 90 kg bag | Mostly per 90 kg bag (`kg` column) |
| Median price (KSh/kg) | 41.1 | 50.0 | 30.9 (since 2006) | 35.1 (since 2012) |
| Updates | Closed (challenge over) | Static extract | Monthly (last 2026-11-04) | Static (2012–2023) |
| License | Zindi rules: "Open source", may share for research/education | Same | CC BY-IGO | Not stated |
| Known issues | Very patchy; 16 counties but most have <5 weeks | 829 duplicate rows; zeros; outliers up to 3500 (likely per bag); Kiambu and Mombasa end in 2023-08 | No Kiambu or Kirinyaga; Uasin-Gishu is only Eldoret town | Sparse before 2021 (~180 rows/yr nationally vs ~1,000 after); messy market names (`nairobikangemi` vs `nairobi kangemi`) |

### Coverage of the target counties

Each cell shows: date range · share of periods (weeks or months) inside that range with at least one price · longest jump between consecutive observations.

| County | agriBORA (weekly) | KAMIS Zindi (weekly) | WFP (monthly) | KNBS (monthly) |
|---|---|---|---|---|
| Kiambu | 2023-10 → 2025-12 · **32%** · 25 wk | 2021-05 → 2023-08 · 27% · 23 wk | none | 2012-01 → 2023-07 · 19% · 75 mo |
| Kirinyaga | 2023-10 → 2025-12 · **28%** · 53 wk | 2021-05 → 2025-07 · 85% · 31 wk | none | 2020-12 → 2023-12 · 81% · 6 mo |
| Mombasa | 2024-02 → 2025-12 · **25%** · 36 wk | 2021-05 → 2023-08 · 28% · 33 wk | 2006-01 → 2023-07 · 89% · 10 mo | 2012-01 → 2023-07 · 77% · 12 mo |
| Nairobi | 2023-10 → 2025-12 · **54%** · 24 wk | 2021-05 → 2025-07 · 81% · 27 wk | 2006-01 → **2026-09** · 92% · 5 mo | 2012-01 → 2023-12 · 86% · 6 mo |
| Uasin-Gishu | 2023-10 → 2025-12 · **69%** · 8 wk | 2021-05 → 2025-06 · 72% · 34 wk | 2006-01 → **2026-09** · 90% · 14 mo | 2012-01 → 2023-11 · 83% · 10 mo |

### Agreement with agriBORA

Monthly means compared over months where both sources have data; ratio is the median of source ÷ agriBORA.

| County | KAMIS Zindi | WFP |
|---|---|---|
| Kirinyaga | corr 0.95, ratio 1.04 (10 months) | — |
| Nairobi | corr 0.76, ratio 1.29 (15 months) | corr 0.74, ratio 1.12 (11 months) |
| Uasin-Gishu | corr 0.87, ratio 1.30 (12 months) | corr 0.82, ratio 1.29 (12 months) |

KNBS overlaps agriBORA only in Oct–Dec 2023, too few months to compare. These comparisons rest on only 10–15 months each, so treat them as rough.

## Provenance and attribution

- **`raw/`**: agriBORA Commodity Price Forecasting Challenge, <https://zindi.africa/competitions/agribora-commodity-price-forecasting-challenge>
  (downloaded 2026-11-06; zip dated 2026-01-14; files unmodified). The challenge rules say: *"Data Sharing: Open source"* and
  *"You are allowed to access and, use and share challenge data for the competition. for any commercial, non-commercial,
  research or education purposes, by open source."* Data provided by **agriBORA** via **Zindi** (partner: Digital Africa).
  The KAMIS series come from the **Kenya Agricultural Market Information System**, Ministry of Agriculture (<https://kamis.kilimo.go.ke>).
  The challenge's `StarterNotebook.ipynb` is not included; download it from Zindi.
  - `agriBORA_maize_prices.csv`: 2023-10 → 2025-10 · `agriBORA_maize_prices_weeks_46_to_51.csv`: weeks 46–51 of 2025 ·
    `agriBORA_Final_Weeks_maize_price.csv`: held-out answers for 2025 week 52 and 2026 week 1 · `SampleSubmission.csv`: submission format.
- **`external/wfp_*.csv`**: WFP, "Kenya – Food Prices", Humanitarian Data Exchange,
  <https://data.humdata.org/dataset/wfp-food-prices-for-kenya> (downloaded 2026-11-06; CC BY-IGO).
  The second row of the prices file is an HXL tag row; skip it with `pd.read_csv(..., skiprows=[1])`.
- **`external/knbs_kamis_monthly_wholesale_2012_2023.xlsx`** (excluded by `.gitignore`): KNBS National Information Platform for Food
  Security and Nutrition, "National average monthly wholesale prices 2012–2023 (source: KAMIS, Ministry of Agriculture)",
  <https://nipfn.knbs.or.ke/download/national-average-monthly-wholesales-prices-2012-2023-source-kamis-ministry-of-agriculture/>.
  It is not committed because no license is stated; download it from that link. Sheets: `Data` (long format), `Markets Avg`, `County Avg`, `National Avg`.
- **KAMIS portal** (<https://kamis.kilimo.go.ke>): the primary source, with daily market prices. It timed out from the US on 2026-11-06; try it from a browser or VPN.
