"""
sun_angle.py: the highest the Sun ever gets in the sky at each site or target.

Why it matters: a low Sun means long shadows, glare and cold, which shape how
landers, rovers and solar panels are tested. It is the one condition we can
compare for BOTH the Moon and Mars targets, using only latitude.

How: at noon on the day the Sun is furthest toward a site's hemisphere,
    highest Sun angle = 90 - max(0, |latitude| - axial tilt)
(If |latitude| is less than the tilt, the Sun passes straight overhead: 90.)
It is one value per point (the site's latitude); it barely changes across a site.
It is calculated from geometry, not measured. It assumes a flat horizon and
ignores mountains and slopes, and the small bending of light by Earth's air.

Axial tilts (tilt of the equator to the planet's path around the Sun), from the
NASA planetary fact sheets (nssdc.gsfc.nasa.gov/planetary/factsheet/):
  Earth 23.44 and Mars 25.19 ("Obliquity to orbit").
  Moon 1.54: the fact sheet lists 6.68 ("Obliquity to orbit") and 5.145 ("Inclination
  to ecliptic"). The Moon's equator, orbit and Earth's path share one tilt line
  (Cassini's laws), so its equator is tilted 6.68 - 5.145 = 1.535, i.e. 1.54 degrees,
  to Earth's path around the Sun.
"""
import pandas as pd

TILT_DEG = {"earth": 23.44, "moon_target": 1.54, "mars_target": 25.19}
# Shown on the About page: why this condition matters for missions.
WHY = ("Why it matters: at the Moon's south pole the Sun stays near the horizon, so shadows are very "
       "long and crews and cameras look almost straight into the Sun. Glare and deep shadow make "
       "landing, driving and finding hazards harder: a real problem for Artemis astronauts and rovers.")
# Written as "Earth: / Moon: / Mars:" parts: a Moon-analog page drops the Mars part and vice versa.
SOURCE = ("Calculated from each place's latitude (one point) and axial tilt (NASA planetary fact sheets); "
          "flat horizon assumed, hills and slopes ignored. Earth: tilt 23.44°, so nowhere on Earth does the "
          "Sun's highest point of the year stay below 23.4°. Moon: tilt 1.54°, so no Earth site can match Malapert's low Sun. "
          "Mars: tilt 25.19°.")


def highest_sun(lat, row_type):
    """Highest Sun angle in degrees above the horizon, or None if latitude is missing."""
    lat = pd.to_numeric(lat, errors="coerce")  # the Sheet gives text; blank -> NaN
    if pd.isna(lat):  # no latitude, so no value (never guessed)
        return None
    return round(90.0 - max(0.0, abs(lat) - TILT_DEG[row_type]), 2)


def add_column(rows):
    """Fill the sun_max_elev_deg column for every row (Earth sites and targets)."""
    rows["sun_max_elev_deg"] = [highest_sun(lat, kind) for lat, kind in zip(rows["lat"], rows["type"])]
    return rows


def gap_card(sites):
    """Gap page card: no Earth site can get the Sun as low as the Moon's south pole does."""
    moon = sites[sites["type"] == "moon_target"].iloc[0]
    earth = sites[sites["type"] == "earth"].sort_values("sun_max_elev_deg").iloc[0]  # lowest Earth site
    return (f'<section class="card"><h2>Lowest Sun</h2><p>At {moon["name"]} the Sun never climbs '
            f'higher than about {moon["sun_max_elev_deg"]:.1f}° above the horizon: it skims along the edge of '
            f'the sky, casting very long shadows. Nowhere on Earth does the Sun\'s highest point of the year '
            f'stay below 23.4°, because Earth is tilted 23.44° but the Moon only 1.5°. Our lowest site, '
            f'{earth["name"]}, gets {earth["sun_max_elev_deg"]:.1f}°. Low-Sun lighting for cameras, solar panels '
            f'and shadow navigation has to be tested in a lab or simulated.</p><p class="meta">Calculated '
            f'from each place\'s latitude (one point; no map pixels involved) and axial tilt (NASA '
            f'planetary fact sheets). Flat horizon assumed: on Malapert\'s slopes and peaks the Sun can '
            f'look higher or lower than this.</p></section>')
