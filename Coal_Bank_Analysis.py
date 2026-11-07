# ----------------------------------------
# SIG x BDAA Hackathon
# GRAPH 2: THE COAL BANK BALANCE
# using us_by_sector.csv
# ----------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# File paths
# -----------------------------
folder = Path(__file__).resolve().parent
charts_folder = folder / "charts"
charts_folder.mkdir(exist_ok=True)

us_file = folder / "us_by_sector.csv"
states_file = folder / "states_by_sector.csv"   # not used in this graph, but okay to keep in project

# -----------------------------
# Load the CSV
# -----------------------------
us = pd.read_csv(us_file)

# Keep only U.S. Electric Power rows
national = us[us["sector_name"] == "Electric Power"].copy()

# Sort by year
national = national.sort_values("year")

# -----------------------------
# Quick check
# -----------------------------
print(national[[
    "year",
    "stocks_mm_tons",
    "days_of_burn"
]])

# -----------------------------
# Variables
# -----------------------------
years = national["year"]
stocks = national["stocks_mm_tons"]
days = national["days_of_burn"]

# -----------------------------
# Create figure
# -----------------------------
fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(11, 8),
    sharex=True
)

# White background for presentation
fig.patch.set_facecolor("white")
ax1.set_facecolor("white")
ax2.set_facecolor("white")

# -----------------------------
# TOP CHART: Stockpiles
# -----------------------------
ax1.plot(
    years,
    stocks,
    marker="o",
    markersize=8,
    linewidth=3,
    color="#1f4e79"
)

ax1.set_title(
    "The Coal Bank Balance",
    fontsize=18,
    fontweight="bold",
    color="black",
    pad=15
)

ax1.set_ylabel("Stockpiles (Million Tons)", fontsize=12, color="black")
ax1.grid(True, linestyle="--", alpha=0.25)

ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.spines["left"].set_color("black")
ax1.spines["bottom"].set_color("black")
ax1.tick_params(axis="both", colors="black", labelsize=11)

# Value labels
for x, y in zip(years, stocks):
    ax1.text(
        x, y + 2,
        f"{y:.1f}",
        ha="center",
        va="bottom",
        fontsize=10,
        color="#1f4e79"
    )

# -----------------------------
# BOTTOM CHART: Days of Burn
# -----------------------------
ax2.plot(
    years,
    days,
    marker="o",
    markersize=8,
    linewidth=3,
    color="#c55a11"
)

ax2.set_ylabel("Days of Burn", fontsize=12, color="black")
ax2.set_xlabel("Year", fontsize=12, color="black")
ax2.set_xticks(years)
ax2.grid(True, linestyle="--", alpha=0.25)

ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_color("black")
ax2.spines["bottom"].set_color("black")
ax2.tick_params(axis="both", colors="black", labelsize=11)

# Value labels
for x, y in zip(years, days):
    ax2.text(
        x, y + 2,
        f"{y:.1f}",
        ha="center",
        va="bottom",
        fontsize=10,
        color="#c55a11"
    )

# -----------------------------
# Add a subtitle / footnote
# -----------------------------
fig.text(
    0.5, 0.01,
    "Source: U.S. Coal Consumption and Quality dataset (EIA), U.S. Electric Power sector, 2020–2025.",
    ha="center",
    fontsize=10,
    color="gray"
)

# -----------------------------
# Layout and save
# -----------------------------
plt.tight_layout(rect=[0, 0.03, 1, 1])

plt.savefig(
    charts_folder / "02_Coal_Bank_Balance_White.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white"
)

plt.show()


# ---------------------------------------------
# GRAPH 4: ONE COAL MARKET, DIFFERENT FUTURES
# Coal Consumption Growth by Sector (2024-2025)
# ---------------------------------------------


# Keep 2024 and 2025
sector_data = us[
    us["year"].isin([2024, 2025])
].copy()

# Organize consumption by sector and year
sector_table = sector_data.pivot(
    index="sector_name",
    columns="year",
    values="consumption_mm_tons"
)

# Calculate percentage change
sector_table["Growth"] = (
    (sector_table[2025] - sector_table[2024])
    / sector_table[2024]
) * 100

# Sort from highest growth to lowest
sector_table = sector_table.sort_values(
    "Growth", ascending=False
)

# -----------------------------
# Create chart
# -----------------------------

fig, ax = plt.subplots(figsize=(12, 6))

fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Colors
colors = [
    "#1f4e79" if value >= 0 else "#c55a11"
    for value in sector_table["Growth"]
]

# Horizontal bars
bars = ax.barh(
    sector_table.index,
    sector_table["Growth"],
    color=colors,
    height=0.55
)

# Highest growth at top
ax.invert_yaxis()

# Title
ax.set_title(
    "One Coal Market, Different Futures",
    fontsize=19,
    fontweight="bold",
    pad=23
)

# Axis labels
ax.set_xlabel(
    "Change in Coal Consumption (2024–2025, %)",
    fontsize=12
)

# Zero reference line
ax.axvline(
    0,
    color="black",
    linewidth=1
)

# Light gridlines
ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.2
)

ax.set_axisbelow(True)

# Remove unnecessary borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

# Make labels readable
ax.tick_params(
    axis="both",
    labelsize=11,
    length=0
)

