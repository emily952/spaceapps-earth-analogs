"""
build.py: build the website in docs/ from data/sites.csv.

Steps:
  1. Score every Earth site against every target (score.py).
  2. Write one page per Earth site, plus docs/about.html (HTML is in pages.py).
  3. Write docs/index.html: a world map with one marker per Earth site.
  4. Print warnings about anything to fix before submitting.

Run:  python3 data/build.py   then open docs/index.html in a browser.
Everything in docs/ is generated: edit the CSV or these scripts, not docs/.
"""
from pathlib import Path

import folium
import pandas as pd

import pages  # our own data/pages.py
import score  # our own data/score.py

# Where the website goes.
DOCS = Path(__file__).resolve().parent.parent / "docs"
SITE_PAGES = DOCS / "sites"

# Map background tiles (max zoom level 8 for this layer).
GIBS_TILES = ("https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry"
              "/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg")


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
                     min_zoom=1, max_zoom=8, no_wrap=True).add_to(world)
    for _, site in earth_sites.iterrows():
        # A site without coordinates can't go on the map; say so instead of guessing.
        if pd.isna(site["lat"]) or pd.isna(site["lon"]):
            print(f"  Skipping on map (no lat/lon): {site['name']}")
            continue
        popup = (f"<b>{pages.show(site['name'])}</b><br>"
                 f"<a href='sites/{pages.slugify(site['name'])}.html'>Open radar chart</a>")
        folium.Marker([site["lat"], site["lon"]], tooltip=pages.show(site["name"]),
                      popup=folium.Popup(popup, max_width=250)).add_to(world)
    # Small info box: title, which targets the sites are compared with, About link.
    target_list = "".join(f"<li>{pages.show(n)}</li>" for n in targets["name"])
    world.get_root().html.add_child(folium.Element(
        "<div style='position:fixed;bottom:20px;left:20px;z-index:9999;background:white;"
        "padding:8px 12px;border-radius:6px;box-shadow:0 1px 4px #0004;font-family:sans-serif;"
        f"max-width:300px'><b>Earth analogs for Moon and Mars</b><br>Click a marker for its "
        f"scores.<br>Compared against:<ul style='margin:4px 0;padding-left:18px'>{target_list}</ul>"
        "<a href='about.html'>About, sources &amp; credits</a></div>"))
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
        page = SITE_PAGES / f"{pages.slugify(site['name'])}.html"
        page.write_text(pages.site_page(site, scores[scores["site"] == site["name"]]), encoding="utf-8")
        print(f"  Wrote {page.relative_to(DOCS.parent)}")
    (DOCS / "about.html").write_text(pages.about_page(sites), encoding="utf-8")
    print("  Wrote docs/about.html")

    # Step 3: the map.
    build_map(earth_sites, targets)
    print(f"  Wrote docs/index.html ({len(earth_sites)} Earth sites, {len(targets)} targets)")

    # Step 4: remind us of anything that breaks the challenge rules.
    warnings = score.check_sites(sites)
    if warnings:
        print(f"\nBEFORE SUBMITTING, fix these {len(warnings)} issue(s):")
        for warning in warnings:
            print(f"  - {warning}")


if __name__ == "__main__":
    main()
