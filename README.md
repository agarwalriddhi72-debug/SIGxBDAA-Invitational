# The Coal Bank: Is America's Coal Comeback Real?

U.S. coal market outlook, 2020-2025, built **only** from the provided U.S. Coal Consumption and Quality dataset (EIA) for the **SIG x BDAA Invitational (Beginner Track)**. No outside data, financial statements, or stock prices were used.

> **"America's coal comeback might be running on its savings."**

---

## Executive Summary

Electric power coal consumption rose **11.3%** from 2024 to 2025, but deliveries rose only **7.3%**. Inventories declined **14.2%**, and average delivered prices fell **1.9%**. This suggests the recovery is partly supported by existing stockpiles rather than equally strong new purchasing activity.

**Recommendation: UNDERWEIGHT U.S. thermal coal over the next 18-24 months**, while monitoring selective opportunities from potential inventory replenishment.

- **Short term:** invest little.
- **Longer term:** watch deliveries. If they rise, increase exposure.

## The Idea

We treat the coal market like a bank account:

| Bank term | Dataset measure |
|---|---|
| Deposits | Deliveries (receipts) |
| Withdrawals | Consumption |
| Savings | Stockpiles (stocks) |

The question: is more coal being burned because more coal is being bought, or because plants are spending their savings?

## Full Thesis

Although U.S. coal consumption rebounded in 2025, the recovery masks underlying weakness in coal purchasing activity and pricing. Electric power coal consumption increased 11.3%, yet deliveries rose only 7.3%, inventories declined 14.2%, and average delivered prices fell 1.9%. This divergence suggests that the rebound was partly supported by previously accumulated coal stockpiles rather than proportionate growth in new purchases.

We recommend underweighting broad U.S. thermal coal exposure over the next 18-24 months, as the current recovery has not demonstrated sustained purchasing growth or pricing strength. However, declining inventories create a potential short-term opportunity for coal suppliers and transportation providers if utilities increase deliveries to replenish stockpiles.

## Key Numbers (Electric Power, 2024 to 2025)

| Metric | Change |
|---|---|
| Coal consumption | **+11.3%** |
| Coal deliveries | **+7.3%** |
| Coal stockpiles | **-14.2%** |
| Average delivered price | **-1.9%** |

## Coal Recovery Reality Matrix

Each state is placed in one of four groups based on its 2024 to 2025 change in consumption and deliveries (all sectors combined):

| Group | Consumption | Deliveries | States |
|---|---|---|---|
| Real Recovery | Up | Up | 25 |
| Phantom Recovery | Up | Down | 8 |
| Contraction | Down | Down | 6 |
| Inventory Building | Down | Up | 2 |

41 states have usable data for both years. The labels describe consumption and delivery trends. They are **not** proven changes in state-level inventories or company profits.

## Charts

| # | Chart | What it shows |
|---|---|---|
| 1 | Burned vs. Bought | National consumption vs. deliveries, 2020-2025 |
| 2 | The Coal Bank Balance | National stockpiles and days of inventory coverage, 2020-2025 |
| 3 | Coal Recovery Reality Matrix | State consumption growth vs. delivery growth, 2024-2025 |
| 4 | One Coal Market, Different Futures | Consumption growth by sector, 2024-2025 |
| 5 | Burned, Bought & Paid | Changes in consumption, deliveries, delivered prices, and estimated purchasing value |
| 6 | Coal Quality & Pricing | Heat content, sulfur, ash, and delivered price by sector, 2020-2025 |

## Repository Contents

```
.
├── data/
│   ├── Coal_analysis_Raw_data_.csv      # provided dataset, unmodified
│   ├── states_by_sector.csv             # cleaned: state x sector x year
│   └── us_by_sector.csv                 # cleaned: U.S. total x sector x year
├── chart3_recovery_matrix_white.py      # Coal Recovery Reality Matrix
├── chart6_quality_pricing.py            # Coal Quality & Pricing
└── README.md
```

Add the remaining chart scripts to this list as they are finished.

## Data Cleaning

All cleaning is done on the provided dataset only:

- Dropped constant unit columns. One of them, `heat-content-units`, was mislabeled as sulfur units.
- Converted heat content to one unit. Electric sectors were in million Btu per short ton, while other sectors were in Btu per pound.
- Replaced zeros that meant "no coal burned" with missing values for quality and price fields.
- Separated state rows from regional rows and the U.S. total, to avoid double counting.
- Rolled the electric power sub-sectors (utility, IPP non-CHP, IPP CHP) into one **Electric Power** sector. The result is four sectors: Electric Power, Other Industrial, Coke Plants, and Commercial and Institutional.
- Excluded Puerto Rico, since it is a territory and not a state.
- Added derived columns: consumption in millions of tons, receipts minus consumption, days of burn, and price per million Btu.

## How to Run

1. Install Python 3.9 or newer.
2. Install the packages:
   ```
   pip install pandas matplotlib
   ```
3. Put the cleaned CSVs in the same folder as the scripts, or edit the file paths at the top of each script.
4. Run any chart script, for example:
   ```
   python chart3_recovery_matrix_white.py
   ```
   Each script displays the chart, saves a PNG, and prints a short summary in the terminal.

## Limitations

- **The dataset covers U.S. use only.** It has no exports, mining output, company financials, or prices of any traded securities, so it cannot measure producer profits directly.
- **2025 is marked preliminary** in the data and may be revised.
- **Stockpile figures are missing for most state-level electric power rows,** so state-level inventory changes are inferred from consumption and deliveries, not observed.
- **Short comparison window.** Headline numbers compare 2024 to 2025. We use 2020-2025 to check whether the pattern is a trend or one year of noise.
- **Small states can look extreme.** Percentage changes for states with little coal use can swing sharply on small tonnage changes.
- **Missing data.** Price is missing for many state and sector rows, and the U.S. Electric Power price is missing for 2021.

## Team

SIG x BDAA Invitational, Beginner Track. Add team member names here.

## Tools Used

Python, pandas, matplotlib, Jupyter, VS Code.