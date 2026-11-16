"""
read_appeears.py: turn NASA AppEEARS point-sample results into one row per site.

AppEEARS (free NASA Earthdata login) has two MODIS products the no-login service lacks:
  MYD11A1: DAILY land surface temperature, 1 km. We keep the hottest day of 2025.
           (Malapert's 47 °C is a true maximum; fetch_modis.py only has 8-day averages.)
  MCD43A3: DAILY ground brightness (white-sky shortwave albedo), 500 m. We keep the
           2025 average, to compare with Mars' TES albedo map (fetch_tes_albedo.py).

Request: AppEEARS -> Extract -> Point Sample, upload data/appeears_points.csv,
dates 2025-01-01 to 2025-12-31, layers listed in PRODUCTS below. Save each results CSV
in data/ (names end in "MYD11A1-061-results.csv" / "MCD43A3-061-results.csv").

Quality: we keep only readings whose quality number (QC) passes the check below.
MYD11A1 QC_Day: lowest 2 bits 00 = good, or 01 = produced with average error of 2 K or
less (bits 6-7 = 00 or 01). MCD43A3: 0 = full model fit, 1 = simpler fit; others dropped.
AppEEARS already applies the scale (kelvin / albedo 0-1).

Run:  python3 data/read_appeears.py MYD11A1     or     python3 data/read_appeears.py MCD43A3
"""
import sys

import pandas as pd

import import_sheet  # our own data/import_sheet.py (site names)
import score         # our own data/score.py (paths)


def lst_ok(qc):
    produced, error = qc % 4, (qc // 64) % 4  # bits 0-1, and bits 6-7
    return (produced == 0) | ((produced == 1) & (error <= 1))


PRODUCTS = {
    "MYD11A1": {"value": "_LST_Day_1km", "qc": "_QC_Day", "qc_ok": lst_ok,
                "valid": lambda v: v > 0, "convert": lambda v: (v - 273.15).round(2), "keep": "max",
                "column": "LST_day_max_c", "output": "modis_daily_lst.csv",
                "about": "MYD11A1.061 LST_Day_1km (daily, 1 km), hottest usable day of 2025"},
    "MCD43A3": {"value": "_Albedo_WSA_shortwave", "qc": "_BRDF_Albedo_Band_Mandatory_Quality_shortwave",
                "qc_ok": lambda qc: qc <= 1, "valid": lambda v: (v >= 0) & (v <= 1),
                "convert": lambda v: v, "keep": "mean",
                "column": "albedo_mean", "output": "modis_albedo.csv",
                "about": "MCD43A3.061 Albedo_WSA_shortwave (daily, 500 m), average of usable days in 2025"},
}


def find_results(product):
    """The one AppEEARS results file for this product in data/, or a clear message."""
    files = sorted(score.DATA_DIR.glob(f"*{product}-061-results.csv"))
    if len(files) != 1:
        raise SystemExit(f"Expected one *{product}-061-results.csv in data/, found {len(files)}.")
    return files[0]


def column(table, ending):
    """The one column whose name ends with `ending` (AppEEARS puts the product name in front)."""
    matches = [c for c in table.columns if c.endswith(ending)]
    if len(matches) != 1:
        raise SystemExit(f"Expected one column ending in {ending!r}, found {matches}.")
    return table[matches[0]]


def main(product):
    spec, path = PRODUCTS[product], find_results(product)
    table = pd.read_csv(path)
    values, qc = column(table, spec["value"]), column(table, spec["qc"]).fillna(255).astype(int)
    table["value"] = spec["convert"](values)
    table = table[spec["valid"](values) & spec["qc_ok"](qc)]  # drop clouds, fill values, low quality

    # AppEEARS IDs are site names with commas and spaces removed (see appeears_points.csv).
    sites = import_sheet.read_tab(import_sheet.SITE_OPTIONS, ["Site"])["Site"]
    rows = []
    for site in sites:
        days = table[table["ID"] == site.replace(",", "").replace(" ", "")]
        row = {"site": site, spec["column"]: None, "date_of_max": None, "usable_days": len(days),
               "product": spec["about"], "source_file": path.name}
        if len(days) and spec["keep"] == "max":
            best = days.loc[days["value"].idxmax()]
            row[spec["column"]], row["date_of_max"] = best["value"], best["Date"]
        elif len(days):
            row[spec["column"]] = round(days["value"].mean(), 4)
        rows.append(row)
        print(f"  {site}: {row[spec['column']]} ({len(days)} usable days)")
    pd.DataFrame(rows).to_csv(score.DATA_DIR / spec["output"], index=False)
    print(f"Wrote {spec['output']}. Not scored until import_sheet.py is switched over.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "MYD11A1")
