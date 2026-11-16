"""
downloads.py: the About page's "How we score" and "Download our data" sections.

Judges (and anyone) can download the exact numbers behind every score and redo
the calculation. build.py calls copy_files() to put the CSVs in docs/data/.
The worked example is calculated from the current data, so it never goes stale.
"""
import html
import shutil

import pandas as pd

import score        # our own data/score.py
import scores_html  # our own data/scores_html.py (units and data labels)
import sun_angle    # our own data/sun_angle.py (why the Sun angle matters)

# (file in data/, what it holds). Copied to docs/data/ so the website can link to them.
FILES = [("sites.csv", "Every Earth site and target: coordinates, scored values and all text"),
         ("scores.csv", "Every score shown on the site: one row per Earth site and the target it is compared with"),
         ("power_skin_temps.csv", "Highest hourly ground (skin) temperature per site, NASA POWER TS_MAX"),
         ("copernicus_slope.csv", "Slope per site (1, 5 and 15 km boxes) from Copernicus DEM GLO-30"),
         ("slope_463m.csv", "Slope at ~463 m pixels: Earth (Copernicus, averaged) and Mars (MOLA)"),
         ("dust_aod.csv", "Earth dust/haze optical depth per site (NASA POWER AOD_55)"),
         ("mars_dust.csv", "Mars dust optical depth at Arcadia, one row per Mars Year, plus the average")]

# Sources used in scoring that are not in the Sheet's source columns, so they are credited here.
SCORE_SOURCES = [
    ("Slope (Earth): Copernicus DEM GLO-30, ESA / European Union, doi:10.5270/ESA-c5d3d65, via AWS open data",
     "https://copernicus-dem-30m.s3.amazonaws.com/readme.html"),
    ("Slope box size: NASA release 22-089 (Aug 2022): Artemis candidate landing regions about 15 × 15 km",
     "https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/"),
    ("Sun angle: axial tilts from the NASA planetary fact sheets (Earth)",
     "https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html"),
    ("Sun angle: NASA Moon fact sheet", "https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html"),
    ("Sun angle: NASA Mars fact sheet", "https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html"),
    ("Slope (Mars): MOLA Mission Experiment Gridded Data Record (MEGDR), Smith et al. 2003, NASA PDS "
     "MGS-M-MOLA-5-MEGDR-L3-V1.0", "https://pds-geosciences.wustl.edu/missions/mgs/megdr.html"),
    ("Dust (Earth): NASA POWER AOD_55, climatology 2001–2025 (CERES SYN1deg)", "https://power.larc.nasa.gov"),
    ("Dust (Mars): LMD Mars dust climatology v2, Montabone et al. 2015, Icarus 251:65–95, "
     "doi:10.1016/j.icarus.2014.12.034", "https://www-mars.lmd.jussieu.fr/mars/dust_climatology/index.html"),
    ("Max temperature (Earth): NASA POWER TS_MAX, Climatology API v2.10.1, 2001–2025", "https://power.larc.nasa.gov"),
]


def copy_files(docs):
    """Copy the data files into docs/data/ (only those that exist)."""
    (docs / "data").mkdir(exist_ok=True)
    for old in (docs / "data").glob("*.csv"):  # remove files we no longer publish
        old.unlink()
    for name, _ in FILES:
        if (score.DATA_DIR / name).exists():
            shutil.copy(score.DATA_DIR / name, docs / "data" / name)


def worked_example(sites, scores):
    """One real calculation, step by step: the best-scoring site on the first scored condition."""
    col = next(c for c in score.DIMENSIONS if scores[c].notna().any())
    best = scores.loc[scores[col].idxmax()]
    site = sites[sites["name"] == best["site"]].iloc[0]
    target = sites[sites["name"] == best["target"]].iloc[0]
    unit, lo, hi = scores_html.UNITS[col], sites[col].min(), sites[col].max()
    gap = abs(site[col] - target[col])
    return (f"<p><strong>Example ({score.DIMENSIONS[col].lower()}):</strong> "
            f"{html.escape(site['name'])} is {site[col]:g}{unit}; {html.escape(target['name'])} is "
            f"{target[col]:g}{unit}. The gap is {gap:.2f}. The widest spread in our data is "
            f"{lo:g} to {hi:g}{unit} = {hi - lo:.2f}. Score = 1 − {gap:.2f} / {hi - lo:.2f} = "
            f"<strong>{best[col]:.2f}</strong>.</p>")


