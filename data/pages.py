"""
pages.py: the HTML for each Earth site's page and for the About & credits page.

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
               "or Mars' thin atmosphere, or their radiation environment. These scores compare "
               "surface conditions only.")

# AI disclosure (a challenge rule). Keep in step with the README's "Use of AI" section.
AI_NOTE = ("AI tools helped with this project's research and coding (coding: Claude Code and "
           "Cursor). Team members verified the sources and reviewed the code.")

# Things we use that are not in sites.csv, so they still get credited.
TOOL_CREDITS = [
    ("Map imagery: NASA EOSDIS GIBS, Blue Marble shaded relief", "https://nasa-gibs.github.io/gibs-api-docs/"),
    ("Map library: Leaflet, via folium", "https://python-visualization.github.io/folium/"),
    ("Charts: plotly", "https://plotly.com/python/"),
    ("Data handling: pandas", "https://pandas.pydata.org"),
]

# Chart colour per target type.
COLOURS = {"moon_target": "#7f8c8d", "mars_target": "#c0392b"}


def slugify(name):
    """Turn a site name into a safe file name, e.g. 'Site A' -> 'site-a'."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def show(value):
    """Make a CSV cell safe to put in HTML; blank cells read 'no data'."""
    if pd.isna(value) or str(value).strip() == "":
        return "no data"
    return html.escape(str(value))


def link_list(links):
    """A bulleted list of links, or 'no data' if there are none."""
    items = "".join(f'<li><a href="{show(u)}">{show(u)}</a></li>' for u in links)
    return f"<ul>{items or '<li>no data</li>'}</ul>"


def page(title, body):
    """Wrap a page body in the shared HTML header and style."""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{show(title)}</title>
<style>body{{font-family:sans-serif;max-width:820px;margin:auto;padding:16px;line-height:1.5}}
table{{border-collapse:collapse}}td,th{{padding:4px 10px;border-bottom:1px solid #ddd;text-align:left}}
.note{{background:#fff4e5;border-left:4px solid #e67e22;padding:8px 12px}}a{{overflow-wrap:anywhere}}</style></head>
<body>{body}</body></html>"""


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


def site_page(site, site_scores):
    """Full HTML for one Earth site's page (saved in docs/sites/)."""
    # Score table: one row per dimension, one column per target.
    table = (site_scores.set_index("target")[list(score.DIMENSIONS)].T
             .rename(index=score.DIMENSIONS)
             .to_html(na_rep="no data", float_format="%.2f", border=0))
    return page(site["name"], f"""
<p><a href="../index.html">&larr; Back to map</a> · <a href="../about.html">About &amp; credits</a></p>
<h1>{show(site['name'])}</h1>
<p>Lat {show(site['lat'])}, lon {show(site['lon'])}. Scores: 1 = same as target, 0 = as different as anything in our dataset.</p>
{radar_chart(site_scores)}
<h2>Scores by dimension</h2>{table}
<h2>What matches</h2><p>{show(site['matches'])}</p>
<h2>What breaks</h2><p>{show(site['breaks'])}</p>
<p class="note"><strong>Limits of any Earth analog:</strong> {LIMITS_NOTE}</p>
<h2>Sources</h2>{link_list(score.split_links(site['source_links']))}""")


def about_page(sites):
    """Full HTML for docs/about.html: method, limits, every source, AI use."""
    # One entry per CSV row (Earth sites and targets), with that row's links.
    data_sources = "".join(f"<h3>{show(row['name'])}</h3>{link_list(score.split_links(row['source_links']))}"
                           for _, row in sites.iterrows())
    tools = "".join(f'<li>{html.escape(label)}: <a href="{url}">{url}</a></li>' for label, url in TOOL_CREDITS)
    return page("About & credits", f"""
<p><a href="index.html">&larr; Back to map</a></p>
<h1>About &amp; credits</h1>
<h2>What this is</h2>
<p>We compare Earth sites with a Moon target and a Mars target, one condition at a time
(slope, temperatures, precipitation, dust). Each condition gets its own score from 0 to 1:
<code>1 - |Earth value - target value| / (largest - smallest value in our dataset)</code>.
1 means the same as the target, 0 means as different as anything in our dataset. Scores are
never added together. Blank data shows as "no data"; we never estimate missing values.</p>
<p class="note"><strong>Limits of any Earth analog:</strong> {LIMITS_NOTE}</p>
<h2>Data sources</h2>{data_sources}
<h2>Tools and imagery</h2><ul>{tools}</ul>
<h2>Use of AI</h2><p>{AI_NOTE}</p>""")
