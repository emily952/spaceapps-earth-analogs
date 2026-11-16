"""
pages.py: shared HTML helpers and each Earth site's page.

build.py calls these functions and saves the results into docs/.
All text from the CSV goes through show(), so it is safe to put in HTML.
The look of every page comes from data/style.css (copied to docs/ by build.py).
"""
import html
import re
from urllib.parse import urlparse

import pandas as pd

import analog       # our own data/analog.py (Moon or Mars analog?)
import score        # our own data/score.py
import scores_html  # our own data/scores_html.py (the "Similarity scores" section)

# Shown on every site page and the About page, as required by the project rules.
# Site pages use the version for their own body (limits_note); "both" sites get LIMITS_NOTE.
LIMITS_BY_BODY = {
    "moon_target": "No place on Earth can reproduce the Moon's low gravity, its vacuum or its radiation environment.",
    "mars_target": "No place on Earth can reproduce Mars' low gravity, its thin atmosphere or its radiation environment.",
}
LIMITS_NOTE = ("No place on Earth can reproduce lunar or Martian gravity, the Moon's vacuum "
               "or Mars' thin atmosphere, or their radiation environment.")

# AI disclosure (a challenge rule). Keep in step with the README's "Use of AI" section.
AI_NOTE = ("AI tools helped with this project's research and coding. Claude (chat) did background research and compiled the research spreadsheet, research doc and source list; the team reviewed them, chose the targets and sites, and made the method decisions. "
           "Coding: Claude Code and Cursor wrote the scripts and website; the team reviewed the code "
           "and verified the sources.")

# Things we use that are not in the sheet, so they still get credited.
TOOL_CREDITS = [
    ("Map imagery: NASA EOSDIS GIBS, Blue Marble shaded relief", "https://nasa-gibs.github.io/gibs-api-docs/"),
    ("Map library: Leaflet, via folium", "https://python-visualization.github.io/folium/"),
    ("Charts: plotly", "https://plotly.com/python/"),
    ("Data handling: pandas", "https://pandas.pydata.org"),
]

# Site categories: (start of the Category text, map marker colour, matching dot colour, legend text).
# build.py uses this for the map markers, so map and pages always agree.
CATEGORIES = [("New find", "blue", "#38aadd", "new finds"),
              ("Baseline", "gray", "#575757", "well-known baselines"),
              ("Limit site", "purple", "#d252b9", "limit site (shows Earth's gap)")]


def slugify(name):
    """Turn a site name into a safe file name, e.g. 'Lut Desert, Iran' -> 'lut-desert-iran'."""
    name = name.lower().translate(str.maketrans("áéíóúñ", "aeioun"))
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-")


def show(value):
    """Make a CSV cell safe to put in HTML; blank cells read 'no data'."""
    if pd.isna(value) or str(value).strip() == "":
        return "no data"
    return html.escape(str(value))


def link_list(links):
    """Numbered list of sources: the website's name as the link, the full address underneath."""
    items = "".join(f'<li><a href="{show(u)}">{show(urlparse(u).netloc.removeprefix("www.") or u)}</a>'
                    f"<small>{show(u)}</small></li>" for u in links)
    return f'<ol class="sources">{items}</ol>' if items else "<p>no data</p>"


def page(title, body, root=""):
    """Wrap a page body in the shared header, stylesheet and navigation bar.
    root is "" for pages in docs/ and "../" for pages in docs/sites/."""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{show(title)}</title><link rel="stylesheet" href="{root}style.css"></head>
<body><nav><a href="{root}index.html">Key findings</a><a href="{root}map.html">Map</a><a href="{root}gap.html">Where Earth falls short</a>
<a href="{root}compare.html">Compare sites</a><a href="{root}tasks.html">Sites by mission task</a><a href="{root}about.html">About &amp; credits</a></nav>
<main>{body}</main></body></html>"""


def limits_note(analog_for):
    """The fixed limits note, naming only the body (Moon / Mars) this site is an analog for."""
    compared = analog.compared_targets(analog_for)
    return LIMITS_BY_BODY[compared[0]] if len(compared) == 1 else LIMITS_NOTE


def category_badge(category):
    """Pill showing the site's category, with a dot in its map-marker colour."""
    colour = next((dot for start, _, dot, _ in CATEGORIES if str(category).startswith(start)), "#888")
    return f'<span class="badge"><span class="dot" style="background:{colour}"></span>{show(category)}</span>'


def notes_list(text):
    """'Label: value' lines (from import_sheet.py) as a two-column label/value list."""
    lines = [] if pd.isna(text) else str(text).splitlines()
    items = "".join(f"<dt>{show(label)}</dt><dd>{show(value)}</dd>"
                    for label, _, value in (line.partition(": ") for line in lines))
    return f"<dl>{items}</dl>" if items else "<p>no data</p>"


def site_page(site, site_scores, sites):
    """Full HTML for one Earth site's page (saved in docs/sites/).
    sites (all rows, incl. targets) is needed to show the values each score compares."""
    return page(site["name"], f"""
<h1>{show(site['name'])}</h1>
<div class="badges">{category_badge(site['category'])}<span class="badge">Analog for: {show(site['analog_for'])}</span>
<span class="badge">How well studied: {show(site['how_well_studied'])} (team estimate)</span></div>
<p class="meta">Lat {show(site['lat'])}, lon {show(site['lon'])}</p>
<div class="grid"><section class="card match"><h2>What matches</h2><p>{show(site['matches'])}</p></section>
<section class="card break"><h2>Where it breaks</h2><p>{show(site['breaks'])}</p></section></div>
<p class="note"><strong>Limits of any Earth analog:</strong> {limits_note(site['analog_for'])}</p>
<section class="card"><h2>Key facts</h2><p>{show(site['key_facts'])}</p></section>
<div class="grid"><section class="card"><h2>Climate and conditions</h2>{notes_list(site['climate_notes'])}</section>
<section class="card"><h2>Geology and minerals</h2><p>{show(site['geology'])}</p>
<h2>Suggested mission tasks</h2><p>{show(site['mission_tasks'])} <span class="meta">(team judgment)</span></p></section></div>
<section class="card"><h2>Similarity scores</h2>{scores_html.scores_section(site, site_scores, sites)}</section>
<section class="card"><h2>Sources</h2>{link_list(score.split_links(site['source_links']))}</section>""", root="../")
