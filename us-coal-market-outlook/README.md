# U.S. Coal Market Outlook

An investment outlook on the U.S. coal market and the industries exposed to it (coal producers, coal-reliant utilities, railroads, steelmakers), built only from the EIA *U.S. Coal Consumption and Quality* dataset for 2020–2025.

## Project structure

```
├── data/
│   ├── raw/                          Original EIA file (never edited)
│   └── clean/                        Cleaned data, ready for analysis
│       ├── us_by_sector.csv          ⭐ U.S. totals, 4 sectors x 6 years
│       ├── states_by_sector.csv      ⭐ 48 states + DC, 4 sectors x 6 years
│       ├── power_subsectors_us.csv   U.S. utilities vs. independent power producers
│       └── coal_clean.csv            Every row, with level labels (filter before summing)
├── notebooks/
│   └── 01_data_cleaning.ipynb        Every cleaning step, with explanations
├── verify/
│   └── verify_cleaning.py            Independent audit: 51 checks against the raw file
├── data_cleaning_notes.md            What we fixed and why, plus data limitations
└── requirements.txt
```

## How to run

```bash
pip install -r requirements.txt

# 1. Clean the data (writes data/clean/)
cd notebooks
jupyter nbconvert --to notebook --execute --inplace 01_data_cleaning.ipynb
cd ..

# 2. Audit the result (should print ALL CHECKS PASSED)
python verify/verify_cleaning.py data/raw/eia_coal_consumption_quality_2020_2025.csv data/clean
```

You can also open the notebook in Jupyter or Google Colab and run all cells.

## Which file should I use?

| Question | File |
|---|---|
| National trends by sector (consumption, prices, stockpiles) | `us_by_sector.csv` |
| Which states rely most on coal, and how that's changing | `states_by_sector.csv` |
| Utilities vs. independent power producers | `power_subsectors_us.csv` |
| Anything else (regions, Puerto Rico, sub-sectors by state) | `coal_clean.csv`, filtered to **one** `geo_level` and **one** `sector_level` first |

**The 4 top-level sectors** (these don't overlap, so they're safe to add together): Electric Power, Other Industrial, Coke Plants, Commercial and Institutional.

## Column guide

| Column | Meaning | Unit |
|---|---|---|
| `year` | Data year (2025 is preliminary) | |
| `is_preliminary` | True for 2025 | |
| `location_code` / `location_name` | State, region, or `US` | |
| `geo_level` *(coal_clean only)* | `national`, `region`, `region_pacific_total`, `state`, `territory` | |
| `sector_name` | Type of coal user | |
| `sector_group` | Short name: Power, Industrial, Coke (steel), Commercial | |
| `sector_level` / `sector_parent` *(coal_clean only)* | `top`, `sub`, `sub_sub`, and which sector it's part of | |
| `consumption_tons` | Coal burned during the year | short tons |
| `receipts_tons` | Coal delivered during the year | short tons |
| `stocks_tons` | Coal in stockpiles at year-end | short tons |
| `*_mm_tons` | Same three, in millions of tons | million short tons |
| `receipts_minus_consumption_tons` | Deliveries minus burn (positive = stockpiling) | short tons |
| `days_of_burn` | Days the year-end stockpile would last at that year's burn rate | days |
| `no_coal_burned` | True where consumption = 0 | |
| `price_usd_per_ton` | Average delivered price | $ / short ton |
| `price_usd_per_mmbtu` | Price per unit of energy (fair comparison across coal types) | $ / million Btu |
| `heat_btu_per_lb` | Energy content (fixed to one unit for all sectors) | Btu / lb |
| `heat_mmbtu_per_ton` | Same, in the other common unit | million Btu / short ton |
| `heat_was_converted` *(coal_clean only)* | True where the raw value was converted from MMBtu/ton | |
| `sulfur_pct` / `ash_pct` | Sulfur and ash share of weight | % |

**Blank = data not available, never zero.** See `data_cleaning_notes.md` for every cleaning decision and the full list of data limitations.

## Data source

U.S. Energy Information Administration (EIA), *Coal Consumption and Quality* by state and sector, 2020–2025. No outside data is used.
