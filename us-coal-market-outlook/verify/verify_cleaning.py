"""Independent audit of the cleaned coal data against the raw file.
Written separately from the notebook so it doesn't share its logic."""
import sys
import numpy as np
import pandas as pd

RAW, CLEAN_DIR = sys.argv[1], sys.argv[2]
raw = pd.read_csv(RAW)
raw["location"] = raw["location"].astype(str)
clean = pd.read_csv(CLEAN_DIR + "/coal_clean.csv", dtype={"location_code": str})
ok = True

def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))

# ---------- 1. Every raw row appears exactly once ----------
c = clean.copy()
c["loc_raw"] = c["location_code"].replace({"PAC": "90"})
m = raw.merge(c, left_on=["period", "location", "sector"], right_on=["year", "loc_raw", "sector_code"],
              how="outer", indicator=True, validate="one_to_one")
check("1. row count unchanged", len(raw) == len(clean) == 1750, f"{len(raw)} raw / {len(clean)} clean")
check("1. every raw row matched to exactly one clean row", (m["_merge"] == "both").all())
check("1. names carried over correctly",
      (m["stateDescription"] == m["location_name"]).all() and (m["sectorDescription"] == m["sector_name"]).all())

def same(a, b):
    return ((a == b) | (a.isna() & b.isna())) | np.isclose(a, b, rtol=1e-12, atol=0, equal_nan=True)

# ---------- 2. Volumes untouched ----------
for r, cl in [("consumption", "consumption_tons"), ("receipts", "receipts_tons"), ("stocks", "stocks_tons")]:
    check(f"2. {cl} identical to raw", same(m[r], m[cl]).all())
for v in ["consumption", "receipts", "stocks"]:
    check(f"2. {v}_mm_tons = tons / 1e6 (3 dp)", same((m[f"{v}_tons"] / 1e6).round(3), m[f"{v}_mm_tons"]).all())

# ---------- 3. Price: only exact zeros changed ----------
changed = ~same(m["price"], m["price_usd_per_ton"])
check("3. price changed only where raw price was 0", (m.loc[changed, "price"] == 0).all() and m.loc[changed, "price_usd_per_ton"].isna().all(),
      f"{changed.sum()} cells changed")
check("3. no zero or negative prices remain", (clean["price_usd_per_ton"].dropna() > 0).all())
check("3. power-sector 2021 price was ALREADY blank in raw (not our doing)",
      raw.query("period == 2021 and sector in [1,2,3,94,98]")["price"].isna().all())

# ---------- 4. Sulfur / ash: only exact zeros changed ----------
for r, cl in [("sulfur-content", "sulfur_pct"), ("ash-content", "ash_pct")]:
    ch = ~same(m[r], m[cl])
    check(f"4. {cl} changed only where raw was 0", (m.loc[ch, r] == 0).all() and m.loc[ch, cl].isna().all(), f"{ch.sum()} cells")

# ---------- 5. Heat content conversion ----------
power = m["sector"].isin([1, 2, 3, 94, 98])
expected = np.where(m["heat-content"] == 0, np.nan, np.where(power, m["heat-content"] * 500, m["heat-content"])).round(2)
check("5. heat_btu_per_lb = raw x 500 (power) / raw (others) / blank if 0", same(pd.Series(expected), m["heat_btu_per_lb"]).all())
check("5. heat_mmbtu_per_ton = Btu/lb / 500", same((m["heat_btu_per_lb"] / 500).round(4), m["heat_mmbtu_per_ton"]).all())
check("5. power-sector MMBtu/ton exactly equals the raw EIA value", same(m.loc[power & (m["heat-content"] > 0), "heat-content"], m.loc[power & (m["heat-content"] > 0), "heat_mmbtu_per_ton"]).all())
check("5. raw power heat all < 30 and non-power all > 5000 (clean split, no borderline rows)",
      (m.loc[power & (m["heat-content"] > 0), "heat-content"] < 30).all() and
      (m.loc[~power & (m["heat-content"] > 0), "heat-content"] > 5000).all())
h = clean["heat_btu_per_lb"].dropna()
check("5. all converted heat values in the physically possible coal range (4,000-15,500 Btu/lb)",
      h.between(4000, 15500).all(), f"min {h.min():.0f}, max {h.max():.0f}")
