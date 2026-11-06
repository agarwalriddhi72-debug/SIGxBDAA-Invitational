import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

# ---- 1. Load -------------------------------------------------------------
us = pd.read_csv("us_by_sector.csv")

# ---- 2. Setup --------------------------------------------------------------
# (column, panel title, y-axis label)
panels = [
    ("heat_mmbtu_per_ton", "Heat content",     "million Btu per short ton"),
    ("sulfur_pct",         "Sulfur content",   "% sulfur by weight"),
    ("ash_pct",            "Ash content",      "% ash by weight"),
    ("price_usd_per_ton",  "Delivered price",  "dollars per short ton"),
]

colors = {
    "Power":        "#2b6cb0",   # blue
    "Industrial":   "#e08a1e",   # orange
    "Coke (steel)": "#7b4fb0",   # purple
    "Commercial":   "#d64545",   # red
}
order = ["Power", "Industrial", "Coke (steel)", "Commercial"]

BG, FG, MUTED = "#ffffff", "#1a1a1a", "#555555"
halo = [pe.withStroke(linewidth=3, foreground="white")]

# ---- 3. Plot ---------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10.5), facecolor=BG)

for ax, (col, title, ylabel) in zip(axes.flat, panels):
    ax.set_facecolor(BG)
    ends = []

    for sector in order:
        d = us[us["sector_group"] == sector].sort_values("year")
        d_ok = d.dropna(subset=[col])           # bridges gaps with a dashed line

        # dashed line bridges any missing year (e.g. Power price in 2021)
        ax.plot(d_ok["year"], d_ok[col], color=colors[sector],
                linewidth=1.5, linestyle=(0, (3, 3)), alpha=0.6, zorder=2)
        # solid line only where consecutive years both exist
        ax.plot(d["year"], d[col], color=colors[sector], linewidth=2.6, zorder=3)
        # dots, hollow for preliminary 2025
        hist = d_ok[d_ok["year"] < 2025]
        prelim = d_ok[d_ok["year"] == 2025]
        ax.scatter(hist["year"], hist[col], color=colors[sector], s=34, zorder=4)
        ax.scatter(prelim["year"], prelim[col], facecolor="white",
                   edgecolor=colors[sector], linewidth=2, s=44, zorder=4)

        ends.append((sector, d_ok.iloc[-1]["year"], d_ok.iloc[-1][col]))

    # Direct labels at the right end of each line, nudged apart so they never overlap
    lo, hi = ax.get_ylim()
    min_gap = (hi - lo) * 0.065
    ends.sort(key=lambda e: e[2])
    ypos = []
    for _, _, val in ends:
        ypos.append(val if not ypos else max(val, ypos[-1] + min_gap))
    for (sector, yr, val), y in zip(ends, ypos):
        ax.text(yr + 0.18, y, sector, va="center", fontsize=9.5, fontweight="bold",
                color=colors[sector], path_effects=halo)

    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=FG, pad=10)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=10)
    ax.set_xticks(range(2020, 2026))
    ax.set_xlim(2019.8, 2026.4)                  # room for the end labels
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color="#e3e3e3", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#bbbbbb")

# Titles and footnote
fig.text(0.04, 0.965, "Coal Quality & Pricing by Sector, 2020 to 2025", color=FG,
         fontsize=18, fontweight="bold", ha="left")
fig.text(0.04, 0.93, "U.S. national averages. Each panel is one measure, each line is one sector.",
         color=MUTED, fontsize=10.5, ha="left")

legend_items = [
    Line2D([0], [0], marker="o", color="none", markerfacecolor="#555555",
           markeredgecolor="#555555", markersize=7, label="Final data"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
           markeredgecolor="#555555", markeredgewidth=2, markersize=7, label="2025 (preliminary)"),
    Line2D([0], [0], color="#555555", linestyle=(0, (3, 3)), linewidth=1.5, label="Gap in data bridged"),
]
fig.legend(handles=legend_items, loc="lower left", bbox_to_anchor=(0.04, 0.005),
           ncol=3, frameon=False, fontsize=9.5, labelcolor=MUTED)

plt.tight_layout(rect=(0, 0.04, 1, 0.92), h_pad=4.5, w_pad=6)
plt.savefig("coal_quality_pricing.png", dpi=200, facecolor=BG)

# ---- 4. Quick summary in the command window ------------------------------------
print("\nChange from 2020 to 2025, by sector:")
for col, title, _ in panels:
    print(f"\n{title}")
    for sector in order:
        d = us[us["sector_group"] == sector].set_index("year")[col].dropna()
        print(f"  {sector:<13} {d.loc[2020]:>8.2f} -> {d.loc[2025]:>8.2f}  ({(d.loc[2025]/d.loc[2020]-1)*100:+.1f}%)")

plt.show()