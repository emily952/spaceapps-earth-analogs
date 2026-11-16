"""
import_sheet.py: turn the research Google Sheet exports into data/sites.csv.

Inputs (export each tab of the research sheet as CSV into data/):
  site_options.csv -> one "earth" row per site
  targets.csv      -> one moon_target / mars_target row per target. Rows with
                      "(reference)" in the name are skipped here; the gap page uses them.
Output: data/sites.csv, which score.py and build.py read.

Text is copied word for word. The scoring columns (slope_deg, temp_max_c, ...) are
only filled from sheet columns with exactly those names, holding plain numbers.
We never pull numbers out of text like "<30" or "80.8 (surface, MODIS)": that
would be guessing.

build.py runs this automatically. Don't edit sites.csv by hand: edit the Sheet,
re-export the tabs, and run build.py again.
"""
import pandas as pd

import score      # our own data/score.py (for the scoring column names and paths)
import sun_angle  # our own data/sun_angle.py (calculated from latitude)

SITE_OPTIONS = score.DATA_DIR / "site_options.csv"
TARGETS = score.DATA_DIR / "targets.csv"

# Our column name -> the Sheet's column header, for each tab.
SITE_COLUMNS = {
    "name": "Site", "lat": "Lat", "lon": "Lon", "category": "Category",
    "analog_for": "Analog for", "mission_tasks": "Suggested mission tasks",
    "matches": "Strong matches", "breaks": "Where it breaks", "key_facts": "Key facts",
    "geology": "Geology and minerals", "how_well_studied": "How well studied (est.)",
    "source_links": "Source URLs (plain text)",
}
TARGET_COLUMNS = {
    "name": "Target", "lat": "Lat", "lon": "Lon (-180 to 180)", "key_facts": "Why it matters",
    "geology": "Terrain", "matches": "Earth sites that match parts of it (suggested)",
    "source_links": "Source URLs (plain text)",
}
# Scoring values that come from somewhere other than an exact-name Sheet column.
# Each must be the same kind of number as the column: max ground (skin) temperature.
TARGET_SCORE_COLUMNS = {"temp_max_c": "Max ground surface temp (°C)",  # LRO Diviner, entered by the team
                        "slope_deg": "Landing-area slope (°)"}         # Wueller et al. 2025, entered by the team
# Scoring values made by our download scripts: (our column, file in data/, name column,
# value column, script that makes the file). Rows not in a file stay blank ("no data").
# Not scored, kept for reference: modis_daily_lst.csv (daily MODIS, 1 km) and modis_lst.csv (8-day MODIS).
DOWNLOADED = [
    # Team decision: max = highest HOURLY ground (skin) temperature reported by the dataset in its period.
    ("temp_max_c", "power_skin_temps.csv", "site", "TS_MAX_annual_c", "fetch_power.py"),     # NASA POWER TS_MAX
    ("slope_deg", "copernicus_slope.csv", "site", "slope_mean_15km", "fetch_slope.py"),       # Copernicus 30 m, 15 km box
    ("slope_463m_deg", "slope_463m.csv", "name", "slope_463m_deg", "fetch_mars_slope.py"),     # Earth + Mars at 463 m
    ("dust_aod", "dust_aod.csv", "site", "aod_55_annual", "fetch_dust.py"),                     # Earth: NASA POWER AOD_55
    ("dust_aod", "mars_dust.csv", "target", "dust_visible_mean", "fetch_dust.py"),              # Mars: LMD climatology
]

# Sheet columns shown together as "Climate and conditions" notes, word for word.
SITE_NOTES = ["Elevation (m)", "Mean annual temp (°C)", "Extreme temp (°C)", "Precip (mm/yr)"]
TARGET_NOTES = ["Gravity (m/s²)", "Surface pressure", "Surface temperature", "Ice and water"]

