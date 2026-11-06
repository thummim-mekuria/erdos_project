"""
Is there a seasonal price cycle? Tests + figure for Uasin-Gishu and Nairobi.

Run from the repo root after data/make_data.py:

    python figures/seasonality.py

Prints the tests and writes figures/seasonality_uasin_gishu_vs_nairobi.png.

Tests (monthly log returns r_t = log P_t - log P_{t-1}):
  1. Joint test that all 12 calendar months have the same mean return:
     one-way ANOVA and Kruskal-Wallis (rank-based, no normality assumption).
  2. Annual sine fit r_t = a + b sin(2 pi m/12) + c cos(2 pi m/12); the cycle
     size is sqrt(b^2 + c^2). Its p-value comes from a random-phase
     permutation test: each year's 12 returns are rotated by an independent
     random number of months, which destroys any seasonal timing shared
     across years but keeps each year's returns (and their size) intact.
     (Rotating the whole series by one common lag is NOT a valid null: it
     only moves the cycle to another month and leaves its size unchanged.)
  3. Year-by-year consistency: the log change from the harvest window
     (Dec of the previous year + Jan) to the lean window (May-Jul); one-sided
     sign test that it is positive more often than half the time.
  4. Stability: tests 1-3 repeated on each half of the sample.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, BLUE_BAND, YEAR_LINE = "#2a78d6", "#cde2fb", "#c3c2b7"
SEASON = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]          # harvest-first ordering
MONTHS = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
WINDOWS = {"Uasin-Gishu": ("2006-01", "2025-06"), "Nairobi": ("2006-01", "2021-11")}
N_PERM = 5000


def load(county, start, end):
    m = pd.read_csv(ROOT / "data" / "processed" / "wfp_monthly_wholesale.csv")
    s = m[m.county == county].set_index("month").wholesale_kes_per_kg.loc[start:end]
    s.index = pd.PeriodIndex(s.index, freq="M")
    return s


def sine_amplitude(year_by_month):
    mon = np.tile(np.arange(1, 13), (year_by_month.shape[0], 1))
    ok = ~np.isnan(year_by_month)
    y, mm = year_by_month[ok], mon[ok]
    X = np.column_stack([np.ones(len(y)), np.sin(2 * np.pi * mm / 12), np.cos(2 * np.pi * mm / 12)])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return np.hypot(b[1], b[2])


def seasonal_rises(s):
    """Log change from Dec(prev)+Jan average to May-Jul average, per year."""
    lv = np.log(s)
    out = {}
    for yr in range(s.index.year.min() + 1, s.index.year.max() + 1):
        h = lv[[p for p in lv.index if (p.year == yr - 1 and p.month == 12) or (p.year == yr and p.month == 1)]].dropna()
        l = lv[[p for p in lv.index if p.year == yr and p.month in (5, 6, 7)]].dropna()
        if len(h) and len(l):
            out[yr] = l.mean() - h.mean()
    return pd.Series(out)


def run_tests(s, rng):
    lr = np.log(s).diff().dropna()
    groups = [lr[lr.index.month == k].values for k in range(1, 13)]
    full = np.log(s).diff()
    years = sorted(set(full.index.year))
    Y = np.full((len(years), 12), np.nan)
    for p, v in full.items():
        Y[years.index(p.year), p.month - 1] = v
    amp = sine_amplitude(Y)
    null = np.array([sine_amplitude(np.array([np.roll(r, rng.integers(12)) for r in Y]))
                     for _ in range(N_PERM)])
    rises = seasonal_rises(s)
    pos = int((rises > 0).sum())
    return dict(n=len(lr),
                anova_p=stats.f_oneway(*groups).pvalue,
                kw_p=stats.kruskal(*groups).pvalue,
                amp=amp, amp_p=(np.sum(null >= amp) + 1) / (N_PERM + 1),
                rises=rises, pos=pos,
                sign_p=stats.binomtest(pos, len(rises), .5, alternative="greater").pvalue)


def season_paths(s):
    """Log price relative to each season's harvest base (Dec prev + Jan), Dec..Nov."""
    lv = np.log(s)
    rows = {}
    for yr in range(s.index.year.min() + 1, s.index.year.max() + 1):
        months = [pd.Period(f"{yr - 1}-12", "M")] + [pd.Period(f"{yr}-{m:02d}", "M") for m in range(1, 12)]
        vals = lv.reindex(months)
        base = vals.iloc[:2].mean()
        if np.isfinite(base) and vals.notna().sum() >= 9:
            rows[yr] = (vals - base).values
    return pd.DataFrame(rows, index=MONTHS).T          # seasons x months