# Add percentage and actual consumption values
for bar, (sector, row) in zip(
    bars,
    sector_table.iterrows()
):

    growth = row["Growth"]

    # Place label outside bar
    offset = 0.4 if growth >= 0 else -0.4
    alignment = "left" if growth >= 0 else "right"

    ax.text(
        growth + offset,
        bar.get_y() + bar.get_height() / 2,
        f"{growth:+.1f}%",
        ha=alignment,
        va="center",
        fontsize=12,
        fontweight="bold"
    )

# Leave space for percentage labels
ax.set_xlim(-10, 15)

# Footnote
fig.text(
    0.5,
    0.01,
    "Source: EIA U.S. Coal Consumption and Quality dataset | "
    "National sector totals | 2024–2025",
    ha="center",
    fontsize=9,
    color="gray"
)

plt.tight_layout(rect=[0, 0.04, 1, 1])

# Save for PowerPoint
plt.savefig(
    charts_folder / "04_Consumption_by_Sector_White.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white"
)

plt.show()

# ---------------------------------------------
# GRAPH 5: BURNED, BOUGHT & PAID
# U.S. Electric Power Sector (2024–2025)
# ---------------------------------------------

# Use our previously loaded national data
power = us[us["sector_name"] == "Electric Power"].copy()
power = power.set_index("year")

# Select years
data_2024 = power.loc[2024]
data_2025 = power.loc[2025]

# ---------------------------------------------
# Calculate percentage changes
# ---------------------------------------------

# Coal consumption growth
consumption_growth = (
    (data_2025["consumption_tons"] /
     data_2024["consumption_tons"]) - 1
) * 100

# Coal delivery growth
delivery_growth = (
    (data_2025["receipts_tons"] /
     data_2024["receipts_tons"]) - 1
) * 100

# Delivered price growth
price_growth = (
    (data_2025["price_usd_per_ton"] /
     data_2024["price_usd_per_ton"]) - 1
) * 100

# Estimated coal purchasing value
value_2024 = (
    data_2024["receipts_tons"] *
    data_2024["price_usd_per_ton"]
)

value_2025 = (
    data_2025["receipts_tons"] *
    data_2025["price_usd_per_ton"]
)

# Purchasing value growth
value_growth = (
    (value_2025 / value_2024) - 1
) * 100

# ---------------------------------------------
# Organize chart data
# ---------------------------------------------

labels = [
    "Coal Consumed",
    "Coal Delivered",
    "Purchasing Value",
    "Delivered Price"
]

values = [
    consumption_growth,
    delivery_growth,
    value_growth,
    price_growth
]

# Consistent presentation colors
colors = [
    "#1f4e79",  # Consumption - blue
    "#3f78a3",  # Deliveries - lighter blue
    "#287d65",  # Purchasing value - green
    "#c55a11"   # Price - orange
]

# ---------------------------------------------
# Create figure
# ---------------------------------------------

fig, ax = plt.subplots(figsize=(11, 6))

fig.patch.set_facecolor("white")
ax.set_facecolor("white")

bars = ax.barh(
    labels,
    values,
    color=colors,
    height=0.55
)

# Highest values appear at top
ax.invert_yaxis()

# Title
ax.set_title(
    "Burned, Bought & Paid",
    fontsize=20,
    fontweight="bold",
    color="#1a1a1a",
    pad=25
)

# Subtitle
ax.text(
    0.5, 1.02,
    "U.S. Electric Power Sector | 2024–2025",
    transform=ax.transAxes,
    ha="center",
    fontsize=12,
    color="#666666"
)

# Axis formatting
ax.set_xlabel(
    "Year-over-Year Change (%)",
    fontsize=12
)

ax.set_xlim(-5, 15)
ax.axvline(0, color="#333333", linewidth=1.2)

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.2
)

ax.set_axisbelow(True)

# Remove extra borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)

ax.tick_params(
    axis="both",
    labelsize=12,
    length=0,
    pad=8
)

# ---------------------------------------------
# Add percentage labels
# ---------------------------------------------

for bar, value in zip(bars, values):

    if value >= 0:
        x_position = value + 0.35
        alignment = "left"
    else:
        x_position = value - 0.35
        alignment = "right"

    ax.text(
        x_position,
        bar.get_y() + bar.get_height() / 2,
        f"{value:+.1f}%",
        ha=alignment,
        va="center",
        fontsize=13,
        fontweight="bold",
        color="#222222"
    )

# ---------------------------------------------
# Add data source and notes
# ---------------------------------------------

fig.text(
    0.5, 0.07,
    "Purchasing Value = Coal Deliveries x Average Delivered Price",
    ha="center",
    fontsize=10,
    color="#555555"
)

fig.text(
    0.5, 0.035,
    "Source: Supplied EIA U.S. Coal Consumption and Quality dataset. "
    "2025 data preliminary.",
    ha="center",
    fontsize=9,
    color="gray"
)

# Layout
plt.tight_layout(rect=[0, 0.12, 1, 0.96])

# ---------------------------------------------
# Save chart
# ---------------------------------------------

plt.savefig(
    charts_folder / "05_Burned_Bought_Paid_White.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white"
)

plt.show()

# Print values for checking
print("\nGRAPH 5 RESULTS")
print(f"Consumption growth: {consumption_growth:+.2f}%")
print(f"Delivery growth: {delivery_growth:+.2f}%")
print(f"Purchasing value growth: {value_growth:+.2f}%")
print(f"Delivered price growth: {price_growth:+.2f}%")

print(f"2024 purchasing value: ${value_2024/1e9:.2f} billion")
print(f"2025 purchasing value: ${value_2025/1e9:.2f} billion")