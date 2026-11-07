# Data Cleaning Notes: EIA U.S. Coal Consumption & Quality (2020–2025)

Full code and outputs: `notebooks/01_data_cleaning.ipynb`. The raw file in `data/raw/` is never modified.

## What we fixed

| # | Problem found | What we did |
|---|---|---|
| 1 | The data guide says volumes are in **thousands** of short tons, but the units column says **short tons**. U.S. power burn in 2020 = 435,826,849, which only makes sense as plain tons. | Treated volumes as plain short tons; added `_mm_tons` (millions) columns for slides. |
| 2 | The `heat-content` units column is mislabeled ("average sulfur percent by weight"). | Ignored the label; worked out the real units (see #3). |
| 3 | Heat content mixes **two units**: power sectors use MMBtu/short ton (~18) and industrial/coke/commercial use Btu/lb (~11,000–14,500). | Converted everything to Btu/lb (MMBtu/ton × 500). Kept `heat_mmbtu_per_ton` too. Flagged converted rows in `heat_was_converted`. |
| 4 | Impossible zeros: heat content 0 (177 rows), sulfur and ash 0 (63 each), price 0 (17). These are rows where no coal was burned or delivered. | Set to blank (NaN) so they don't pull averages down. |
| 5 | Zero consumption and zero receipts (e.g., California's power sector). | **Kept** as 0, because "no coal burned" is a real fact. |
| 6 | Stacked levels: U.S. Total, regions, and states sit in one table, and so do total and sub-sectors. Adding everything counts each ton about 3×. | Added `geo_level` and `sector_level` labels and built pre-filtered files that are safe to add up. |
| 7 | Puerto Rico appears like a state but is **not** in the U.S. Total (~1.5 M tons/yr). | Labeled PR `territory` and left it out of `states_by_sector.csv`. |
| 8 | The Pacific region appears twice: once as a total (code 90) and once split into Contiguous (PCC) and Noncontiguous (PCN). | Renamed 90 → `PAC`, labeled it `region_pacific_total`, and used PCC + PCN as the regions. |
| 9 | Blanks (missing data). | **Not filled in.** Guessing would add made-up numbers. |
| 10 | Calculated columns had long decimals (e.g., 115.10341553704336 days). | Rounded **only the columns we calculated**. Heat content keeps enough decimals that converting back gives exactly the EIA value. Original EIA columns are untouched. |

## Kept on purpose (look odd but are real)

- **Very high ash (42–48%)** in Pennsylvania and Utah independent power producer rows. These are waste-coal plants that burn leftover mining refuse, which is why their heat content is also low (~6,000 Btu/lb). Not an error.
- **One $0 price with deliveries** (Utah, Independent Power Producers, 2020) was set to blank. Its matching sub-sector row is blank too, which points to a reporting quirk rather than free coal.

## Checks that passed

Run `python verify/verify_cleaning.py data/raw/eia_coal_consumption_quality_2020_2025.csv data/clean` to rerun all 51 checks. The audit was written separately from the notebook, so it checks the cleaning independently:

- Every one of the 1,750 raw rows appears exactly once; no rows lost or added
- Consumption, deliveries and stockpiles are **identical** to the raw file
- Prices, sulfur and ash changed **only** where the raw value was exactly 0
- Converted heat content matches coal types: North Dakota lignite ~6,700 < Wyoming sub-bituminous ~8,500 < West Virginia bituminous ~12,400 Btu/lb
- Every state adds up to its own Census region (0 mismatches across 378 comparisons)

- 48 states + DC add up to the U.S. Total (0.000% difference) for every sector and year
- 10 regions add up to the U.S. Total (0.000% difference)
- Electric Utility + IPP = Electric Power, and IPP Non-CHP + IPP CHP = IPP (0 tons difference)
- No duplicate rows

## How to add things up without double-counting

- **Sectors:** add only `sector_level == "top"`: Electric Power, Other Industrial, Coke Plants, Commercial and Institutional
- **Geography:** pick one of `national`, `region`, or `state`, never mixed together

## Data limitations (for the slide)

1. **No power-sector prices in 2021.** Every power row is blank that year.
2. **Power-sector stockpiles exist only at the national level**, with no state breakdown.
3. **Price is blank in about 60% of rows**, mostly where EIA withholds data to protect individual plants.
4. **Coke plants only appear in 8 states:** AL, IL, IN, MI, OH, PA, VA, WV.
5. **Massachusetts and Vermont have no rows.** States drop out once coal use ends (e.g., Hawaii after 2022).
6. **2025 is preliminary** and may be revised.
7. **Prices are nominal** (not adjusted for inflation), and we can't adjust them because outside data isn't allowed.
8. **U.S. consumption only:** no exports, production, mine output, or company data. Coal miners that depend on exports (especially metallurgical coal) are only partly covered.
9. **Quality fields describe delivered coal**, so a row with deliveries but no burn can still carry quality values.

## New columns we added

| Column | Meaning |
|---|---|
| `receipts_minus_consumption_tons` | Positive = deliveries beat burn (stockpiling); negative = burning from stockpiles |
| `days_of_burn` | How many days year-end stockpiles would last at that year's burn rate |
| `price_usd_per_mmbtu` | Price per unit of energy, for fairly comparing low- and high-energy coal |
| `is_preliminary` | True for 2025 |
| `no_coal_burned` | True where consumption = 0 |
