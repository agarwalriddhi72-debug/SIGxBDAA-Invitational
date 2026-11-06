import pandas as pd
import matplotlib.pyplot as plt

# Load both datasets
us = pd.read_csv("us_by_sector.csv")
states = pd.read_csv("states_by_sector.csv")

# GRAPH 1: Coal consumption vs deliveries

electric = us[us["sector_name"] == "Electric Power"].sort_values("year")

plt.figure(figsize=(10, 5))

plt.plot(electric["year"], electric["consumption_mm_tons"],
         marker="o", label="Coal Consumption")

plt.plot(electric["year"], electric["receipts_mm_tons"],
         marker="o", label="Coal Deliveries")

plt.title("U.S. Electric Power: Coal Consumption vs Deliveries")
plt.xlabel("Year")
plt.ylabel("Million Short Tons")
plt.xticks(electric["year"])
plt.legend()
plt.grid(True)

plt.show()
