"""
Price-history figures for Uasin-Gishu and Nairobi.

Run from the repo root after data/make_data.py:

    python figures/make_figures.py

Writes figures/uasin_gishu_price_2006_2025.png and
figures/nairobi_price_2006_2025.png.

Visual conventions:
  * Grey bands = months with no price (and only that).
  * The 2022-23 drought price spike is marked with a bracket above the plot,
    not shading, so it can't be confused with missing data.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG = ROOT / "data", ROOT / "figures"

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"   # default categorical slots 1-3
VIOLET = "#6250d6"                                      # slot 7
SPIKE = (pd.Timestamp("2022-03-01"), pd.Timestamp("2023-10-01"))
YMAX = 100
plt.rcParams.update({"font.size": 11, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})


def month_mid(months):
    return pd.PeriodIndex(months, freq="M").to_timestamp() + pd.Timedelta(days=14)


def kangemi_series():
    """Kangemi 2021-02 onward: WFP white-dry / 90, gaps filled from KAMIS Kangemi."""
    w = pd.read_csv(DATA / "nairobi_uasingishu" / "wfp.csv")
    w = w[(w.market == "Kangemi (Nairobi)") & (w.pricetype == "Wholesale")
          & (w.commodity == "Maize (white, dry)")]
    W = w.groupby(pd.to_datetime(w.date).dt.to_period("M")).price.mean() / 90
    k = pd.read_csv(DATA / "nairobi_uasingishu" / "kamis.csv", parse_dates=["Date"]).drop_duplicates()
    k = k[(k.Market == "Kangemi_Market") & (k.Commodity_Classification == "Dry_White_Maize")
          & k.Wholesale.between(5, 200)]
    K = k.groupby(k.Date.dt.to_period("M")).Wholesale.median()
    full = pd.period_range("2021-02", "2025-12", freq="M")
    out = pd.DataFrame({"p": W.reindex(full)})
    out["filled"] = out.p.isna() & K.reindex(full).notna()
    out["p"] = out.p.fillna(K.reindex(full))
    out = out.loc[:out.p.last_valid_index()]
    out["date"] = month_mid(out.index.astype(str))
    return out


def kamis_market_series(market):
    """Monthly median KAMIS (Zindi) wholesale price for one market, dry white maize."""
    k = pd.read_csv(DATA / "nairobi_uasingishu" / "kamis.csv", parse_dates=["Date"]).drop_duplicates()
    k = k[(k.Market == market) & (k.Commodity_Classification == "Dry_White_Maize")
          & k.Wholesale.between(5, 200)]
    K = k.groupby(k.Date.dt.to_period("M")).Wholesale.median()
    K = K.reindex(pd.period_range(K.index.min(), K.index.max(), freq="M"))
    return pd.DataFrame({"p": K, "date": month_mid(K.index.astype(str))})


def setup(title, n_missing, band_note=""):
    fig, ax = plt.subplots(figsize=(12, 5.6), dpi=150)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    ax.set_ylim(0, YMAX)
    ax.set_ylabel("Wholesale price (KSh / kg)")
    ax.grid(axis="y", color=GRID, lw=.8)
    ax.grid(axis="x", visible=False)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(length=0)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_title(title, loc="left", color=INK, fontsize=14, pad=62)
    ax.text(0, 1.115, f"{n_missing} months with no price{band_note}.\nSources: WFP / HDX (CC BY-IGO); "
            "KAMIS via Zindi agriBORA challenge.", transform=ax.transAxes, color=INK2, fontsize=9.5,
            va="bottom", linespacing=1.4)
    return fig, ax


def missing_bands(ax, dates):
    for d in dates:
        ax.axvspan(d - pd.Timedelta(days=15), d + pd.Timedelta(days=15),
                   color=GRID, lw=0, zorder=0.5)


def spike_bracket(ax):
    """Bracket in the margin above the plot area, spanning the spike months."""
    trans = ax.get_xaxis_transform()   # x in data units, y in axes fraction
    y = 1.02
    a, b = mdates.date2num(SPIKE[0]), mdates.date2num(SPIKE[1])
    ax.plot([a, a, b, b], [y - .02, y, y, y - .02], color=INK2, lw=1.2,
            transform=trans, clip_on=False)
    ax.text((a + b) / 2, y + .012, "2022–23 drought price spike", ha="center",
            va="bottom", color=INK2, fontsize=10, transform=trans)


def finish(fig, ax, handles, path, xmax):
    ax.set_xlim(pd.Timestamp("2005-10-01"), xmax)
    handles.append(Patch(facecolor=GRID, edgecolor="none", label="No price that month"))
    ax.legend(handles=handles, loc="upper left", frameon=False, labelcolor=INK)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURF)
    plt.close(fig)
    print("wrote", path)


def fill_dots(ax, dates, values, label):
    return ax.scatter(dates, values, s=42, facecolor=ORANGE, edgecolor=SURF,
                      linewidth=2, zorder=3, label=label)


def peak_label(ax, date, value, offset=(8, 4), ha="left"):
    ax.annotate(f"{value:.1f} ({date.strftime('%b %Y')})", (date, value), xytext=offset,
                textcoords="offset points", color=INK, fontsize=10, ha=ha)


def main():
    m = pd.read_csv(DATA / "processed" / "wfp_monthly_wholesale.csv")
    m["date"] = month_mid(m.month)
    xmax_default = pd.Timestamp("2025-10-01")

    # --- Uasin-Gishu ------------------------------------------------------
    u = m[m.county == "Uasin-Gishu"]
    miss = u[u.wholesale_kes_per_kg.isna()]
    fig, ax = setup("Uasin-Gishu (Eldoret) monthly wholesale maize price, 2006–2025", len(miss))
    missing_bands(ax, miss.date)
    spike_bracket(ax)
    h = [ax.plot(u.date, u.wholesale_kes_per_kg, color=BLUE, lw=2, zorder=2,
                 label="WFP Eldoret town")[0]]
    f = u[u.source.str.startswith("KAMIS") | u.source.str.contains(r"\(white\) per 90")]
    h.append(fill_dots(ax, f.date, f.wholesale_kes_per_kg,
                       "Gap filled (other WFP series or KAMIS Eldoret Main)"))
    pk = u.loc[u.wholesale_kes_per_kg.idxmax()]
    peak_label(ax, pk.date, pk.wholesale_kes_per_kg)
    finish(fig, ax, h, FIG / "uasin_gishu_price_2006_2025.png", xmax_default)

    # --- Nairobi ----------------------------------------------------------
    n = m[m.county == "Nairobi"]
    kg = kangemi_series()
    miss = pd.concat([n.loc[n.wholesale_kes_per_kg.isna(), "date"], kg.loc[kg.p.isna(), "date"]])
    fig, ax = setup("Nairobi monthly wholesale maize price, 2006–2025", len(miss),
                    " in the Nairobi or Kangemi series (Nyamakima gaps show as line breaks)")
    missing_bands(ax, miss)
    spike_bracket(ax)
    h = [ax.plot(n.date, n.wholesale_kes_per_kg, color=BLUE, lw=2, zorder=2,
                 label='WFP "Nairobi" market, 2006–2021 (calibration series)')[0],
         ax.plot(kg.date, kg.p, color=AQUA, lw=2, ls=(0, (5, 2)), zorder=2,
                 label="Kangemi market, 2021–2025 (WFP + KAMIS; not spliced)")[0]]
    ny = kamis_market_series("Nyamakima_Market")
    h.append(ax.plot(ny.date, ny.p, color=VIOLET, lw=2, ls=(0, (8, 2, 2, 2)), zorder=2,
                     label="Nyamakima market (CBD), 2021–2025 (KAMIS)")[0])
    f = n[n.source.str.contains(r"\(white\) per 90")]
    fk = kg[kg.filled]
    h.append(fill_dots(ax, pd.concat([f.date, fk.date]), pd.concat([f.wholesale_kes_per_kg, fk.p]),
                       "Gap filled (other WFP series or KAMIS, same market)"))
    pk = kg.p.idxmax()
    peak_label(ax, kg.loc[pk, "date"], kg.p.max(), offset=(16, -14))
    pn = ny.p.idxmax()
    peak_label(ax, ny.loc[pn, "date"], ny.p.max(), offset=(-8, 4), ha="right")
    last = n.dropna(subset=["wholesale_kes_per_kg"]).iloc[-1]
    ax.text(last.date, last.wholesale_kes_per_kg - 7, '"Nairobi" series\nends 2021-11',
            ha="center", va="top", color=INK2, fontsize=9.5)
    finish(fig, ax, h, FIG / "nairobi_price_2006_2025.png",
           max(xmax_default, kg.date.max() + pd.Timedelta(days=60)))


if __name__ == "__main__":
    main()