# Coal-rank plausibility by state (power sector, 2024): lignite < sub-bituminous < bituminous
p24 = clean.query("year == 2024 and sector_name == 'Electric Power' and geo_level == 'state'").set_index("location_code")["heat_btu_per_lb"]
print(f"     ND (lignite) {p24.get('ND'):.0f} | WY/MT (sub-bit) {p24.get('WY'):.0f}/{p24.get('MT'):.0f} | "
      f"WV/KY (bituminous) {p24.get('WV'):.0f}/{p24.get('KY'):.0f} Btu/lb")
check("5. coal-rank order makes physical sense (ND < WY < WV)", p24["ND"] < p24["WY"] < p24["WV"])

# ---------- 6. Zero-heat rows really had no coal burned ----------
z = raw[raw["heat-content"] == 0]
check("6. every raw heat=0 row also had consumption=0", (z["consumption"] == 0).all(), f"{len(z)} rows")
zs = raw[raw["sulfur-content"] == 0]
check("6. every raw sulfur/ash=0 row had zero receipts or zero consumption",
      ((zs["receipts"].fillna(0) == 0) | (zs["consumption"] == 0)).all(), f"{len(zs)} rows")
zp = raw[raw["price"] == 0]
print(f"     price=0 rows: {len(zp)} total, {(zp['receipts'].fillna(0) == 0).sum()} with zero deliveries, "
      f"{(zp['receipts'] > 0).sum()} with deliveries > 0")

# ---------- 7. Geography labels ----------
geo = clean.drop_duplicates("location_code").set_index("location_code")["geo_level"]
states = set(geo[geo == "state"].index)
all50 = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
check("7. 'state' = real states + DC only", states <= all50 | {"DC"} and "DC" in states)
print(f"     states missing from file: {sorted(all50 - states)}")
DIV = {  # U.S. Census divisions (Pacific split the way EIA does it)
    "NEW": "CT ME MA NH RI VT", "MAT": "NJ NY PA", "ENC": "IL IN MI OH WI", "WNC": "IA KS MN MO NE ND SD",
    "SAT": "DE DC FL GA MD NC SC VA WV", "ESC": "AL KY MS TN", "WSC": "AR LA OK TX",
    "MTN": "AZ CO ID MT NV NM UT WY", "PCC": "CA OR WA", "PCN": "AK HI"}
st2div = {s: d for d, ss in DIV.items() for s in ss.split()}
for col in ["consumption_tons", "receipts_tons", "stocks_tons"]:
    s = clean[clean.geo_level == "state"].assign(div=lambda d: d.location_code.map(st2div))
    s_sum = s.groupby(["year", "sector_name", "div"])[col].sum(min_count=1)
    d_val = clean[clean.geo_level == "region"].set_index(["year", "sector_name", "location_code"])[col]
    d_val.index.names = ["year", "sector_name", "div"]
    j = pd.concat([s_sum, d_val], axis=1, keys=["states", "region"]).dropna()
    bad = (j["states"] - j["region"]).abs() > 1
    check(f"7. states add up to their own Census region ({col})", not bad.any(), f"{len(j)} region-sector-years compared, {bad.sum()} off")
pac = clean[clean.location_code.isin(["PCC", "PCN"])].groupby(["year", "sector_name"])["consumption_tons"].sum()
pac90 = clean[clean.location_code == "PAC"].set_index(["year", "sector_name"])["consumption_tons"]
check("7. PAC (code 90) = PCC + PCN", ((pac.reindex(pac90.index) - pac90).abs() < 1).all())

for col in ["consumption_tons", "receipts_tons", "stocks_tons"]:
    nat = clean[clean.geo_level == "national"].set_index(["year", "sector_name"])[col]
    for lvl in ["state", "region"]:
        parts = clean[clean.geo_level == lvl].groupby(["year", "sector_name"])[col].sum(min_count=1)
        j = pd.concat([parts, nat], axis=1, keys=["p", "n"]).dropna()
        diff = ((j.p - j.n).abs() / j.n.replace(0, np.nan)).max() * 100
        check(f"7. {lvl}s add up to U.S. Total ({col})", (j.p - j.n).abs().max() <= 1, f"max diff {diff:.4f}%")