# Column order of the finished sites.csv.
OUTPUT_COLUMNS = (["name", "type", "lat", "lon"] + list(score.DIMENSIONS) +
                  ["matches", "breaks", "source_links", "category", "analog_for", "mission_tasks",
                   "key_facts", "climate_notes", "geology", "how_well_studied"])


def read_tab(path, needed):
    """Read one exported tab and check it has the columns we need."""
    if not path.exists():
        raise FileNotFoundError(f"Missing {path.name}: export that tab of the research sheet into data/")
    tab = pd.read_csv(path, dtype=str)  # keep every cell as text, exactly as typed
    tab.columns = tab.columns.str.strip()
    missing = [col for col in needed if col not in tab.columns]
    if missing:
        raise ValueError(f"{path.name} is missing column(s) {missing}. Did a header change in the Sheet?")
    return tab.dropna(how="all")  # drop fully empty rows


def join_notes(row, note_columns):
    """One line per non-blank cell, labelled with its Sheet header."""
    return "\n".join(f"{col}: {str(row[col]).strip()}" for col in note_columns
                     if not pd.isna(row[col]) and str(row[col]).strip())


def convert(tab, column_map, note_columns):
    """Rename the Sheet's columns to ours and add the notes and scoring columns."""
    out = pd.DataFrame({ours: tab[theirs] for ours, theirs in column_map.items()})
    out["climate_notes"] = [join_notes(row, note_columns) for _, row in tab.iterrows()]
    # Scoring columns: only from Sheet columns with exactly our names, else blank (no data).
    for col in score.DIMENSIONS:
        out[col] = tab[col] if col in tab.columns else None
    return out


def read_targets():
    """The Targets tab, checked for every column we use (including scoring columns)."""
    return read_tab(TARGETS, list(TARGET_COLUMNS.values()) + TARGET_NOTES + ["Body"]
                    + list(TARGET_SCORE_COLUMNS.values()))


def reference_rows():
    """Target rows marked '(reference)': used on the gap page, never scored."""
    targets = read_targets()
    return targets[targets["Target"].str.contains("(reference)", regex=False)]


def add_downloaded(rows):
    """Fill scoring columns from the files our download scripts made (see DOWNLOADED)."""
    for column, file_name, key, value, script in DOWNLOADED:
        path = score.DATA_DIR / file_name
        if not path.exists():
            print(f"  No data/{file_name}: run data/{script} to score {column}.")
            continue
        table = pd.read_csv(path)
        if "mars_year" in table:  # mars_dust.csv: use the average of all Mars Years
            table = table[table["mars_year"] == "ALL"]
        found = rows["name"].map(table.set_index(key)[value])
        rows[column] = found.where(found.notna(), rows.get(column))  # keep Sheet values where a file has none
    return rows


def main():
    sites = convert(read_tab(SITE_OPTIONS, list(SITE_COLUMNS.values()) + SITE_NOTES),
                    SITE_COLUMNS, SITE_NOTES)
    sites["type"] = "earth"

    targets = read_targets()
    targets = targets[~targets["Target"].str.contains("(reference)", regex=False)]
    target_rows = convert(targets, TARGET_COLUMNS, TARGET_NOTES)
    for ours, theirs in TARGET_SCORE_COLUMNS.items():
        target_rows[ours] = targets[theirs]  # must be a plain number or blank; load_sites checks
    # "Moon" -> moon_target, "Mars" -> mars_target. Anything else is caught by score.load_sites.
    target_rows["type"] = targets["Body"].str.strip().str.lower() + "_target"
    target_rows["category"] = "Target"

    combined = add_downloaded(pd.concat([sites, target_rows], ignore_index=True))
    combined = sun_angle.add_column(combined)[OUTPUT_COLUMNS]  # highest Sun angle, from latitude
    combined.to_csv(score.SITES_CSV, index=False)
    print(f"  Wrote data/sites.csv ({len(sites)} Earth sites, {len(target_rows)} targets)")


if __name__ == "__main__":
    main()
