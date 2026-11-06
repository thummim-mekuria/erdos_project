# Data

The project focuses on two counties: **Nairobi** (consumer market) and
**Uasin-Gishu** (grain-producing region, Eldoret). This repo contains only
those counties' data. Prices are wholesale dry maize in **KSh per kg** (prices
per 90-kg bag are divided by 90).

## What is in the repo

| File | Contents |
|---|---|
| `processed/wfp_monthly_wholesale.csv` | **Cleaned monthly series for calibration.** Nairobi 2006-01 → 2021-11 (188/191 months; missing 2020-05, 2020-06, 2020-12). Uasin-Gishu 2006-01 → 2025-06 (225/234; missing 2020-04/05, 2023-12, 2024-01, 2024-10 → 2025-01, 2025-03). The `source` column says which WFP series each month came from. |
| `nairobi_uasingishu/agribora_weekly.csv` | agriBORA weekly prices for both counties, 2023-10 → 2026-01, from all three challenge files (the `file` column; `final_weeks_heldout` = the challenge's held-out answers) |
| `nairobi_uasingishu/kamis.csv` | KAMIS market-level rows (Zindi extract) for both counties, 2021-05 → 2025-07, unmodified (it still contains duplicates and outliers) |
| `nairobi_uasingishu/wfp.csv` | WFP maize-grain rows (wholesale and retail) for both counties, 2006 → 2026-09, unmodified; Kitengela removed (it is in Kajiado county) |
| `make_data.py` | Rebuilds all of the above from the full downloads: `python data/make_data.py` |

The full downloads (`raw/`, `external/`) are not committed. To rebuild,
download them to those folders from the sources below.

## How the monthly series was built

* **Nairobi:** WFP market "Nairobi", per-kg series; 2018-04 filled from the
  per-90-kg "Maize (white)" series (the two agree: median ratio 1.02).
  Ends at **2021-11**: the series then skips two months, and its last
  two points (2022-02 = 40.0, 2022-03 = 25.0 KSh/kg) disagree with every
  other Nairobi market (≈ 33–36 KSh/kg), so they are dropped.
* **Uasin-Gishu:** WFP market "Eldoret town". Per-kg series to 2020-12, with
  2008-01..03 and 2009-10..11 filled from the per-90-kg "Maize (white)"
  series (median ratio 1.02 over 2006–2020). For 2021 the per-kg series runs
  ≈ 26% below both WFP's "Maize (white, dry)" bag series and KAMIS's Eldoret
  Main Market, so **from 2021** the white-dry bag series is used, with gaps
  filled from KAMIS Eldoret Main Market (monthly median), which matches WFP
  Eldoret exactly where both exist (median ratio 1.00, IQR 0.99–1.01, 36
  months: WFP republishes KAMIS). Ends 2025-06: neither source has Eldoret
  prices for 2025-07..12. Assumption: the
  "white" (ends 2020-03) and "white, dry" (starts 2021-01) bag series are the
  same series, renamed; they do not overlap, so this cannot be checked.
* Missing months are left as NaN; interpolating them is a modelling choice.
* Nairobi stops before the 2022–23 drought price spike; Uasin-Gishu includes
  it (peaks 90.3 KSh/kg Jul 2022, 90.4 Jun 2023, both confirmed by KAMIS).

## Figures

`figures/make_figures.py` (price histories) and `figures/seasonality.py`
(seasonal-cycle tests + figure) regenerate everything in `figures/`.

## Sources reviewed (full datasets, 2026-11-06)

| | **agriBORA** | **KAMIS (Zindi extract)** | **WFP / HDX** | **KNBS (KAMIS monthly)** |
|---|---|---|---|---|
| What it measures | B2B transaction prices on agriBORA's platform (the Zindi forecast target) | Government market-survey prices | WFP market monitoring | KAMIS market prices, monthly averages |
| Range | 2023-10 → 2025-12 | 2021-05 → 2025-07 | **2006-01 → 2026-09** | 2012-01 → 2023-12 |
| Frequency | Weekly | Market-day, used as weekly | Monthly | Monthly |
| Granularity | County (16) | 216 markets, 46 counties | 24 markets, 14 counties | 273 markets, 47 counties |
| License | Zindi rules: "Open source" | Same | CC BY-IGO | Not stated |
| Known issues | Very patchy | 829 duplicate rows; zeros; outliers up to 3500 | No Kiambu/Kirinyaga; market mix changes in 2021–22 | Sparse before 2021; messy market names |

Coverage of the two counties (share of periods with a price · longest gap):

| County | agriBORA (weekly) | KAMIS Zindi (weekly) | WFP (monthly) | KNBS (monthly) |
|---|---|---|---|---|
| Nairobi | 54% · 24 wk | 81% · 27 wk | 92% · 5 mo | 86% · 6 mo |
| Uasin-Gishu | 69% · 8 wk | 72% · 34 wk | 90% · 14 mo | 83% · 10 mo |

Level vs agriBORA (median ratio, shared months): KAMIS ≈ 1.29–1.30×, WFP ≈ 1.12–1.29×.
WFP and KNBS agree closely for Nairobi (ratio 1.003, 122 months), so KNBS is
not needed once WFP is used.

## Provenance and attribution

* **agriBORA / KAMIS (Zindi):** agriBORA Commodity Price Forecasting Challenge,
  <https://zindi.africa/competitions/agribora-commodity-price-forecasting-challenge>
  (downloaded 2026-11-06). Rules: *"Data Sharing: Open source"* and *"You are
  allowed to access and, use and share challenge data for the competition. for
  any commercial, non-commercial, research or education purposes, by open
  source."* Data provided by **agriBORA** via **Zindi** (partner: Digital Africa).
  KAMIS series originate from the **Kenya Agricultural Market Information System**,
  Ministry of Agriculture (<https://kamis.kilimo.go.ke>).
* **WFP:** "Kenya – Food Prices", Humanitarian Data Exchange,
  <https://data.humdata.org/dataset/wfp-food-prices-for-kenya> (downloaded
  2026-11-06; CC BY-IGO). The second row of the full file is an HXL tag row
  (`pd.read_csv(..., skiprows=[1])`).
* **KNBS:** "National average monthly wholesale prices 2012–2023 (source:
  KAMIS)", <https://nipfn.knbs.or.ke/download/national-average-monthly-wholesales-prices-2012-2023-source-kamis-ministry-of-agriculture/>.
  No license stated; not redistributed.