# ---------- 8. Sector labels ----------
lv = clean.drop_duplicates("sector_code").set_index("sector_name")["sector_level"].to_dict()
check("8. top sectors are the 4 non-overlapping ones",
      {k for k, v in lv.items() if v == "top"} == {"Electric Power", "Other Industrial", "Coke Plants", "Commercial and Institutional"})
for col in ["consumption_tons", "receipts_tons", "stocks_tons"]:
    p = clean.pivot_table(index=["year", "location_code"], columns="sector_name", values=col)
    g1 = (p["Electric Utility"].fillna(0) + p["Independent Power Producers"].fillna(0) - p["Electric Power"]).abs().max()
    g2 = (p["IPP Non-CHP"].fillna(0) + p["IPP CHP"].fillna(0) - p["Independent Power Producers"]).abs().max()
    check(f"8. sub-sectors add up to parents ({col})", g1 <= 1 and g2 <= 1, f"gaps {g1:.0f}, {g2:.0f} tons")

# ---------- 9. Derived columns recomputed independently ----------
rc = (clean["receipts_tons"] - clean["consumption_tons"]).round(2)
check("9. receipts_minus_consumption correct", same(rc, clean["receipts_minus_consumption_tons"]).all())
dob = np.where(clean["consumption_tons"] > 0, clean["stocks_tons"] / (clean["consumption_tons"] / 365), np.nan)
check("9. days_of_burn correct", same(pd.Series(dob).round(1), clean["days_of_burn"]).all())
ppm = (clean["price_usd_per_ton"] / clean["heat_mmbtu_per_ton"]).round(3)
check("9. price_per_mmbtu correct", same(ppm, clean["price_usd_per_mmbtu"]).all())
check("9. is_preliminary only for 2025", (clean["is_preliminary"] == (clean["year"] == 2025)).all())
check("9. no_coal_burned matches consumption == 0", (clean["no_coal_burned"] == (clean["consumption_tons"] == 0)).all())
us = clean.query("location_code == 'US' and sector_name == 'Electric Power'").set_index("year")
print("     U.S. power days of burn:", us["days_of_burn"].round(0).to_dict())
print("     U.S. power $/MMBtu:", us["price_usd_per_mmbtu"].round(2).to_dict())

# ---------- 10. Convenience files are exact filters of coal_clean ----------
files = {"us_by_sector": "geo_level == 'national' and sector_level == 'top'",
         "states_by_sector": "geo_level == 'state' and sector_level == 'top'",
         "power_subsectors_us": "geo_level == 'national' and sector_level == 'sub'"}
for f, q in files.items():
    sub = pd.read_csv(f"{CLEAN_DIR}/{f}.csv", dtype={"location_code": str}).reset_index(drop=True)
    exp = clean.query(q).reset_index(drop=True)[sub.columns] if set(sub.columns) <= set(clean.columns) else None
    vals_equal = exp is not None and sub.shape == exp.shape and all(((sub[k] == exp[k]) | (sub[k].isna() & exp[k].isna())).all() for k in sub.columns)
    check(f"10. {f}.csv values equal the filter of coal_clean.csv", vals_equal, f"{sub.shape[0]} rows x {sub.shape[1]} cols")
    check(f"10. {f}.csv has one row per year/location/sector (safe to sum)", not sub.duplicated(["year", "location_code", "sector_name"]).any())
u = pd.read_csv(CLEAN_DIR + "/us_by_sector.csv")
check("10. us_by_sector has exactly 4 sectors x 6 years, all U.S.", len(u) == 24 and (u["location_code"] == "US").all() and u["sector_name"].nunique() == 4)
st = pd.read_csv(CLEAN_DIR + "/states_by_sector.csv")
check("10. states_by_sector has only the 4 top sectors and 49 locations (48 states + DC)", st["sector_name"].nunique() == 4 and st["location_code"].nunique() == 49 and "Electric Utility" not in st["sector_name"].values)
check("10. Puerto Rico not in states_by_sector", "PR" not in pd.read_csv(CLEAN_DIR + "/states_by_sector.csv")["location_code"].values)

print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
