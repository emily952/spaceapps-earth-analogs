"""
read_appeears.py: hottest DAILY MODIS land surface temperature per site, from an AppEEARS file.

Why: Malapert's 47 °C is a true maximum (LRO Diviner). The no-login service only has
8-day averages (fetch_modis.py), which sit a few degrees below the true peak. NASA
AppEEARS (free Earthdata login) has the daily product, MYD11A1.

Before running: submit an AppEEARS "Point Sample" request with data/appeears_points.csv,
dates 2025-01-01 to 2025-12-31, product MYD11A1.061, layers LST_Day_1km and QC_Day.
Save the results CSV in data/ (its name ends in "MYD11A1-061-results.csv").

Quality: each daily reading has a QC_Day number. Its lowest 2 bits say whether the
value was produced (00 = good, 01 = produced, check bits 6-7); bits 6-7 give the
average error (00 = 1 K or less, 01 = 2 K or less). We keep good readings, plus
"produced" readings with an error of 2 K or less. AppEEARS already gives kelvin;
0 means "no reading" (cloud).

Output: data/modis_daily_lst.csv (one row per site).
Run:  python3 data/read_appeears.py
"""
import pandas as pd

import import_sheet  # our own data/import_sheet.py (site names and coordinates)
import score         # our own data/score.py (for paths)

OUTPUT = score.DATA_DIR / "modis_daily_lst.csv"


def find_results():
    """The AppEEARS results file in data/. Stops with a clear message if there isn't exactly one."""
    files = sorted(score.DATA_DIR.glob("*MYD11A1-061-results.csv"))
    if len(files) != 1:
        raise SystemExit(f"Expected one *MYD11A1-061-results.csv in data/, found {len(files)}.")
    return files[0]


def column(table, ending):
    """The one column whose name ends with `ending` (AppEEARS adds the product name in front)."""
    matches = [c for c in table.columns if c.endswith(ending)]
    if len(matches) != 1:
        raise SystemExit(f"Expected one column ending in {ending!r}, found {matches}.")
    return table[matches[0]]


def usable(qc):
    """True for good-quality readings, or produced readings with average error of 2 K or less."""
    qc = qc.fillna(255).astype(int)
    produced, error = qc % 4, (qc // 64) % 4  # bits 0-1, and bits 6-7
    return (produced == 0) | ((produced == 1) & (error <= 1))


def main():
    path = find_results()
    table = pd.read_csv(path)
    kelvin, qc = column(table, "_LST_Day_1km"), column(table, "_QC_Day")
    table["lst_c"] = (kelvin - 273.15).round(2)
    table = table[(kelvin > 0) & usable(qc)]  # drop cloudy days and low-quality readings

    # AppEEARS IDs are site names with commas and spaces removed (see appeears_points.csv).
    sites = import_sheet.read_tab(import_sheet.SITE_OPTIONS, ["Site"])["Site"]
    id_to_site = {s.replace(",", "").replace(" ", ""): s for s in sites}
    rows = []
    for site_id, site in id_to_site.items():
        days = table[table["ID"] == site_id]
        hottest = days.loc[days["lst_c"].idxmax()] if len(days) else None
        rows.append({"site": site, "LST_day_max_c": None if hottest is None else hottest["lst_c"],
                     "date_of_max": None if hottest is None else hottest["Date"],
                     "usable_days": len(days), "product": "MYD11A1.061 LST_Day_1km (daily, 1 km), 2025",
                     "source_file": path.name})
        print(f"  {site}: max {rows[-1]['LST_day_max_c']} °C on {rows[-1]['date_of_max']} "
              f"({len(days)} usable days)")
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT.name}. Nothing is scored from it until import_sheet.py is switched over.")


if __name__ == "__main__":
    main()
