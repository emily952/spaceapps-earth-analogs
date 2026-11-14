"""
build.py: build the website in docs/ from data/sites.csv.

Steps:
  1. Score every Earth site against every target (uses score.py).
  2. Write one page per Earth site: radar chart, score table, matches/breaks.
  3. Write docs/index.html: a world map with one marker per Earth site.

Run:  python3 data/build.py   then open docs/index.html in a browser.
Everything in docs/ is generated: edit the CSV or this script, not docs/.
"""
import html
import re
from pathlib import Path

import folium
import pandas as pd
import plotly.graph_objects as go

import score  # our own data/score.py

# Where the website goes.
DOCS = Path(__file__).resolve().parent.parent / "docs"
SITE_PAGES = DOCS / "sites"

# Shown on every site page, as required by the project rules.
LIMITS_NOTE = ("No place on Earth can reproduce lunar or Martian gravity, the Moon's vacuum "
               "or Mars' thin atmosphere, or their radiation environment. These scores compare "
               "surface conditions only.")

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
    """Return the full HTML for one Earth site's page."""
    # Score table: one row per dimension, one column per target.
    table = (site_scores.set_index("target")[list(score.DIMENSIONS)].T
             .rename(index=score.DIMENSIONS)
             .to_html(na_rep="no data", float_format="%.2f", border=0))
    # Source links can be separated by spaces or semicolons in the CSV.
    links = re.split(r"[;\s]+", str(site["source_links"])) if not pd.isna(site["source_links"]) else []
    sources = "".join(f'<li><a href="{show(u)}">{show(u)}</a></li>' for u in links if u) or "<li>no data</li>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{show(site['name'])}</title>
<style>body{{font-family:sans-serif;max-width:820px;margin:auto;padding:16px;line-height:1.5}}
table{{border-collapse:collapse}}td,th{{padding:4px 10px;border-bottom:1px solid #ddd;text-align:left}}
.note{{background:#fff4e5;border-left:4px solid #e67e22;padding:8px 12px}}</style></head>
<body><p><a href="../index.html">&larr; Back to map</a></p>
<h1>{show(site['name'])}</h1>
<p>Lat {show(site['lat'])}, lon {show(site['lon'])}. Scores: 1 = same as target, 0 = as different as anything in our dataset.</p>
{radar_chart(site_scores)}
<h2>Scores by dimension</h2>{table}
<h2>What matches</h2><p>{show(site['matches'])}</p>
<h2>What breaks</h2><p>{show(site['breaks'])}</p>
<p class="note"><strong>Limits of any Earth analog:</strong> {LIMITS_NOTE}</p>
<h2>Sources</h2><ul>{sources}</ul>
</body></html>"""


def build_map(earth_sites, targets):
    """World map with a clickable marker for each Earth site."""
    world = folium.Map(location=[20, 0], zoom_start=2)
    for _, site in earth_sites.iterrows():
        # A site without coordinates can't go on the map; say so instead of guessing.
        if pd.isna(site["lat"]) or pd.isna(site["lon"]):
            print(f"  Skipping on map (no lat/lon): {site['name']}")
            continue
        popup = (f"<b>{show(site['name'])}</b><br>"
                 f"<a href='sites/{slugify(site['name'])}.html'>Open radar chart</a>")
        folium.Marker([site["lat"], site["lon"]], tooltip=show(site["name"]),
                      popup=folium.Popup(popup, max_width=250)).add_to(world)
    # Small info box: title and which targets the sites are compared with.
    target_list = "".join(f"<li>{show(n)}</li>" for n in targets["name"])
    world.get_root().html.add_child(folium.Element(
        "<div style='position:fixed;bottom:20px;left:20px;z-index:9999;background:white;"
        "padding:8px 12px;border-radius:6px;box-shadow:0 1px 4px #0004;font-family:sans-serif;"
        f"max-width:300px'><b>Earth analogs for Moon and Mars</b><br>Click a marker for its "
        f"scores.<br>Compared against:<ul style='margin:4px 0;padding-left:18px'>{target_list}</ul></div>"))
    world.save(DOCS / "index.html")


def main():
    # Step 1: load the data and compute scores (also saved to data/scores.csv).
    sites = score.load_sites()
    scores = score.compute_scores(sites)
    scores.to_csv(score.SCORES_CSV, index=False)
    earth_sites = sites[sites["type"] == "earth"]
    targets = sites[sites["type"].isin(score.TARGET_TYPES)]

    # Step 2: one page per Earth site. Old pages are removed first so a
    # renamed or deleted site doesn't leave a stale page behind.
    SITE_PAGES.mkdir(parents=True, exist_ok=True)
    for old_page in SITE_PAGES.glob("*.html"):
        old_page.unlink()
    for _, site in earth_sites.iterrows():
        page = SITE_PAGES / f"{slugify(site['name'])}.html"
        page.write_text(site_page(site, scores[scores["site"] == site["name"]]), encoding="utf-8")
        print(f"  Wrote {page.relative_to(DOCS.parent)}")

    # Step 3: the map.
    build_map(earth_sites, targets)
    print(f"  Wrote docs/index.html ({len(earth_sites)} Earth sites, {len(targets)} targets)")


if __name__ == "__main__":
    main()
