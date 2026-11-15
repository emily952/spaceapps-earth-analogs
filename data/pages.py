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
import plotly.graph_objects as go

import score  # our own data/score.py

# Shown on every site page and the About page, as required by the project rules.
LIMITS_NOTE = ("No place on Earth can reproduce lunar or Martian gravity, the Moon's vacuum "
               "or Mars' thin atmosphere, or their radiation environment.")

# Shown instead of a radar chart when a site has no real scores (project rule).
NOT_SCORED_NOTE = ("Not scored yet. We only score a condition when we have an exact, ground-surface "
                   "value for both this site and a Moon or Mars target. We don't have such a pair "
                   "yet, so we show no chart rather than an empty or misleading one. The values we "
                   "do have are listed above, with their caveats.")

# AI disclosure (a challenge rule). Keep in step with the README's "Use of AI" section.
AI_NOTE = ("AI tools helped with this project's research and coding (coding: Claude Code and "
           "Cursor). Team members verified the sources and reviewed the code.")

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

# Radar chart colour per target type.
COLOURS = {"moon_target": "#7f8c8d", "mars_target": "#c0392b"}


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
<body><nav><a href="{root}index.html">Map</a><a href="{root}gap.html">Where Earth falls short</a>
<a href="{root}tasks.html">Sites by mission task</a><a href="{root}about.html">About &amp; credits</a></nav>
<main>{body}</main></body></html>"""


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


def radar_chart(site_scores):
    """Radar chart with one shape per target. Missing scores leave a gap."""
    labels = list(score.DIMENSIONS.values())
    fig = go.Figure()
    for _, row in site_scores.iterrows():
        values = [row[col] for col in score.DIMENSIONS]
        hover = ["no data" if pd.isna(v) else f"{v:.2f}" for v in values]
        # Repeat the first point at the end so the shape closes.
        fig.add_trace(go.Scatterpolar(
            r=values + values[:1], theta=labels + labels[:1], customdata=hover + hover[:1],
            name=row["target"], fill="toself", line_color=COLOURS[row["target_type"]],
            hovertemplate="%{theta}: %{customdata}<extra>%{fullData.name}</extra>"))
    fig.update_layout(polar={"radialaxis": {"range": [0, 1]}}, height=480,
                      legend={"orientation": "h"}, margin={"t": 30, "b": 30})
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def scores_section(site_scores):
    """Radar chart and score table, but only if the site has at least one real score."""
    if not site_scores[list(score.DIMENSIONS)].notna().any().any():
        return f'<p class="meta">{NOT_SCORED_NOTE}</p>'
    table = (site_scores.set_index("target")[list(score.DIMENSIONS)].T.rename(index=score.DIMENSIONS)
             .to_html(na_rep="no data", float_format="%.2f", border=0))
    return (f"<p>1 = same as the target, 0 = as different as anything in our dataset.</p>"
            f"{radar_chart(site_scores)}<div class='scroll'>{table}</div>")


def site_page(site, site_scores):
    """Full HTML for one Earth site's page (saved in docs/sites/)."""
    return page(site["name"], f"""
<h1>{show(site['name'])}</h1>
<div class="badges">{category_badge(site['category'])}<span class="badge">Analog for: {show(site['analog_for'])}</span>
<span class="badge">How well studied: {show(site['how_well_studied'])} (team estimate)</span></div>
<p class="meta">Lat {show(site['lat'])}, lon {show(site['lon'])}</p>
<div class="grid"><section class="card match"><h2>What matches</h2><p>{show(site['matches'])}</p></section>
<section class="card break"><h2>Where it breaks</h2><p>{show(site['breaks'])}</p></section></div>
<p class="note"><strong>Limits of any Earth analog:</strong> {LIMITS_NOTE}</p>
<section class="card"><h2>Key facts</h2><p>{show(site['key_facts'])}</p></section>
<div class="grid"><section class="card"><h2>Climate and conditions</h2>{notes_list(site['climate_notes'])}</section>
<section class="card"><h2>Geology and minerals</h2><p>{show(site['geology'])}</p>
<h2>Suggested mission tasks</h2><p>{show(site['mission_tasks'])} <span class="meta">(team judgment)</span></p></section></div>
<section class="card"><h2>Similarity scores</h2>{scores_section(site_scores)}</section>
<section class="card"><h2>Sources</h2>{link_list(score.split_links(site['source_links']))}</section>""", root="../")
