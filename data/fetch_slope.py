"""
fetch_slope.py: average ground slope around each Earth site, from Copernicus DEM GLO-30.

Why this DEM: covers all 12 sites (SRTM misses Haughton and Antarctica). ~30 m pixels
(wider east-west near the poles). A surface model: includes buildings/plants (rare here).

Area: a 15 km x 15 km box. Malapert's 5.6° ± 2.0° is for a landing AREA with ~1,250 m of
relief (Wueller et al. 2025), which needs ~13 km at 5.6°; NASA release 22-089 (Aug 2022):
"Each region is approximately ... 15 by 15 kilometers" (a landing SITE is ~100 m radius).
We also save 1 km and 5 km boxes so the team can see how much the size matters.

Data: free on AWS (no login), Cloud-Optimised GeoTIFFs. We download only the 1024 x 1024
blocks we need and unpack them ourselves (zlib + "floating point predictor"; numpy only).

Cite: Copernicus DEM GLO-30, ESA/EU, doi:10.5270/ESA-c5d3d65. Output: data/copernicus_slope.csv.
"""
import math
import struct
import time
import urllib.request
import zlib
from datetime import date

import numpy as np
import pandas as pd

import import_sheet  # our own data/import_sheet.py (site coordinates)
import score         # our own data/score.py (paths)

BUCKET = "https://copernicus-dem-30m.s3.amazonaws.com"
BOX_KM = [1, 5, 15]   # box sizes we compute; 15 km is the one we score
SCORED_BOX_KM = 15
M_PER_DEG = 6371008.8 * math.pi / 180  # metres per degree of latitude (mean Earth radius)
OUTPUT = score.DATA_DIR / "copernicus_slope.csv"
_tiles, _blocks = {}, {}  # downloaded tile headers and blocks, so nothing is fetched twice


def get(url, start, end, tries=4):
    """Download bytes start..end of a file (an HTTP Range request). Retries if the connection drops."""
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}", "User-Agent": "earth-analogs-script"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                return response.read()
        except OSError:
            if attempt == tries - 1:
                raise
            time.sleep(5 * (attempt + 1))  # wait a little longer each time


def tile_url(lat_floor, lon_floor):
    ns, ew = ("N" if lat_floor >= 0 else "S"), ("E" if lon_floor >= 0 else "W")
    name = f"Copernicus_DSM_COG_10_{ns}{abs(lat_floor):02d}_00_{ew}{abs(lon_floor):03d}_00_DEM"
    return f"{BUCKET}/{name}/{name}.tif"


def tile_info(url):
    """Read a tile's TIFF header: size, block size, where each block is, and pixel spacing."""
    if url not in _tiles:
        head = get(url, 0, 65535)
        tags = {}
        offset = struct.unpack("<I", head[4:8])[0]
        for i in range(struct.unpack("<H", head[offset:offset + 2])[0]):
            tag, kind, count, value = struct.unpack("<HHI4s", head[offset + 2 + 12 * i: offset + 14 + 12 * i])
            fmt = {3: "H", 4: "I", 12: "d"}.get(kind)
            if fmt is None:
                continue
            size = struct.calcsize(fmt) * count
            raw = value[:size] if size <= 4 else head[struct.unpack("<I", value)[0]:][:size]
            tags[tag] = struct.unpack(f"<{count}{fmt}", raw)
        _tiles[url] = {"width": tags[256][0], "height": tags[257][0], "block": tags[322][0],
                       "offsets": tags[324], "lengths": tags[325], "dx": tags[33550][0], "dy": tags[33550][1]}
    return _tiles[url]


def block(url, index):
    """One 1024 x 1024 block of heights (metres), unpacked."""
    if (url, index) not in _blocks:
        info = tile_info(url)
        start = info["offsets"][index]
        raw = zlib.decompress(get(url, start, start + info["lengths"][index] - 1))
        n = info["block"]
        # Floating point predictor: each row stores byte 1 of every pixel, then byte 2, ...,
        # each as differences from the previous byte. Undo the differences, then regroup.
        rows = np.cumsum(np.frombuffer(raw, np.uint8).reshape(n, 4 * n), axis=1, dtype=np.uint8)
        _blocks[(url, index)] = rows.reshape(n, 4, n).transpose(0, 2, 1).copy().view(">f4")[:, :, 0]
    return _blocks[(url, index)]


