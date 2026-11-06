"""
Build the two-county data files committed to this repo from the full
downloads (which are kept locally and not committed).

Run from the repo root:

    python data/make_data.py

Inputs (download first; see data/README.md):
    data/raw/agriBORA_maize_prices.csv
    data/raw/agriBORA_maize_prices_weeks_46_to_51.csv
    data/raw/agriBORA_Final_Weeks_maize_price.csv
    data/raw/kamis_maize_prices.csv
    data/external/wfp_food_prices_ken.csv

Outputs:
    data/nairobi_uasingishu/agribora_weekly.csv   agriBORA rows, both counties
    data/nairobi_uasingishu/kamis.csv             KAMIS (Zindi extract) rows, both counties
    data/nairobi_uasingishu/wfp.csv               WFP maize-grain rows, both counties
    data/processed/wfp_monthly_wholesale.csv      cleaned monthly series used for the
                                                  storage-option calibration
                                                  (Nairobi 2006-01..2021-11,
                                                  Uasin-Gishu 2006-01..2025-06)
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent
RAW, EXT = DATA / "raw", DATA / "external"
OUT, PROC = DATA / "nairobi_uasingishu", DATA / "processed"
COUNTIES = ["Nairobi", "Uasin-Gishu"]

# Windows chosen in the 2026-11-06 data review (see research notebook):
#  * Nairobi: WFP "Nairobi" market, per-kg series. Unbroken to 2021-11; the
#    only later points (2022-02 = 40.0, 2022-03 = 25.0) disagree with every
#    other Nairobi market and are dropped.
#  * Uasin-Gishu: WFP "Eldoret town". The per-kg "Maize" series runs ~26%
#    below both the WFP white-dry bag series and KAMIS Eldoret Main from 2021,
#    so it is used only to 2020-12 (gaps filled from the white 90 kg series,
#    which agrees with it: median ratio 1.02 over 2006-2020), and the white-dry
#    90 kg series is used from 2021. Its gaps are filled from KAMIS Eldoret
#    Main Market (monthly median), which matches WFP Eldoret where both exist
#    (median ratio 1.00, IQR 0.99-1.01, 36 months): WFP republishes KAMIS.
NAIROBI_END = "2021-11"
UG_PERKG_END, UG_END = "2020-12", "2025-06"   # no WFP or KAMIS Eldoret data for 2025-07..12


def agribora():
    a = pd.read_csv(RAW / "agriBORA_maize_prices.csv").assign(file="agriBORA_maize_prices")
    b = pd.read_csv(RAW / "agriBORA_maize_prices_weeks_46_to_51.csv").assign(file="weeks_46_to_51")
    c = pd.read_csv(RAW / "agriBORA_Final_Weeks_maize_price.csv")
    c = c.assign(County=c.ID.str.split("_Week").str[0],
                 file="final_weeks_heldout").drop(columns="ID")
    df = pd.concat([a, b, c], ignore_index=True)
    df = df[df.County.isin(COUNTIES)]
    return df[["County", "Date", "WholeSale", "Commodity_Classification", "file"]] \
        .sort_values(["County", "Date"])


def kamis():
    df = pd.read_csv(RAW / "kamis_maize_prices.csv")
    return df[df.County.isin(COUNTIES)].sort_values(["County", "Market", "Date"])


def wfp():
    df = pd.read_csv(EXT / "wfp_food_prices_ken.csv", skiprows=[1], low_memory=False)
    keep = (df.admin2.isin(["Nairobi", "Uasin Gishu"])
            & df.commodity.str.startswith("Maize")
            & ~df.commodity.str.contains("flour")
            & ~df.market.str.contains("Kitengela"))   # Kitengela is in Kajiado county
    return df[keep].sort_values(["admin2", "market", "commodity", "date"])


def monthly_series(w, k):
    w = w[w.pricetype == "Wholesale"].copy()
    w["month"] = pd.to_datetime(w.date).dt.to_period("M")
    w["kes_per_kg"] = np.where(w.unit == "90 KG", w.price / 90, w.price)

    def series(market, commodity, unit):
        s = w[(w.market == market) & (w.commodity == commodity) & (w.unit == unit)]
        return s.groupby("month").kes_per_kg.mean()

    rows = []
    # Nairobi
    nb, nb_white = series("Nairobi", "Maize", "KG"), series("Nairobi", "Maize (white)", "90 KG")
    for m in pd.period_range("2006-01", NAIROBI_END, freq="M"):
        if m in nb.index:
            rows.append(("Nairobi", m, nb[m], "WFP Nairobi, Maize per kg"))
        elif m in nb_white.index:   # agrees with per-kg: median ratio 1.02
            rows.append(("Nairobi", m, nb_white[m], "WFP Nairobi, Maize (white) per 90 kg / 90"))
        else:
            rows.append(("Nairobi", m, np.nan, "missing"))
    # Uasin-Gishu (Eldoret town)
    mk = "Eldoret town (Uasin Gishu)"
    kk = k.drop_duplicates()
    kk = kk[(kk.Market == "Eldoret_Main_Market") & (kk.Commodity_Classification == "Dry_White_Maize")
            & kk.Wholesale.between(5, 200)]
    k_eld = kk.groupby(pd.to_datetime(kk.Date).dt.to_period("M")).Wholesale.median()
    perkg, white, dry = (series(mk, "Maize", "KG"), series(mk, "Maize (white)", "90 KG"),
                         series(mk, "Maize (white, dry)", "90 KG"))
    for m in pd.period_range("2006-01", UG_END, freq="M"):
        if m <= pd.Period(UG_PERKG_END, "M"):
            if m in perkg.index:
                rows.append(("Uasin-Gishu", m, perkg[m], "WFP Eldoret, Maize per kg"))
            elif m in white.index:
                rows.append(("Uasin-Gishu", m, white[m], "WFP Eldoret, Maize (white) per 90 kg / 90"))
            else:
                rows.append(("Uasin-Gishu", m, np.nan, "missing"))
        elif m in dry.index:
            rows.append(("Uasin-Gishu", m, dry[m], "WFP Eldoret, Maize (white, dry) per 90 kg / 90"))
        elif m in k_eld.index:
            rows.append(("Uasin-Gishu", m, k_eld[m], "KAMIS Eldoret Main Market (Zindi), monthly median"))
        else:
            rows.append(("Uasin-Gishu", m, np.nan, "missing"))
    out = pd.DataFrame(rows, columns=["county", "month", "wholesale_kes_per_kg", "source"])
    out["wholesale_kes_per_kg"] = out.wholesale_kes_per_kg.round(4)
    return out


def main():
    OUT.mkdir(exist_ok=True)
    PROC.mkdir(exist_ok=True)
    agribora().to_csv(OUT / "agribora_weekly.csv", index=False)
    k = kamis()
    k.to_csv(OUT / "kamis.csv", index=False)
    w = wfp()
    w.to_csv(OUT / "wfp.csv", index=False)
    m = monthly_series(w, k)
    m.to_csv(PROC / "wfp_monthly_wholesale.csv", index=False)
    for c, g in m.groupby("county"):
        miss = g[g.wholesale_kes_per_kg.isna()].month.astype(str).tolist()
        print(f"{c}: {g.month.min()} -> {g.month.max()}, {g.wholesale_kes_per_kg.notna().sum()}/{len(g)} months; missing {miss}")


if __name__ == "__main__":
    main()