def section(sites, scores):
    """HTML for the two About page sections."""
    scored = [c for c in score.DIMENSIONS if scores[c].notna().any()]
    why = {"sun_max_elev_deg": sun_angle.WHY}  # extra "why it matters" text per condition
    conditions = "".join(f"<li><strong>{score.DIMENSIONS[c]}:</strong> "
                         f"{html.escape(scores_html.DIMENSION_SOURCES.get(c, ''))} "
                         f"{html.escape(why.get(c, ''))}</li>" for c in scored)
    links = "".join(f'<li><a href="data/{name}">{name}</a>: {html.escape(text)}</li>'
                    for name, text in FILES if (score.DATA_DIR / name).exists())
    return (f'<section class="card"><h2>How we score</h2>'
            f"<p>For each condition separately: <code>score = 1 − |Earth value − target value| / "
            f"(largest − smallest value in our data)</code>, kept between 0 and 1. "
            f"1 = same as the target; 0 = as different as anything in our data.</p>"
            f"{worked_example(sites, scores)}<p>Conditions scored so far:</p><ul>{conditions}</ul>"
            f'<p class="meta">Scores are never added into one overall number. Adding or removing a site '
            f"can shift every score a little, because the spread comes from our own data. A condition "
            f'without exact, comparable values on both sides shows "no data": we never estimate.</p></section>'
            f'<section class="card"><h2>Data behind the scores</h2><ul>'
            + "".join(f'<li>{html.escape(label)}: <a href="{url}">{url}</a></li>' for label, url in SCORE_SOURCES)
            + "</ul></section>"
            f'<section class="card"><h2>Download our data</h2><p>The exact numbers behind every score '
            f"(CSV files; open in any spreadsheet):</p><ul>{links}</ul></section>")


# NASA POWER's requested citation (power.larc.nasa.gov/docs/referencing/), and our exact requests.
POWER_CSV = score.DATA_DIR / "power_skin_temps.csv"
POWER_REFERENCE = ("The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research "
                   "Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth "
                   "Science Division.")


def temperature_credit():
    """About page section: the max-temperature data (NASA POWER TS_MAX), citation and each site's request."""
    if not POWER_CSV.exists():
        return ""
    power = pd.read_csv(POWER_CSV)
    first = power.iloc[0]
    rows = "".join(f'<tr><td>{html.escape(r.site)}</td><td>{r.TS_MAX_annual_c:g} °C</td>'
                   f'<td><a href="{html.escape(r.request_url)}">request</a></td></tr>' for r in power.itertuples())
    return (f'<section class="card"><h2>Ground temperatures: NASA POWER (hourly maximum)</h2><p>{POWER_REFERENCE}</p>'
            f'<p>{html.escape(first["api"])}, accessed {html.escape(first["accessed"])}. Parameter TS_MAX: '
            f'"{html.escape(first["TS_MAX_definition"])}" Period: {html.escape(first["period"])}. Source MERRA-2, '
            f'about 50 km grid. This follows our team decision: max = the highest hourly ground (skin) temperature '
            f'reported by the dataset in its stated period, not an all-time record or an average of daily maxima. '
            f'Home: <a href="https://power.larc.nasa.gov">power.larc.nasa.gov</a></p>'
            f'<div class="scroll"><table><tr><th>Site</th><th>TS_MAX</th><th>Exact request</th></tr>{rows}</table></div>'
            f'<p class="meta">We also downloaded MODIS daily (1 km, MYD11A1 via NASA AppEEARS, doi:10.5067/MODIS/'
            f'MYD11A1.061) and 8-day (MYD11A2) temperatures; they are in our repository for reference and not scored, '
            f'because MODIS gives one reading a day, not hourly values.</p></section>')
