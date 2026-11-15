"""
pages.py: shared HTML helpers, each Earth site's page, and the About & credits page.

build.py calls these functions and saves the results into docs/.
All text from the CSV goes through show(), so it is safe to put in HTML.
"""
import html
import re

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

# Chart colour per target type.
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
    """A bulleted list of links, or 'no data' if there are none."""
    items = "".join(f'<li><a href="{show(u)}">{show(u)}</a></li>' for u in links)
    return f"<ul>{items or '<li>no data</li>'}</ul>"


def page(title, body, root=""):
    """Wrap a page body in the shared header, style and navigation bar.
    root is "" for pages in docs/ and "../" for pages in docs/sites/."""
    nav = (f'<nav><a href="{root}index.html">Map</a> · <a href="{root}gap.html">Where Earth falls short</a> · '
           f'<a href="{root}tasks.html">Sites by mission task</a> · <a href="{root}about.html">About &amp; credits</a></nav>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{show(title)}</title>
<style>body{{font-family:sans-serif;max-width:860px;margin:auto;padding:16px;line-height:1.5;background:#fff;color:#222}}
table{{border-collapse:collapse;width:100%}}td,th{{padding:6px 8px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}}
.note{{background:#fff4e5;border-left:4px solid #e67e22;padding:8px 12px}}.meta{{color:#555}}
nav{{padding-bottom:8px;border-bottom:1px solid #ddd}}a{{overflow-wrap:anywhere}}.scroll{{overflow-x:auto}}</style></head>
<body>{nav}{body}</body></html>"""


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
        return f'<p class="note">{NOT_SCORED_NOTE}</p>'
    table = (site_scores.set_index("target")[list(score.DIMENSIONS)].T.rename(index=score.DIMENSIONS)
             .to_html(na_rep="no data", float_format="%.2f", border=0))
    return (f"<p>1 = same as the target, 0 = as different as anything in our dataset.</p>"
            f"{radar_chart(site_scores)}<div class='scroll'>{table}</div>")


def site_page(site, site_scores):
    """Full HTML for one Earth site's page (saved in docs/sites/)."""
    notes = "".join(f"<li>{show(line)}</li>" for line in str(site["climate_notes"]).splitlines()
                    if not pd.isna(site["climate_notes"]))
    return page(site["name"], f"""
<h1>{show(site['name'])}</h1>
<p class="meta">{show(site['category'])} · Analog for: {show(site['analog_for'])}<br>
Lat {show(site['lat'])}, lon {show(site['lon'])} · How well studied (team estimate): {show(site['how_well_studied'])}</p>
<h2>What matches</h2><p>{show(site['matches'])}</p>
<h2>Where it breaks</h2><p>{show(site['breaks'])}</p>
<p class="note"><strong>Limits of any Earth analog:</strong> {LIMITS_NOTE}</p>
<h2>Suggested mission tasks</h2><p>{show(site['mission_tasks'])} <span class="meta">(team judgment)</span></p>
<h2>Key facts</h2><p>{show(site['key_facts'])}</p>
<h2>Climate and conditions</h2><ul>{notes or '<li>no data</li>'}</ul>
<h2>Geology and minerals</h2><p>{show(site['geology'])}</p>
<h2>Similarity scores</h2>{scores_section(site_scores)}
<h2>Sources</h2>{link_list(score.split_links(site['source_links']))}""", root="../")


def about_page(sites, limits):
    """Full HTML for docs/about.html: method, limits, every source, AI use."""
    # One entry per site/target, then per row of the Earth's limits table.
    rows = [(r["name"], r["source_links"]) for _, r in sites.iterrows()]
    rows += [(f"Earth's limits: {r['Condition']}", r["Source URLs (plain text)"]) for _, r in limits.iterrows()]
    data_sources = "".join(f"<h3>{show(name)}</h3>{link_list(score.split_links(links))}" for name, links in rows)
    tools = "".join(f'<li>{html.escape(label)}: <a href="{url}">{url}</a></li>' for label, url in TOOL_CREDITS)
    return page("About & credits", f"""
<h1>About &amp; credits</h1>
<h2>What this is</h2>
<p>Earth places that resemble parts of the Moon's south pole (Malapert Massif) and a Martian
ice plain (Arcadia Planitia): what matches, where each falls short, and which mission tests
each could support. We also score individual conditions from 0 to 1 with
<code>1 - |Earth value - target value| / (largest - smallest value in our dataset)</code>,
but only where we have exact, comparable measurements; scores are never added together.
Missing data shows as "no data"; we never estimate.</p>
<p class="note"><strong>Limits of any Earth analog:</strong> {LIMITS_NOTE}</p>
<h2>Use of AI</h2><p>{AI_NOTE}</p>
<h2>Tools and imagery</h2><ul>{tools}</ul>
<h2>Data sources</h2>{data_sources}""")
