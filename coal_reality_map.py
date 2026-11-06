import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle

# ---- 1. Load -------------------------------------------------------------
states = pd.read_csv("states_by_sector.csv")

# ---- 2. Total each state across sectors, 2024 vs 2025 ----------------------
cols = ["consumption_tons", "receipts_tons"]
totals = (
    states[states["year"].isin([2024, 2025])]
    .groupby(["location_code", "year"])[cols]
    .sum(min_count=1)
    .unstack("year")
)
df = pd.DataFrame({
    "cons_24": totals[("consumption_tons", 2024)],
    "cons_25": totals[("consumption_tons", 2025)],
    "rec_24":  totals[("receipts_tons", 2024)],
    "rec_25":  totals[("receipts_tons", 2025)],
}).dropna()
df = df[(df["cons_24"] > 0) & (df["rec_24"] > 0)]

# ---- 3. Percent growth -----------------------------------------------------
df["cons_growth"] = (df["cons_25"] / df["cons_24"] - 1) * 100
df["rec_growth"]  = (df["rec_25"]  / df["rec_24"]  - 1) * 100

# ---- 4. Quadrant definitions (x = deliveries, y = consumption) -------------
# name, sub-label, background tint, bubble color, title color
Q = {
    "real":      ("REAL\nRECOVERY",      "Consumption ↑   Deliveries ↑", "#e3f3f0", "#1b9e8f", "#0f6f64"),
    "phantom":   ("PHANTOM\nRECOVERY",   "Consumption ↑   Deliveries ↓", "#edf4df", "#6aa21f", "#4a7311"),
    "contract":  ("CONTRACTION",         "Consumption ↓   Deliveries ↓", "#fcefdc", "#e08a1e", "#a05a08"),
    "inventory": ("INVENTORY\nBUILDING", "Consumption ↓   Deliveries ↑", "#fae5e5", "#d64545", "#a32d2d"),
}

def quadrant(row):
    up_c = row.cons_growth >= 0
    up_d = row.rec_growth >= 0
    if up_c and up_d:      return "real"
    if up_c and not up_d:  return "phantom"
    if not up_c and up_d:  return "inventory"
    return "contract"

df["quad"] = df.apply(quadrant, axis=1)
df["color"] = df["quad"].map(lambda k: Q[k][3])

# ---- 5. Plot ---------------------------------------------------------------
BG, FG, MUTED = "#ffffff", "#1a1a1a", "#555555"
fig, ax = plt.subplots(figsize=(12, 9), facecolor=BG)
ax.set_facecolor(BG)

# Axis limits with padding
xpad = (df["rec_growth"].max() - df["rec_growth"].min()) * 0.12
ypad = (df["cons_growth"].max() - df["cons_growth"].min()) * 0.12
xmin, xmax = min(df["rec_growth"].min() - xpad, -5), df["rec_growth"].max() + xpad
ymin = min(df["cons_growth"].min() - ypad, -5)
ymax = df["cons_growth"].max() + ypad * 2.6   # extra headroom for quadrant titles
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

# Softly tinted quadrant backgrounds
rects = {
    "phantom":   (xmin, 0, -xmin, ymax),
    "real":      (0, 0, xmax, ymax),
    "contract":  (xmin, ymin, -xmin, -ymin),
    "inventory": (0, ymin, xmax, -ymin),
}
for key, (x, y, w, h) in rects.items():
    ax.add_patch(Rectangle((x, y), w, h, facecolor=Q[key][2], edgecolor="none", zorder=0))

# Dashed center lines
ax.axhline(0, color="#444444", linestyle=(0, (4, 3)), linewidth=1.6, zorder=1)
ax.axvline(0, color="#444444", linestyle=(0, (4, 3)), linewidth=1.6, zorder=1)

# Quadrant titles (x in data units, y in axes units), left-aligned inside each quadrant
trans = ax.get_xaxis_transform()
xl = (xmax - xmin) * 0.02

def quad_label(key, x, y_title, y_sub, va):
    title, sub, _, _, tcolor = Q[key]
    ax.text(x, y_title, title, ha="left", va=va, color=tcolor, fontsize=17,
            fontweight="bold", transform=trans, linespacing=1.15, zorder=2)
    ax.text(x, y_sub, sub, ha="left", va=va, color=MUTED, fontsize=10,
            transform=trans, zorder=2)

quad_label("phantom",   xmin + xl, 0.97, 0.875, "top")
quad_label("real",      0 + xl,    0.97, 0.875, "top")
quad_label("contract",  xmin + xl, 0.10, 0.07,  "bottom")
quad_label("inventory", 0 + xl,    0.10, 0.07,  "bottom")

# Bubbles (size = 2025 consumption)
ax.scatter(
    df["rec_growth"], df["cons_growth"],
    s=df["cons_25"] / df["cons_25"].max() * 2200,
    c=df["color"], alpha=0.8, edgecolor="white", linewidth=1.2, zorder=3,
)

# State labels: biggest states plus the biggest outliers (white halo keeps them readable)
halo = [pe.withStroke(linewidth=2.5, foreground="white")]
label = set(df.nlargest(12, "cons_25").index)
label |= set(df["cons_growth"].abs().nlargest(4).index)
label |= set(df["rec_growth"].abs().nlargest(4).index)
for code in label:
    r = df.loc[code]
    ax.annotate(code, (r.rec_growth, r.cons_growth), xytext=(6, 6),
                textcoords="offset points", color=FG, fontsize=9.5,
                fontweight="bold", zorder=4, path_effects=halo)

# Axes styling
ax.set_xlabel("% change in deliveries, 2024 to 2025", color=FG, fontsize=12, labelpad=10)
ax.set_ylabel("% change in consumption, 2024 to 2025", color=FG, fontsize=12, labelpad=10)
ax.tick_params(colors=MUTED)
for s in ax.spines.values():
    s.set_visible(False)

# Titles
fig.text(0.04, 0.965, "Coal Recovery Reality Matrix", color=FG, fontsize=18, fontweight="bold", ha="left")
fig.text(0.04, 0.93, "Each bubble is a state  |  X = change in deliveries  |  Y = change in consumption  |  "
         "bubble size = 2025 consumption", color=MUTED, fontsize=10, ha="left")
fig.text(0.04, 0.012, "2025 data is preliminary. States with no 2024 or 2025 data are excluded.",
         color="#777777", fontsize=9, ha="left")

plt.tight_layout(rect=(0, 0.03, 1, 0.92))
plt.savefig("coal_recovery_matrix_white.png", dpi=200, facecolor=BG)

# ---- 6. Summary in the command window ----------------------------------------
print(f"\n{len(df)} states plotted\n")
for key in ["real", "phantom", "contract", "inventory"]:
    members = sorted(df.index[df["quad"] == key])
    name = Q[key][0].replace("\n", " ")
    print(f"{name:<20} {len(members):>2} states: {', '.join(members)}")

plt.show()