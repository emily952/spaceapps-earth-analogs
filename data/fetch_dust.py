"""
fetch_dust.py: how dusty/hazy the air is (aerosol optical depth) at each Earth site and Mars target.

Optical depth = how much sunlight the dust and haze in the whole air column block
(0 = perfectly clear; 1 = about 63% of direct sunlight blocked). We use yearly averages.

Earth: NASA POWER parameter AOD_55 ("The optical thickness at 0.55 um measured vertically"),
  climatology 2001-2025, source CERES SYN1deg, about 1 degree (~100 km) grid. No login.
Mars: LMD Mars dust climatology (Montabone et al. 2015, Icarus 251:65-95,
  doi:10.1016/j.icarus.2014.12.034; v2 maps), built from orbiter measurements (TES, THEMIS,
  MCS) for Mars Years 24-36. Variable "cdodtot": 9.3 micrometre infrared ABSORPTION column
  dust optical depth for the whole local air column, on a 3 x 3 degree grid (~180 km).
  LMD's own note: "Equivalent visible column optical depths can be obtained by multiplying
  the 9.3 um absorption column dust optical depth by 2.6." We do that, so Mars is in visible
  light like Earth's 0.55 um value. Moon: no air, no dust optical depth: "no data".
Caveats: different wavelengths (0.55 um vs visible-equivalent), different grid sizes, and
  Earth's value counts all aerosols (dust, smoke, sea salt), Mars' only dust.

The Mars files are "classic" netCDF (a simple binary layout), read here without extra
libraries: we read the header, then download only the cdodtot block (~19 MB per year).
Output: data/dust_aod.csv (Earth sites), data/mars_dust.csv (Mars target, one row per year + mean).
Run:  python3 data/fetch_dust.py   (needs internet; a few minutes)
"""
import struct
import time
import urllib.request
from datetime import date

import pandas as pd

import fetch_power   # our own data/fetch_power.py (get_json for NASA POWER)
import import_sheet  # our own data/import_sheet.py (site and target coordinates)
import score         # our own data/score.py (paths)

POWER_URL = ("https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=AOD_55"
             "&community=AG&longitude={lon}&latitude={lat}&format=JSON")
LMD = "https://www-mars.lmd.jussieu.fr/mars/dust_climatology/dataset_v2/"
MARS_FILES = [f"dustscenario_MY{y}_v2-0.nc" for y in range(24, 33)] + [
    "dustscenario_MY33_v2-1.nc", "dustscenario_MY34_v2-5.nc", "dustscenario_MY35_v2-5.nc",
    "dustscenario_MY36_v2-5.nc"]
VISIBLE_PER_IR = 2.6  # LMD: visible column optical depth = 2.6 x 9.3 um absorption optical depth


def get(url, start, end):
    """Bytes start..end of a file (HTTP Range request)."""
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}", "User-Agent": "earth-analogs-script"})
    with urllib.request.urlopen(req, timeout=300) as response:
        return response.read()


def netcdf_header(raw):
    """Variables of a classic netCDF file: name -> (dimension names, start byte). Big-endian."""
    pos = 8  # skip "CDF", version byte, number of records

    def number():
        nonlocal pos
        pos += 4
        return struct.unpack(">i", raw[pos - 4:pos])[0]

    def name():
        nonlocal pos
        n = number()
        text = raw[pos:pos + n].decode()
        pos += (n + 3) // 4 * 4  # names are padded to 4 bytes
        return text

    def skip_attributes():
        nonlocal pos
        number()
        for _ in range(number()):
            name()
            kind, count = number(), number()
            pos += (count * {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 8}[kind] + 3) // 4 * 4

    number()
    dims = [(name(), number()) for _ in range(number())]
    skip_attributes()
    number()
    variables = {}
    for _ in range(number()):
        var = name()
        dim_ids = [number() for _ in range(number())]
        skip_attributes()
        number(), number()  # data type, size
        variables[var] = ([dims[d] for d in dim_ids], number())
    return variables


def mars_year_mean(file_name, lat, lon):
    """Yearly mean visible-equivalent dust optical depth at the grid cell nearest lat/lon."""
    url = LMD + file_name
    head = get(url, 0, 65535)
    variables = netcdf_header(head)
    floats = lambda var: struct.unpack(f">{variables[var][0][0][1]}f",
                                       head[variables[var][1]:variables[var][1] + 4 * variables[var][0][0][1]])
    lats, lons = floats("latitude"), floats("longitude")
    i = min(range(len(lats)), key=lambda k: abs(lats[k] - lat))
    j = min(range(len(lons)), key=lambda k: abs((lons[k] - lon + 180) % 360 - 180))
    (n_time, _), (n_lat, _), (n_lon, _) = [(d[1], d[0]) for d in variables["cdodtot"][0]]
    begin = variables["cdodtot"][1]
    block = get(url, begin, begin + 4 * n_time * n_lat * n_lon - 1)
    values = [struct.unpack(">f", block[4 * ((t * n_lat + i) * n_lon + j): 4 * ((t * n_lat + i) * n_lon + j) + 4])[0]
              for t in range(n_time)]
    good = [v for v in values if v == v and v >= 0]  # drop missing values (NaN or negative)
    return round(VISIBLE_PER_IR * sum(good) / len(good), 3), lats[i], lons[j], len(good)


def main():
    rows = []  # Earth: NASA POWER annual AOD_55 per site
    sites = import_sheet.read_tab(import_sheet.SITE_OPTIONS, ["Site", "Lat", "Lon"])
    for _, s in sites.iterrows():
        url = POWER_URL.format(lat=s["Lat"], lon=s["Lon"])
        value = fetch_power.get_json(url)["properties"]["parameter"]["AOD_55"]["ANN"]
        rows.append({"site": s["Site"], "aod_55_annual": None if value == -999 else value, "request_url": url,
                     "source": "NASA POWER AOD_55 climatology 2001-2025 (CERES SYN1deg, ~1 degree)",
                     "accessed": date.today().isoformat()})
        print(f"  {s['Site']}: AOD {rows[-1]['aod_55_annual']}", flush=True)
        time.sleep(1)
    pd.DataFrame(rows).to_csv(score.DATA_DIR / "dust_aod.csv", index=False)

    mars_rows = []  # Mars: one row per Mars Year, then the average of all years
    targets = import_sheet.read_targets()
    for _, t in targets[targets["Body"].str.strip() == "Mars"].iterrows():
        lat, lon = float(t["Lat"]), float(t["Lon (-180 to 180)"])
        for file_name in MARS_FILES:
            mean, cell_lat, cell_lon, sols = mars_year_mean(file_name, lat, lon)
            mars_rows.append({"target": t["Target"], "mars_year": file_name.split("_")[1], "dust_visible_mean": mean,
                              "grid_lat": cell_lat, "grid_lon": cell_lon, "sols": sols, "file": LMD + file_name})
            print(f"  {t['Target']} {file_name}: {mean} ({sols} sols, cell {cell_lat}, {cell_lon})", flush=True)
        years = [r["dust_visible_mean"] for r in mars_rows if r["target"] == t["Target"]]
        mars_rows.append({"target": t["Target"], "mars_year": "ALL", "dust_visible_mean": round(sum(years) / len(years), 3),
                          "file": "average of the Mars Years above"})
    pd.DataFrame(mars_rows).to_csv(score.DATA_DIR / "mars_dust.csv", index=False)
    print("Wrote dust_aod.csv and mars_dust.csv")


if __name__ == "__main__":
    main()
