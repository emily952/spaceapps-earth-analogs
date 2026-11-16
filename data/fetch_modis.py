"""
fetch_modis.py: hottest 8-day MODIS land surface temperature (1 km pixel) for every Earth site.

Why: NASA POWER (fetch_power.py) describes a ~50 km grid cell. MODIS is the smallest
Earth temperature data on our Resources list that covers all 12 sites and needs no
login: one value = one 1 km pixel at the site's lat/lon.

What we download: product MYD11A2 (MODIS Aqua, 8-day composite, 1 km), band LST_Day_1km,
every 8-day period of YEAR, through NASA's ORNL DAAC MODIS web service (free, no key).
Each value is the AVERAGE of the clear-sky daytime readings in one 8-day period.
(The daily product MYD11A1 is not offered by this service: it answers "not found".)
Aqua passes over at about 1:30 pm local time, close to the hottest part of the day.
We keep the hottest 8-day value of the year. Because it is an average, it is a few
degrees below the single hottest reading: label it "hottest 8-day average".

Units: the raw number times 0.02 gives kelvin (MODIS user guide). Raw values under
7500 are "no data" (0 = fill). Kelvin minus 273.15 = °C.

Output: data/modis_lst.csv (one row per site, with an example request URL to cite).
Run when sites change (uses the internet, takes a few minutes):  python3 data/fetch_modis.py

Cite as: ORNL DAAC. 2018. MODIS and VIIRS Land Product Subsets RESTful Web Service.
https://doi.org/10.3334/ORNLDAAC/1600 . Product MYD11A2 v6.1 (Wan, Hook, Hulley).
"""
import calendar
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pandas as pd

import import_sheet  # our own data/import_sheet.py (reads site_options.csv)
import score         # our own data/score.py (for paths)

OUTPUT = score.DATA_DIR / "modis_lst.csv"
BASE = "https://modis.ornl.gov/rst/api/v1"
PRODUCT = "MYD11A2"      # Aqua 8-day land surface temperature, 1 km
BAND = "LST_Day_1km"     # daytime reading
YEAR = 2025              # the most recent full year
SCALE = 0.02             # raw value x 0.02 = kelvin
MIN_VALID = 7500         # raw values below this mean "no data"
WORKERS = 4              # requests at the same time (be gentle with the free service)


def get_json(url, tries=4):
    """Download a URL as JSON. Retries a few times, because the service is sometimes slow."""
    request = urllib.request.Request(url, headers={"Accept": "application/json",
                                                   "User-Agent": "earth-analogs-script"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(5 * (attempt + 1))  # wait a bit longer each time


def subset_url(lat, lon, start, end):
    """One request: the single 1 km pixel at lat/lon, for dates start..end (max 10 dates)."""
    return (f"{BASE}/{PRODUCT}/subset?latitude={lat}&longitude={lon}&band={BAND}"
            f"&startDate={start}&endDate={end}&kmAboveBelow=0&kmLeftRight=0")


def windows(year):
    """The service allows at most 10 dates per request. One date = one 8-day period, so
    80 days = 10 periods per request. MODIS dates look like A2025001 (year + day of year)."""
    days = 366 if calendar.isleap(year) else 365
    for first in range(1, days + 1, 80):
        last = min(first + 79, days)
        yield f"A{year}{first:03d}", f"A{year}{last:03d}"


def readings(lat, lon, start, end):
    """All valid (period start date, °C) values in one window."""
    reply = get_json(subset_url(lat, lon, start, end))
    found = []
    for day in reply.get("subset", []):
        raw = day["data"][0]  # one pixel, so one number per 8-day period
        if raw is not None and raw >= MIN_VALID:
            found.append((day["calendar_date"], round(raw * SCALE - 273.15, 2)))
    return found


def hottest(site):
    """Hottest 8-day average of clear-sky daytime readings in the year, at one site."""
    pieces_of_year = list(windows(YEAR))
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        pieces = pool.map(lambda w: readings(site["Lat"], site["Lon"], *w), pieces_of_year)
    all_days = [reading for piece in pieces for reading in piece]
    row = {"site": site["Site"], "lat": site["Lat"], "lon": site["Lon"],
           "LST_day_max_c": None, "date_of_max": None, "periods_with_data": len(all_days)}
    if all_days:
        row["date_of_max"], row["LST_day_max_c"] = max(all_days, key=lambda r: r[1])
    first, last = pieces_of_year[0][0], pieces_of_year[-1][1]
    row["example_request_url"] = subset_url(site["Lat"], site["Lon"], first, first)
    row["product"] = f"{PRODUCT} {BAND} (1 km, 8-day), {first}-{last}"
    row["service"] = "ORNL DAAC MODIS/VIIRS Land Product Subsets web service, doi:10.3334/ORNLDAAC/1600"
    row["accessed"] = date.today().isoformat()
    return row


def main():
    sites = import_sheet.read_tab(import_sheet.SITE_OPTIONS, ["Site", "Lat", "Lon"])
    rows = []
    for _, site in sites.iterrows():
        row = hottest(site)
        rows.append(row)
        print(f"  {row['site']}: max {row['LST_day_max_c']} °C on {row['date_of_max']} "
              f"(from 8-day period starting then; {row['periods_with_data']} periods with data)", flush=True)
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT.name} ({len(rows)} sites)")


if __name__ == "__main__":
    main()
