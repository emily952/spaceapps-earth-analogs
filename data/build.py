"""
build.py: build the website in docs/ from the research sheet exports in data/.

Steps:
  1. Turn the sheet exports into data/sites.csv (import_sheet.py).
  2. Score every Earth site against every target (score.py).
  3. Write one page per Earth site, the compare, gap, task and About pages.
  4. Write docs/index.html: a world map with one marker per Earth site.
  5. Print warnings about anything to fix before submitting.

Run:  python3 data/build.py   then open docs/index.html in a browser.
Everything in docs/ is generated: edit the Sheet or these scripts, not docs/.
"""
import shutil
from pathlib import Path

import folium
import pandas as pd

import import_sheet  # our own data/import_sheet.py
import pages         # our own data/pages.py
import score         # our own data/score.py
import topic_pages   # our own data/topic_pages.py
import analog        # our own data/analog.py (Moon or Mars analog?)
import compare_page  # our own data/compare_page.py
import downloads     # our own data/downloads.py

# Where the website goes.
DOCS = Path(__file__).resolve().parent.parent / "docs"
SITE_PAGES = DOCS / "sites"

# Map background tiles (max zoom level 8 for this layer).
GIBS_TILES = ("https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry"
              "/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg")

def marker_colour(category):
    """Map-marker colour from the site's category (pages.CATEGORIES, shared with the site pages)."""
    return next((colour for start, colour, _, _ in pages.CATEGORIES if str(category).startswith(start)), "green")


# Map filters: each site goes in exactly one group (Moon / Mars / Moon and Mars analogs),
# read from its "Analog for" text by analog.py. The map's checkboxes show or hide each group.


def build_map(earth_sites, targets):
    """World map with a clickable marker for each Earth site."""
    # Background map: NASA GIBS "Blue Marble" imagery (public, no API key).
    # We don't use OpenStreetMap's tile servers: they block pages opened from
    # disk with "403 Access blocked". CARTO tiles now want an API key.
    # Show only one copy of the world: min_zoom stops zooming out too far,
    # max_bounds stops panning past the edges, no_wrap stops repeated tiles.
    world = folium.Map(location=[20, 0], zoom_start=2, min_zoom=1, max_zoom=8,
                       max_bounds=True, tiles=None)
    folium.TileLayer(GIBS_TILES, attr="Imagery: NASA EOSDIS GIBS, Blue Marble",
                     min_zoom=1, max_zoom=8, no_wrap=True, control=False).add_to(world)
    # One layer per filter group; its label says how many sites are in it.
    counts = earth_sites["analog_for"].map(analog.group_name).value_counts()
    groups = {name: folium.FeatureGroup(name=f"{name} ({counts.get(name, 0)})").add_to(world)
              for name in analog.GROUP_NAMES.values()}
    for _, site in earth_sites.iterrows():
        # A site without coordinates can't go on the map; say so instead of guessing.
        if pd.isna(site["lat"]) or pd.isna(site["lon"]):
            print(f"  Skipping on map (no lat/lon): {site['name']}")
            continue
        popup = (f"<b>{pages.show(site['name'])}</b><br>{pages.show(site['category'])}<br>"
                 f"Analog for: {pages.show(site['analog_for'])}<br>"
                 f"<a href='sites/{pages.slugify(site['name'])}.html'>Open site page</a>")
        folium.Marker([site["lat"], site["lon"]], tooltip=pages.show(site["name"]),
                      popup=folium.Popup(popup, max_width=260),
                      icon=folium.Icon(color=marker_colour(site["category"]))
                      ).add_to(groups[analog.group_name(site["analog_for"])])
    # Checkboxes (top right) to show or hide each group.
    folium.LayerControl(collapsed=False).add_to(world)
    # Info box: title, targets, marker legend and links to the other pages.
    target_list = "".join(f"<li>{pages.show(n)}</li>" for n in targets["name"])
    legend = " · ".join(f"{colour}: {text}" for _, colour, _, text in pages.CATEGORIES)
    world.get_root().html.add_child(folium.Element(
        "<div style='position:fixed;bottom:20px;left:20px;z-index:9999;background:white;"
        "padding:8px 12px;border-radius:6px;box-shadow:0 1px 4px #0004;font-family:sans-serif;"
        f"max-width:300px;font-size:14px'><b>Earth analogs for Moon and Mars</b><br>Click a marker "
        f"for the site. Compared with:<ul style='margin:4px 0;padding-left:18px'>{target_list}</ul>"
        f"<small>Markers: {legend}</small><br><a href='compare.html'>Compare sites</a> · <a href='gap.html'>Where Earth falls short</a> · "
        "<a href='tasks.html'>Sites by mission task</a> · <a href='about.html'>About &amp; credits</a></div>"))
    world.save(DOCS / "index.html")


def write(path, html_text):
    path.write_text(html_text, encoding="utf-8")
    print(f"  Wrote {path.relative_to(DOCS.parent)}")


def main():
    # Step 1 and 2: sheet exports -> sites.csv -> scores (also saved to data/scores.csv).
    import_sheet.main()
    sites = score.load_sites()
    # A Moon analog is compared only with the Moon target, a Mars analog only with Mars (analog.py).
    scores = analog.keep_matching(score.compute_scores(sites), sites)
    scores.to_csv(score.SCORES_CSV, index=False)
    earth_sites = sites[sites["type"] == "earth"]
    targets = sites[sites["type"].isin(score.TARGET_TYPES)]
    limits, tasks = topic_pages.load_limits(), topic_pages.load_tasks()

    # Step 3: pages. Old site pages are removed first so a renamed or deleted
    # site doesn't leave a stale page behind.
    SITE_PAGES.mkdir(parents=True, exist_ok=True)
    for old_page in SITE_PAGES.glob("*.html"):
        old_page.unlink()
    for _, site in earth_sites.iterrows():
        write(SITE_PAGES / f"{pages.slugify(site['name'])}.html",
              pages.site_page(site, scores[scores["site"] == site["name"]], sites))
    write(DOCS / "gap.html", topic_pages.gap_page(limits, sites))
    write(DOCS / "compare.html", compare_page.compare_page(sites, scores))
    write(DOCS / "tasks.html", topic_pages.tasks_page(tasks, sites))
    write(DOCS / "about.html", topic_pages.about_page(sites, limits, scores))
    downloads.copy_files(DOCS)  # data CSVs for the About page's download links
    shutil.copy(Path(__file__).parent / "style.css", DOCS / "style.css")  # shared look of all pages

    # Step 4: the map.
    build_map(earth_sites, targets)
    print(f"  Wrote docs/index.html ({len(earth_sites)} Earth sites, {len(targets)} targets)")

    # Step 5: remind us of anything that breaks the challenge rules.
    warnings = score.check_sites(sites) + topic_pages.check_chart_values(limits) + analog.warnings(sites)
    if warnings:
        print(f"\nBEFORE SUBMITTING, fix these {len(warnings)} issue(s):")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\nNo rule warnings (FAKE rows, missing sources, private links, chart numbers).")


if __name__ == "__main__":
    main()
