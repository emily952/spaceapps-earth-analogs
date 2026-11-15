"""
score.py: turn data/sites.csv into 0-to-1 similarity scores.

For every Earth site, every target (Moon or Mars), and every dimension
(slope, temperatures, rain, dust) SEPARATELY, we compute:

    score = 1 - |earth_value - target_value| / (column max - column min)

1 = same value as the target, 0 = as different as anything in the dataset.
The column max and min are taken across ALL rows (Earth sites and targets).
A blank cell means "no data": the score is left blank, never guessed.
We never combine dimensions into one overall number.

Run on its own:  python3 data/score.py   -> writes data/scores.csv
build.py also imports this file, so normally you just run build.py.
"""
import re
from pathlib import Path

import pandas as pd

# Paths are relative to this file, so the script works from any folder.
DATA_DIR = Path(__file__).resolve().parent
SITES_CSV = DATA_DIR / "sites.csv"
SCORES_CSV = DATA_DIR / "scores.csv"

# The columns we score, mapped to the label shown in charts and tables.
DIMENSIONS = {
    "slope_deg": "Slope",
    "temp_max_c": "Max temperature",
    "temp_min_c": "Min temperature",
    "temp_range_c": "Temperature range",
    "precip_mm_yr": "Precipitation",
    "dust_aod": "Dust (AOD)",
}

# The only values allowed in the "type" column.
TARGET_TYPES = ["moon_target", "mars_target"]
ALLOWED_TYPES = ["earth"] + TARGET_TYPES


def load_sites(path=SITES_CSV):
    """Read the CSV and check it, so mistakes fail loudly instead of silently."""
    # Blank cells become NaN, which pandas uses to mean "no data".
    sites = pd.read_csv(path)
    sites["type"] = sites["type"].str.strip()

    # Stop if a row has a type we don't know (for example a typo like "mars").
    bad_types = sites.loc[~sites["type"].isin(ALLOWED_TYPES), "type"]
    if not bad_types.empty:
        raise ValueError(f"Unknown type(s) in sites.csv: {sorted(set(bad_types))}. "
                         f"Allowed: {ALLOWED_TYPES}")

    # Make sure number columns hold numbers. Text like "approx 5" stops the
    # script with an error, so nobody's typo turns into a fake value.
    for column in ["lat", "lon"] + list(DIMENSIONS):
        try:
            sites[column] = pd.to_numeric(sites[column])
        except ValueError as err:
            raise ValueError(f"Column '{column}' has a non-number value: {err}") from err
    return sites


def split_links(cell):
    """Split a source_links cell into a list. Links are separated by ; or line breaks."""
    if pd.isna(cell):
        return []
    return [link.strip() for link in re.split(r"[;\n]+", str(cell)) if link.strip()]


# Link addresses that usually need a login, so they break the "public links only" rule.
PRIVATE_HINTS = ["docs.google.com", "drive.google.com", "localhost", "file:"]


def check_sites(sites):
    """List problems to fix before submitting. These are warnings, not errors."""
    warnings = []
    for _, row in sites.iterrows():
        name = row["name"]
        if "FAKE" in str(name).upper():
            warnings.append(f"{name}: FAKE test row. Replace it with real data.")
        links = split_links(row["source_links"])
        # Rule: every source cited.
        if not links:
            warnings.append(f"{name}: no source_links. Every source must be cited.")
        # Rule: public links only.
        for link in links:
            if not link.startswith(("http://", "https://")):
                warnings.append(f"{name}: '{link}' is not a web link.")
            elif " " in link:
                warnings.append(f"{name}: '{link}' contains a space. Separate links with ;")
            elif any(hint in link for hint in PRIVATE_HINTS):
                warnings.append(f"{name}: '{link}' may need a login. Links must be public.")
    return warnings


def score_one(earth_value, target_value, spread):
    """Score one dimension for one Earth site against one target."""
    # Either side blank means we have no data, so no score.
    if pd.isna(earth_value) or pd.isna(target_value):
        return None
    # If every row has the same value, the two values must be identical.
    if spread == 0:
        return 1.0
    score = 1 - abs(earth_value - target_value) / spread
    # Clip to the 0..1 range, as the scoring rules say.
    return min(max(score, 0.0), 1.0)


def compute_scores(sites):
    """Return a table with one row per (Earth site, target) pair."""
    # Spread of each column = max minus min across all rows (blanks ignored).
    spreads = {col: sites[col].max() - sites[col].min() for col in DIMENSIONS}

    earth_sites = sites[sites["type"] == "earth"]
    targets = sites[sites["type"].isin(TARGET_TYPES)]

    rows = []
    for _, site in earth_sites.iterrows():
        for _, target in targets.iterrows():
            row = {"site": site["name"], "target": target["name"],
                   "target_type": target["type"]}
            # Each dimension gets its own score; they are never added together.
            for col in DIMENSIONS:
                row[col] = score_one(site[col], target[col], spreads[col])
            rows.append(row)

    scores = pd.DataFrame(rows, columns=["site", "target", "target_type"] + list(DIMENSIONS))
    # Round so the CSV is easy to read; blanks stay blank.
    return scores.round(3)


if __name__ == "__main__":
    # Only runs when you call "python3 data/score.py" directly.
    scores = compute_scores(load_sites())
    scores.to_csv(SCORES_CSV, index=False)
    print(f"Wrote {len(scores)} score rows to {SCORES_CSV}")
    print(scores.to_string(index=False, na_rep="no data"))
