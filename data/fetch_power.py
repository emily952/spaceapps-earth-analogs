"""
fetch_power.py: download NASA POWER ground ("skin") temperatures for every Earth site.

For each site in data/site_options.csv, ask the NASA POWER climatology API (free,
no key) for the annual TS_MAX and TS_MIN at the site's lat/lon, and save them with
the exact request URL and POWER's own definition of each parameter.

Output: data/power_skin_temps.csv. import_sheet.py reads TS_MAX from it as temp_max_c.

What the numbers are (checked on Nov 15 against POWER's parameter metadata):
  TS_MAX = "The maximum hourly earth skin temperature in the period of interest."
  The annual value is the single hottest hour, NOT an average of daily maxima
  (that is a different parameter, TS_MAX_AVG). Source: MERRA-2 reanalysis, a
  model grid of about 50 km, so it describes the grid cell, not one exact spot.
  Check at Lut: each month's climatology value equals the highest value for that
  month in POWER's year-by-year data up to about 2020-2022 (e.g. annual 63.86 °C =
  July 2019), although the reply header says the period is 2001-2025.

Run only when sites change (it uses the internet):  python3 data/fetch_power.py
"""
import json
import time
import urllib.request
from datetime import date

import pandas as pd

import import_sheet  # our own data/import_sheet.py (reads site_options.csv)
import score         # our own data/score.py (for paths)

OUTPUT = score.DATA_DIR / "power_skin_temps.csv"
PARAMETERS = ["TS_MAX", "TS_MIN"]
POINT_URL = ("https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=TS_MAX,TS_MIN"
             "&community=AG&longitude={lon}&latitude={lat}&format=JSON")
DEFINITION_URL = ("https://power.larc.nasa.gov/api/system/manager/parameters/{param}"
                  "?community=AG&temporal=climatology")
MISSING = -999  # POWER's code for "no value"


def get_json(url):
    """Download a URL and read it as JSON. Stops with an error if POWER doesn't answer."""
    request = urllib.request.Request(url, headers={"User-Agent": "earth-analogs-script"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def definition(param):
    """POWER's own wording for a parameter, from its metadata service."""
    info = get_json(DEFINITION_URL.format(param=param))[param]["temporal"]["CLIMATOLOGY"]
    return f"{info['name']}: {info['definition']}"


def main():
    sites = import_sheet.read_tab(import_sheet.SITE_OPTIONS, ["Site", "Lat", "Lon"])
    definitions = {p: definition(p) for p in PARAMETERS}
    rows = []
    for _, site in sites.iterrows():
        url = POINT_URL.format(lat=site["Lat"], lon=site["Lon"])
        reply = get_json(url)
        values = reply["properties"]["parameter"]
        row = {"site": site["Site"], "lat": site["Lat"], "lon": site["Lon"]}
        for p in PARAMETERS:
            annual = values[p]["ANN"]
            row[f"{p}_annual_c"] = None if annual == MISSING else annual  # missing stays blank
        row["request_url"] = url
        row["period"] = reply["header"].get("range", "")
        row["source"] = ", ".join(reply["header"].get("sources", []))
        # POWER asks citations to give the service, version and date accessed.
        row["api"] = f"{reply['header']['api']['name']} {reply['header']['api']['version']}"
        row["accessed"] = date.today().isoformat()
        for p in PARAMETERS:
            row[f"{p}_definition"] = definitions[p]
        rows.append(row)
        print(f"  {site['Site']}: TS_MAX {row['TS_MAX_annual_c']} °C, TS_MIN {row['TS_MIN_annual_c']} °C")
        time.sleep(1)  # be gentle with the free service
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT.name} ({len(rows)} sites)")


if __name__ == "__main__":
    main()