def height(lat, lon):
    """Heights for arrays of points (any tiles). Missing tiles stop the script loudly."""
    out = np.full(lat.shape, np.nan)
    lat_f, lon_f = np.floor(lat).astype(int), np.floor(lon).astype(int)
    for la, lo in set(zip(lat_f.ravel(), lon_f.ravel())):
        url, here = tile_url(la, lo), (lat_f == la) & (lon_f == lo)
        info = tile_info(url)
        row = ((la + 1 - lat[here]) / info["dy"]).astype(int).clip(0, info["height"] - 1)
        col = ((lon[here] - lo) / info["dx"]).astype(int).clip(0, info["width"] - 1)
        per_row = math.ceil(info["width"] / info["block"])
        index = (row // info["block"]) * per_row + col // info["block"]
        values = np.empty(row.shape)
        for i in np.unique(index):
            pick = index == i
            values[pick] = block(url, i)[row[pick] % info["block"], col[pick] % info["block"]]
        out[here] = values
    return out


def slope_stats(lat0, lon0):
    """Mean and spread of slope (degrees), and relief (m), in boxes of each size in BOX_KM."""
    info = tile_info(tile_url(math.floor(lat0), math.floor(lon0)))
    half = max(BOX_KM) / 2 * 1000 + 100  # metres, plus a margin for the slope at the edges
    dlat, dlon = half / M_PER_DEG, half / (M_PER_DEG * math.cos(math.radians(lat0)))
    lats = np.arange(lat0 + dlat, lat0 - dlat, -info["dy"])
    lons = np.arange(lon0 - dlon, lon0 + dlon, info["dx"])
    grid_lon, grid_lat = np.meshgrid(lons, lats)
    z = height(grid_lat, grid_lon)
    # Slope from the height change per metre north-south and east-west.
    dy_m, dx_m = info["dy"] * M_PER_DEG, info["dx"] * M_PER_DEG * math.cos(math.radians(lat0))
    gy, gx = np.gradient(z, dy_m, dx_m)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    north_m, east_m = (grid_lat - lat0) * M_PER_DEG, (grid_lon - lon0) * M_PER_DEG * math.cos(math.radians(lat0))
    stats = {}
    for km in BOX_KM:
        inside = (np.abs(north_m) <= km * 500) & (np.abs(east_m) <= km * 500)
        stats[f"slope_mean_{km}km"] = round(float(np.nanmean(slope[inside])), 2)
        stats[f"slope_sd_{km}km"] = round(float(np.nanstd(slope[inside])), 2)
        stats[f"relief_m_{km}km"] = round(float(np.nanmax(z[inside]) - np.nanmin(z[inside])), 1)
    stats["pixel_spacing"] = f'{info["dy"] * 3600:g}" x {info["dx"] * 3600:g}"'
    return stats


def main():
    sites = import_sheet.read_tab(import_sheet.SITE_OPTIONS, ["Site", "Lat", "Lon"])
    rows = []
    for _, site in sites.iterrows():
        lat, lon = float(site["Lat"]), float(site["Lon"])
        row = {"site": site["Site"], "lat": lat, "lon": lon, **slope_stats(lat, lon),
               "tile_example": tile_url(math.floor(lat), math.floor(lon)),
               "dem": "Copernicus DEM GLO-30 (AWS open data)", "accessed": date.today().isoformat()}
        rows.append(row)
        print(f"  {site['Site']}: {row[f'slope_mean_{SCORED_BOX_KM}km']}° ± {row[f'slope_sd_{SCORED_BOX_KM}km']}° "
              f"(relief {row[f'relief_m_{SCORED_BOX_KM}km']} m) in {SCORED_BOX_KM} km box; "
              f"1 km: {row['slope_mean_1km']}°, 5 km: {row['slope_mean_5km']}°", flush=True)
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