def panel(ax, county, s, res):
    P = season_paths(s)
    pct = 100 * (np.exp(P) - 1)
    for _, row in pct.iterrows():
        ax.plot(range(12), row.values, color=YEAR_LINE, lw=1, zorder=1)
    mean = P.mean()
    se = P.std() / np.sqrt(P.count())
    lo, hi = 100 * (np.exp(mean - 1.96 * se) - 1), 100 * (np.exp(mean + 1.96 * se) - 1)
    ax.fill_between(range(12), lo, hi, color=BLUE_BAND, lw=0, zorder=2)
    ax.plot(range(12), 100 * (np.exp(mean) - 1), color=BLUE, lw=2.5, zorder=3)
    ax.axhline(0, color=INK2, lw=1, zorder=2)
    ax.set_xticks(range(12), MONTHS)
    ax.set_title(county, loc="left", color=INK, fontsize=13, pad=58)
    ax.grid(axis="y", color=GRID, lw=.8)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(length=0)
    ax.set_facecolor(SURF)
    a, b = WINDOWS[county]
    txt = (f"{a[:4]}–{b[:4]}, {len(P)} seasons\n"
           f"May–Jul above Dec–Jan in {res['pos']} of {len(res['rises'])} years (sign test p = {res['sign_p']:.2g})\n"
           f"Seasonal cycle {100 * res['amp']:.1f}%/month (permutation p = {res['amp_p']:.2g})")

    ax.text(0, 1.02, txt, transform=ax.transAxes, va="bottom", color=INK2, fontsize=9.5, linespacing=1.4)
    return float(np.nanmax(pct.values)), float(np.nanmin(pct.values))


def main():
    rng = np.random.default_rng(2026)
    results = {}
    for county, (a, b) in WINDOWS.items():
        s = load(county, a, b)
        results[county] = (s, run_tests(s, rng))
        mid = f"{(int(a[:4]) + int(b[:4])) // 2}-12"
        print(f"\n{county} {a}..{b}")
        for lab, (x, y) in {"full": (a, b), "first half": (a, mid),
                            "second half": (f"{int(mid[:4]) + 1}-01", b)}.items():
            r = run_tests(load(county, x, y), rng)
            print(f"  {lab:11s} n={r['n']:3d}  ANOVA p={r['anova_p']:.2g}  KW p={r['kw_p']:.2g}  "
                  f"cycle {100 * r['amp']:.1f}%/mo (perm p={r['amp_p']:.2g})  "
                  f"rise>0 in {r['pos']}/{len(r['rises'])} yrs (sign p={r['sign_p']:.2g})")

    plt.rcParams.update({"font.size": 11, "xtick.color": INK2, "ytick.color": INK2,
                         "axes.labelcolor": INK2})
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.4), dpi=150, sharey=True)
    fig.patch.set_facecolor(SURF)
    ext = [panel(ax, county, *results[county]) for ax, county in zip(axes, WINDOWS)]
    axes[0].set_ylabel("Price vs harvest level (Dec–Jan average), %")
    top, bottom = max(e[0] for e in ext), min(e[1] for e in ext)
    axes[0].set_ylim(25 * np.floor(bottom / 25) - 5, 25 * np.ceil(top / 25) + 5)
    fig.suptitle("Uasin-Gishu prices rise after harvest almost every year; Nairobi's don't",
                 x=0.01, ha="left", color=INK, fontsize=14, y=0.995)
    fig.text(0.01, 0.945, "Grey: each season (Dec → Nov). Blue: average, with 95% confidence band. "
             "Monthly wholesale prices, WFP / HDX; gaps filled per data/README.md.",
             color=INK2, fontsize=9.5)
    fig.subplots_adjust(left=0.06, right=0.99, bottom=0.07, top=0.76, wspace=0.08)
    out = ROOT / "figures" / "seasonality_uasin_gishu_vs_nairobi.png"
    fig.savefig(out, facecolor=SURF)
    print("\nwrote", out)


if __name__ == "__main__":
    main()
