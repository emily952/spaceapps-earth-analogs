"""
fetch_tes_albedo.py: Arcadia Planitia's ground brightness (albedo) from NASA's TES map.

Source: Mars Global Surveyor Thermal Emission Spectrometer (TES) global bolometric
albedo map, 8 pixels per degree (about 7.4 km per pixel), PDS Geosciences Node.
Albedo = share of sunlight reflected (0 = black, 1 = white), across sunlight's whole
range (0.3 to 2.9 micrometres). Not corrected for dust in the air (Christensen et al. 2001).
Earth's comparable number is MODIS white-sky shortwave albedo (read_appeears.py).

The map is one big grid of 32-bit numbers, row by row from 90°N, starting at 180°W.
We download only the one row that holds the target, not the whole 16 MB file.

Cite as: Christensen, P. R. et al. (2001), Mars Global Surveyor Thermal Emission
Spectrometer experiment, J. Geophys. Res. 106(E10), doi:10.1029/2000JE001370.
Output: data/mars_albedo.csv.   Run:  python3 data/fetch_tes_albedo.py
"""
import struct
import urllib.request
from datetime import date

import pandas as pd

import import_sheet  # our own data/import_sheet.py (target coordinates)
import score         # our own data/score.py (paths)

URL = "https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-special-v1/global_albedo_8ppd.img"
LABEL = "https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-special-v1/global_albedo_8ppd.lbl"
PIXELS_PER_DEGREE, SAMPLES = 8, 2880   # from the .lbl file
ROW_BYTES = SAMPLES * 4                # 4 bytes per number
OUTPUT = score.DATA_DIR / "mars_albedo.csv"


def albedo_at(lat, lon):
    """The one map pixel at lat/lon (one point, as the team decided)."""
    row, col = int((90 - lat) * PIXELS_PER_DEGREE), int((lon + 180) * PIXELS_PER_DEGREE)
    request = urllib.request.Request(URL, headers={"Range": f"bytes={row * ROW_BYTES}-{(row + 1) * ROW_BYTES - 1}",
                                                   "User-Agent": "earth-analogs-script"})
    with urllib.request.urlopen(request, timeout=60) as response:
        values = struct.unpack(f"<{SAMPLES}f", response.read())  # "<f" = little-endian 32-bit (PC_REAL)
    return round(values[col], 4), row, col


def main():
    targets = import_sheet.read_targets()
    mars = targets[targets["Body"].str.strip() == "Mars"]
    rows = []
    for _, t in mars.iterrows():
        value, row, col = albedo_at(float(t["Lat"]), float(t["Lon (-180 to 180)"]))
        rows.append({"target": t["Target"], "lat": t["Lat"], "lon": t["Lon (-180 to 180)"],
                     "albedo": value, "map_row": row, "map_column": col, "source_url": URL,
                     "label_url": LABEL, "product": "MGS TES global bolometric albedo, 8 pixels/degree",
                     "accessed": date.today().isoformat()})
        print(f"  {t['Target']}: albedo {value} (map row {row}, column {col})")
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
