"""
Visualize the storage decision on the CRR binomial tree (warehouse case).

Run from the repo root after the notebook has written data/processed/model_params.json:

    python figures/storage_tree.py

One step per month (Dec -> Nov). Each node is a possible Eldoret price; its colour is the
tree's decision there (wait or sell), its size the probability of reaching it under the
seasonal drift. Nodes after the sale month are greyed: the grain has already been sold.
The backward induction is done here by hand and checked against qk.binomial_optimal_stopping.
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import quantkit as qk  # noqa: E402

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
WAIT, SELL, DONE = "#2a78d6", "#e34948", "#c9c8c3"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

S0 = 40.0                                  # illustrative December price, KSh/kg
R, FEE, LOSS = 0.15, 0.03, 0.0             # warehouse scenario (worksheet §3)


def main():
    par = json.loads((ROOT / "data" / "processed" / "model_params.json").read_text())
    sigma = par["sigma"]
    mu = np.array([par["mu_arith_annual"][m] for m in MONTHS[:11]])   # steps ending Jan..Nov
    n, dt = len(mu), 1 / 12
    u, d, p = qk.crr_parameters(sigma, dt, np.exp(mu * dt))
    disc = np.exp(-(R + FEE + LOSS) * dt)

    # node prices: column i has i+1 nodes, j = number of up moves
    price = [S0 * u ** np.arange(i + 1) * d ** (i - np.arange(i + 1)) for i in range(n + 1)]
    # backward induction (payoff = price)
    value = [None] * (n + 1)
    sell = [None] * (n + 1)
    value[n] = price[n].copy()
    sell[n] = np.ones(n + 1, bool)
    for i in range(n - 1, -1, -1):
        cont = disc * (p[i] * value[i + 1][1:] + (1 - p[i]) * value[i + 1][:-1])
        sell[i] = price[i] >= cont
        value[i] = np.where(sell[i], price[i], cont)
    check = qk.binomial_optimal_stopping(S0, sigma, n / 12, n, lambda S: S, R, drift=mu,
                                         holding_cost=FEE + LOSS)
    assert np.isclose(value[0][0], check), (value[0][0], check)

    # probability of reaching each node, and whether the grain is still held there
    prob = [np.array([1.0])]
    for i in range(n):
        q = np.zeros(i + 2)
        q[1:] += prob[i] * p[i]
        q[:-1] += prob[i] * (1 - p[i])
        prob.append(q)
    first_sell = next(i for i in range(n + 1) if sell[i].all())   # calendar rule: everyone sells here

    fig, ax = plt.subplots(figsize=(12, 6.6), dpi=150)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    for i in range(n):                                            # branches
        for j in range(i + 1):
            col = GRID if i >= first_sell else "#9fb9d9"
            ax.plot([i, i + 1], [price[i][j], price[i + 1][j + 1]], color=col, lw=0.8, zorder=1)
            ax.plot([i, i + 1], [price[i][j], price[i + 1][j]], color=col, lw=0.8, zorder=1)
    for i in range(n + 1):                                        # nodes
        colour = WAIT if i < first_sell else (SELL if i == first_sell else DONE)
        sizes = 15 + 900 * prob[i] / prob[i].max() * (1 if i <= first_sell else 0.35)
        ax.scatter(np.full(i + 1, i), price[i], s=sizes, color=colour, edgecolor=SURF,
                   linewidth=0.8, zorder=3)
    # expected price path (mean of the tree) for reference
    mean_path = [np.sum(prob[i] * price[i]) for i in range(n + 1)]
    ax.plot(range(n + 1), mean_path, color=INK, lw=1.4, ls="--", zorder=2)
    ax.text(n + 0.15, mean_path[-1], "expected\nprice", color=INK, fontsize=9, va="center")
    # up-probability per month along the top
    for i in range(n):
        ax.text(i + 0.5, 1.01, f"{p[i]:.2f}", transform=ax.get_xaxis_transform(), ha="center",
                va="bottom", fontsize=8, color=INK2)
    ax.text(-0.35, 1.01, "P(up):", transform=ax.get_xaxis_transform(), ha="right", va="bottom",
            fontsize=8, color=INK2)

    ax.set_yscale("log")
    ticks = [10, 20, 30, 40, 60, 80, 120, 160]
    ax.set_yticks(ticks, [str(t) for t in ticks])
    ax.minorticks_off()
    ax.set_ylim(price[n][0] * 0.9, price[n][-1] * 1.1)
    ax.set_xticks(range(n + 1), ["Dec"] + MONTHS[:n])
    ax.set_xlim(-0.6, n + 1.1)
    ax.set_ylabel("possible Eldoret price, KSh/kg (log scale)")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.grid(axis="x", visible=False)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(length=0)
    ax.legend(handles=[
        Line2D([], [], marker="o", ls="", color=WAIT, ms=9, label="wait: holding is worth more than selling"),
        Line2D([], [], marker="o", ls="", color=SELL, ms=9, label=f"sell: end of {MONTHS[first_sell - 1]}, at every price"),
        Line2D([], [], marker="o", ls="", color=DONE, ms=9, label="never reached: grain already sold"),
        Line2D([], [], color=INK, ls="--", lw=1.4, label="expected price under the seasonal drift"),
    ], loc="upper left", frameon=True, facecolor="white", framealpha=1, edgecolor=INK2, fancybox=False,
        fontsize=9, title="node size = probability of reaching it", title_fontsize=9)
    fig.text(0.01, 0.985, "The storage decision on a binomial tree (warehouse, 40 KSh/kg in December)",
             color=INK, fontsize=14, va="top")
    fig.text(0.01, 0.945, f"Each month the price moves up ×{u:.3f} or down ×{d:.3f}; P(up) follows the "
             f"seasonal drift. Working back from November, every node compares 'sell now' with 'wait'.\n"
             f"Value today: {value[0][0]:.2f} KSh/kg vs {S0:.0f} for selling now (+{100 * (value[0][0] / S0 - 1):.0f}% "
             f"before the one-off fee). σ = {sigma:.2f}, loan rate {R:.0%}, fee {FEE:.0%}/yr, no losses.",
             color=INK2, fontsize=9.5, va="top", linespacing=1.4)
    fig.subplots_adjust(left=0.08, right=0.95, top=0.84, bottom=0.07)
    out = ROOT / "figures" / "storage_tree.png"
    fig.savefig(out, facecolor=SURF)
    print("wrote", out, "| tree value", round(value[0][0], 4), "= quantkit", round(check, 4),
          "| sell month", MONTHS[first_sell - 1])


if __name__ == "__main__":
    main()
