"""
Uasin-Gishu price figure: price history (top) and seasonal pattern (bottom).

Run from the repo root after data/make_data.py:

    python figures/make_figures.py

Writes figures/uasin_gishu_price_2006_2025.png.

Visual conventions:
  * Grey bands (top panel) = months with no price, and only that.
  * The 2022-23 drought price spike is marked with a bracket above the top
    panel, not shading, so it can't be confused with missing data.
  * The bottom panel and its test statistics come from figures/seasonality.py,
    so the numbers match that script exactly.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG = ROOT / "data", ROOT / "figures"
sys.path.insert(0, str(FIG))
import seasonality as season  # noqa: E402

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"            # default categorical slots 1-2
SPIKE = (pd.Timestamp("2022-03-01"), pd.Timestamp("2023-10-01"))
plt.rcParams.update({"font.size": 11, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2})


def month_mid(months):
    return pd.PeriodIndex(months, freq="M").to_timestamp() + pd.Timedelta(days=14)


def style(ax):
    ax.set_facecolor(SURF)
    ax.grid(axis="y", color=GRID, lw=.8)
    ax.grid(axis="x", visible=False)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(length=0)


def spike_bracket(ax):
    """Bracket in the margin above the plot area, spanning the spike months."""
    trans = ax.get_xaxis_transform()   # x in data units, y in axes fraction
    y = 1.02
    a, b = mdates.date2num(SPIKE[0]), mdates.date2num(SPIKE[1])
    ax.plot([a, a, b, b], [y - .02, y, y, y - .02], color=INK2, lw=1.2,
            transform=trans, clip_on=False)
    ax.text((a + b) / 2, y + .015, "2022–23 drought price spike", ha="center",
            va="bottom", color=INK2, fontsize=10, transform=trans)


def price_panel(ax, u):
    style(ax)
    miss = u[u.wholesale_kes_per_kg.isna()]
    for d in miss.date:
        ax.axvspan(d - pd.Timedelta(days=15), d + pd.Timedelta(days=15), color=GRID, lw=0, zorder=0.5)
    spike_bracket(ax)
    h = [ax.plot(u.date, u.wholesale_kes_per_kg, color=BLUE, lw=2, zorder=2, label="WFP Eldoret town")[0]]
    f = u[u.source.str.startswith("KAMIS") | u.source.str.contains(r"\(white\) per 90")]
    h.append(ax.scatter(f.date, f.wholesale_kes_per_kg, s=42, facecolor=ORANGE, edgecolor=SURF,
                        linewidth=2, zorder=3, label="Gap filled (other WFP series or KAMIS Eldoret Main)"))
    h.append(Patch(facecolor=GRID, edgecolor="none", label=f"No price that month ({len(miss)} months)"))
    pk = u.loc[u.wholesale_kes_per_kg.idxmax()]
    ax.annotate(f"{pk.wholesale_kes_per_kg:.1f} ({pk.date.strftime('%b %Y')})",
                (pk.date, pk.wholesale_kes_per_kg), xytext=(8, 4), textcoords="offset points",
                color=INK, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_xlim(pd.Timestamp("2005-10-01"), pd.Timestamp("2025-10-01"))
    ax.set_ylabel("Wholesale price (KSh / kg)")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(handles=h, loc="upper left", labelcolor=INK, **season.LEGEND_BOX)
    ax.set_title("Price history", loc="left", color=INK, fontsize=12.5, pad=30)


def seasonal_panel(ax, county="Uasin-Gishu"):
    a, b = season.WINDOWS[county]
    s = season.load(county, a, b)
    res = season.run_tests(s, np.random.default_rng(2026))
    top, bottom = season.panel(ax, county, s, res)        # draws lines, band, stats text
    ax.set_ylim(25 * np.floor(bottom / 25) - 5, 25 * np.ceil(top / 25) + 5)
    ax.set_ylabel("Price vs Dec–Jan harvest level, %")
    ax.set_title("Seasonal pattern: each season's price relative to its harvest level",
                 loc="left", color=INK, fontsize=12.5, pad=12)
    ax.legend(handles=[Line2D([], [], color=season.SEASON_CMAP(0.55), lw=1.2,
                              label="One season (Dec → Nov), coloured by year"),
                       Line2D([], [], color=season.AVG, lw=3.5, label="Average"),
                       Patch(facecolor=season.AVG_BAND, edgecolor="none", label="95% confidence band")],
              loc="upper left", labelcolor=INK, **season.LEGEND_BOX)


def main():
    m = pd.read_csv(DATA / "processed" / "wfp_monthly_wholesale.csv")
    m["date"] = month_mid(m.month)
    u = m[m.county == "Uasin-Gishu"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 11.5), dpi=150,
                                   gridspec_kw={"height_ratios": [1, 1.05]})
    fig.patch.set_facecolor(SURF)
    price_panel(ax1, u)
    seasonal_panel(ax2)
    fig.text(0.015, 0.985, "Uasin-Gishu (Eldoret) monthly wholesale maize price, 2006–2025",
             color=INK, fontsize=14.5, va="top")
    fig.text(0.015, 0.962, "Sources: WFP / HDX (CC BY-IGO); KAMIS via Zindi agriBORA challenge. "
             "Nominal KSh per kg.", color=INK2, fontsize=9.5, va="top")
    fig.subplots_adjust(left=0.07, right=0.9, top=0.885, bottom=0.04, hspace=0.3)
    pos = ax2.get_position()
    season.season_colorbar(fig, fig.add_axes([0.915, pos.y0, 0.012, pos.height]))
    out = FIG / "uasin_gishu_price_2006_2025.png"
    fig.savefig(out, facecolor=SURF)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
