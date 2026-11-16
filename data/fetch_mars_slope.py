"""
fetch_mars_slope.py: slope at the Mars target, and Earth slopes at the SAME pixel size.

Mars: MOLA (Mars Orbiter Laser Altimeter) gridded topography, MEGDR, 128 pixels per
degree (~463 m north-south), PDS Geosciences Node, no login. Where laser tracks are
far apart the grid is filled in between them, so the map is smoother than the ground.
Earth: the same Copernicus DEM GLO-30 heights as fetch_slope.py, first averaged into
blocks of about 463 m so both sides are measured at the same pixel size (coarser pixels
make slopes look gentler, so mixing 30 m and 463 m would be unfair).
Both: mean slope over a 15 km x 15 km box around the coordinate, as for Malapert.

Cite: Smith, D. E. et al. (2003), MGS MOLA MEGDR, NASA PDS, MGS-M-MOLA-5-MEGDR-L3-V1.0.
Output: data/slope_463m.csv (Earth sites and the Mars target).  Run: python3 data/fetch_mars_slope.py
"""
import math
from datetime import date

import numpy as np
import pandas as pd

import fetch_slope   # our own data/fetch_slope.py (Copernicus reader, box size)
import import_sheet  # our own data/import_sheet.py (coordinates)
import score         # our own data/score.py (paths)

MOLA = "https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg128/"
MARS_M_PER_DEG = 3396000 * math.pi / 180   # Mars radius 3396 km (MOLA label)
PIXEL_M = MARS_M_PER_DEG / 128             # ~463 m: the pixel size both sides use
BOX_KM = fetch_slope.SCORED_BOX_KM          # 15 km
OUTPUT = score.DATA_DIR / "slope_463m.csv"


def mean_slope(z, dy_m, dx_m):
    """Mean slope (degrees) of a height grid with the given pixel sizes in metres."""
    gy, gx = np.gradient(z, dy_m, dx_m)
    return float(np.nanmean(np.degrees(np.arctan(np.hypot(gx, gy)))))


def mars_slope(lat, lon):
    """Mean slope in a 15 km box on the MOLA 128 pixel/degree map (tiles of 44 x 90 degrees)."""
    east = lon % 360
    top = 88 if lat >= 44 else 44 if lat >= 0 else 0 if lat >= -44 else -44
    left = int(east // 90) * 90
    name = f"megt{abs(top):02d}{'n' if top > 0 or (top == 0 and lat >= 0) else 's'}{left:03d}hb.img"
    half_rows = math.ceil(BOX_KM * 500 / PIXEL_M)
    half_cols = math.ceil(BOX_KM * 500 / (PIXEL_M * math.cos(math.radians(lat))))
    row0, col0 = int((top - lat) * 128), int((east - left) * 128)
    raw = fetch_slope.get(MOLA + name, (row0 - half_rows) * 23040, (row0 + half_rows + 1) * 23040 - 1)
    tile = np.frombuffer(raw, ">i2").reshape(-1, 11520).astype(float)   # 16-bit heights, metres
    z = tile[:, col0 - half_cols: col0 + half_cols + 1]
    return mean_slope(z, PIXEL_M, PIXEL_M * math.cos(math.radians(lat))), MOLA + name


def earth_slope(lat, lon):
    """Mean slope in a 15 km box after averaging Copernicus heights into ~463 m blocks."""
    m_per_deg = fetch_slope.M_PER_DEG
    dlat = PIXEL_M / m_per_deg                                   # block size in degrees
    dlon = PIXEL_M / (m_per_deg * math.cos(math.radians(lat)))
    n = math.ceil(BOX_KM * 500 / PIXEL_M)
    info = fetch_slope.tile_info(fetch_slope.tile_url(math.floor(lat), math.floor(lon)))
    sub_lat, sub_lon = int(round(dlat / info["dy"])), max(1, int(round(dlon / info["dx"])))
    blocks = np.zeros((2 * n + 1, 2 * n + 1))
    for a in range(sub_lat):          # average sub_lat x sub_lon Copernicus pixels per block
        for b in range(sub_lon):
            lats = lat + (np.arange(n, -n - 1, -1) - 0.5 + (a + 0.5) / sub_lat) * dlat
            lons = lon + (np.arange(-n, n + 1) - 0.5 + (b + 0.5) / sub_lon) * dlon
            grid_lon, grid_lat = np.meshgrid(lons, lats)
            blocks += fetch_slope.height(grid_lat, grid_lon)
    return mean_slope(blocks / (sub_lat * sub_lon), PIXEL_M, PIXEL_M)


def main():
    rows = []
    sites = import_sheet.read_tab(import_sheet.SITE_OPTIONS, ["Site", "Lat", "Lon"])
    for _, s in sites.iterrows():
        value = round(earth_slope(float(s["Lat"]), float(s["Lon"])), 2)
        rows.append({"name": s["Site"], "slope_463m_deg": value, "source": "Copernicus DEM GLO-30, averaged to ~463 m"})
        print(f"  {s['Site']}: {value}°", flush=True)
    targets = import_sheet.read_targets()
    for _, t in targets[targets["Body"].str.strip() == "Mars"].iterrows():
        value, url = mars_slope(float(t["Lat"]), float(t["Lon (-180 to 180)"]))
        rows.append({"name": t["Target"], "slope_463m_deg": round(value, 2), "source": url})
        print(f"  {t['Target']}: {value:.2f}° (MOLA)", flush=True)
    out = pd.DataFrame(rows).assign(box_km=BOX_KM, pixel_m=round(PIXEL_M, 1), accessed=date.today().isoformat())
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
