"""
build.py: build the website in docs/ from the research sheet exports in data/.

Steps:
  1. Turn the sheet exports into data/sites.csv (import_sheet.py).
  2. Score every Earth site against every target (score.py).
  3. Write one page per Earth site, the compare, gap, task and About pages.
  4. Write docs/map.html (world map) and docs/index.html (home page: Key findings).
  5. Print warnings about anything to fix before submitting.

Run:  python3 data/build.py   then open docs/index.html (home) or docs/map.html in a browser.
Everything in docs/ is generated: edit the Sheet or these scripts, not docs/.
"""
import json
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
import findings_page # our own data/findings_page.py (home page)
import slides_page   # our own data/slides_page.py (7-slide demo)

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


PLANET_MAP_TABS = "<style>\n#map-target-tabs{position:fixed;top:58px;left:50%;transform:translateX(-50%);z-index:10000;display:flex;gap:8px;padding:8px 10px;background:#26334ff2;border:1px solid #3b4a70;border-radius:12px;box-shadow:0 8px 24px #00000055}\n#map-target-tabs button{padding:7px 14px;border:1px solid #3b4a70;border-radius:8px;background:#1e2a47;color:#eef2f9;font:600 14px system-ui,sans-serif;cursor:pointer}\n#map-target-tabs button[aria-selected=\"true\"]{background:#7db4ff;color:#14203a}\n#planet-map{display:none;position:fixed;top:49px;left:0;right:0;bottom:0;z-index:600;background:#101827}\n#planet-analog-panel{display:none;position:fixed;right:18px;bottom:20px;z-index:8000;width:min(340px,calc(100vw - 36px));max-height:52vh;overflow:auto;padding:12px 14px;background:#26334ff2;color:#eef2f9;border:1px solid #3b4a70;border-radius:12px;box-shadow:0 8px 24px #00000055;font:14px/1.5 system-ui,sans-serif}\n#planet-analog-panel h3{margin:0 0 6px;font-size:16px}\n#planet-analog-panel p{margin:4px 0;color:#c8d2e5;font-size:12px}\n#planet-analog-panel ul{margin:8px 0;padding-left:20px}\n#planet-analog-panel li{margin:5px 0}\n#planet-analog-panel a{color:#9cc4ff}\n@media(max-width:640px){#map-target-tabs{top:54px}#planet-analog-panel{right:8px;bottom:10px;width:calc(100vw - 16px);max-height:38vh}}\n</style>\n<div id=\"map-target-tabs\" role=\"tablist\" aria-label=\"Map body\">\n  <button type=\"button\" role=\"tab\" data-mode=\"earth\" aria-selected=\"true\">Earth sites</button>\n  <button type=\"button\" role=\"tab\" data-mode=\"moon\" aria-selected=\"false\">Moon</button>\n  <button type=\"button\" role=\"tab\" data-mode=\"mars\" aria-selected=\"false\">Mars</button>\n</div>\n<div id=\"planet-map\" aria-label=\"Moon or Mars surface map\"></div>\n<aside id=\"planet-analog-panel\">\n  <h3 id=\"planet-target-title\"></h3>\n  <p id=\"planet-target-note\">Target-body map with its reference target. Earth analogs are listed here because their coordinates belong on an Earth map.</p>\n  <ul id=\"planet-analog-list\"></ul>\n  <p>Basemap: NASA/JPL Solar System Treks. Scores remain separate by condition; see each site page.</p>\n</aside>\n<script>\n(() => {\n  const bodyData = __PLANET_DATA__;\n  const buttons = document.querySelectorAll(\"#map-target-tabs [data-mode]\");\n  const planetDiv = document.getElementById(\"planet-map\");\n  const panel = document.getElementById(\"planet-analog-panel\");\n  const mapInfo = document.querySelector(\".map-info\");\n  const earthMap = document.querySelector(\".folium-map\");\n  const layerControl = document.querySelector(\".leaflet-control-layers\");\n  let planetMap = null;\n  let planetLayer = null;\n  let targetPin = null;\n\n  function setEarthBody(body) {\n    document.querySelectorAll(\".leaflet-control-layers-overlays label\").forEach((label) => {\n      const text = label.textContent || \"\";\n      const both = text.includes(\"Moon and Mars analogs\");\n      const relevant = both || text.includes(body === \"moon\" ? \"Moon analogs\" : \"Mars analogs\");\n      const checkbox = label.querySelector('input[type=\"checkbox\"]');\n      if (checkbox && checkbox.checked !== relevant) checkbox.click();\n    });\n  }\n\n  function fillAnalogPanel(body) {\n    const info = bodyData[body];\n    document.getElementById(\"planet-target-title\").textContent = `${info.body} target: ${info.name}`;\n    const list = document.getElementById(\"planet-analog-list\");\n    list.replaceChildren();\n    info.sites.forEach((site) => {\n      const item = document.createElement(\"li\");\n      const link = document.createElement(\"a\");\n      link.href = site.href;\n      link.textContent = site.name;\n      item.append(link);\n      if (site.scores.length) {\n        item.append(document.createTextNode(\" — \" + site.scores.join(\"; \")));\n      } else {\n        item.append(document.createTextNode(\" — suggested analog; no comparable scores yet\"));\n      }\n      list.append(item);\n    });\n  }\n\n  function showPlanet(body) {\n    const info = bodyData[body];\n    document.body.classList.add(\"planetary-map-open\");\n    if (earthMap) earthMap.style.visibility = \"hidden\";\n    if (mapInfo) mapInfo.style.display = \"none\";\n    if (layerControl) layerControl.style.display = \"none\";\n    planetDiv.style.display = \"block\";\n    panel.style.display = \"block\";\n\n    if (!planetMap) {\n      planetMap = L.map(planetDiv, {\n        crs: L.CRS.EPSG4326,\n        center: [info.lat, info.lon],\n        zoom: 1,\n        minZoom: 0,\n        maxZoom: 8,\n        zoomControl: true,\n        attributionControl: true,\n      });\n    }\n    if (planetLayer) planetMap.removeLayer(planetLayer);\n    planetLayer = L.tileLayer(info.tiles, {\n      tileSize: 256,\n      minZoom: 0,\n      maxZoom: 8,\n      noWrap: false,\n      attribution: info.attribution,\n    }).addTo(planetMap);\n    if (targetPin) planetMap.removeLayer(targetPin);\n    targetPin = L.marker([info.lat, info.lon]).bindTooltip(info.name).addTo(planetMap);\n    planetMap.setView([info.lat, info.lon], 2);\n    fillAnalogPanel(body);\n    window.setTimeout(() => planetMap.invalidateSize(), 80);\n  }\n\n  function showEarth(body = \"moon\") {\n    document.body.classList.remove(\"planetary-map-open\");\n    planetDiv.style.display = \"none\";\n    panel.style.display = \"none\";\n    if (earthMap) earthMap.style.visibility = \"visible\";\n    if (mapInfo) mapInfo.style.display = \"\";\n    if (layerControl) layerControl.style.display = \"\";\n    setEarthBody(body);\n  }\n\n  buttons.forEach((button) => button.addEventListener(\"click\", () => {\n    const mode = button.dataset.mode;\n    buttons.forEach((item) => item.setAttribute(\"aria-selected\", String(item === button)));\n    if (mode === \"earth\") showEarth();\n    else showPlanet(mode);\n  }));\n  showEarth();\n})();\n</script>"
def planet_map_tabs(earth_sites, targets, scores):
    target_rows = {str(row["type"]): row for _, row in targets.iterrows()}
    details = {}
    metrics = {
        "moon_target": (("slope_deg", "Slope score"), ("temp_max_c", "Max-temperature score"), ("sun_max_elev_deg", "Sun-angle score")),
        "mars_target": (("slope_463m_deg", "Slope score"), ("dust_aod", "Dust score"), ("sun_max_elev_deg", "Sun-angle score")),
    }
    for body, target_type in (("moon", "moon_target"), ("mars", "mars_target")):
        target = target_rows.get(target_type)
        candidates = []
        for _, site in earth_sites.iterrows():
            if body not in analog.compared_targets(site["analog_for"]):
                continue
            scored = scores[(scores["site"] == site["name"]) & (scores["target_type"] == target_type)]
            score_row = scored.iloc[0] if not scored.empty else None
            shown_scores = []
            if score_row is not None:
                for column, label in metrics[target_type]:
                    value = score_row.get(column)
                    if pd.notna(value):
                        shown_scores.append(f"{label}: {float(value):.2f}")
            candidates.append({
                "name": str(site["name"]),
                "href": f"sites/{pages.slugify(site['name'])}.html",
                "scores": shown_scores,
            })
        details[body] = {
            "body": "Moon" if body == "moon" else "Mars",
            "name": str(target["name"]) if target is not None else body.title() + " target",
            "lat": float(target["lat"]) if target is not None and pd.notna(target["lat"]) else 0,
            "lon": float(target["lon"]) if target is not None and pd.notna(target["lon"]) else 0,
            "sites": candidates,
            "tiles": (
                "https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/default028mm/{z}/{y}/{x}.jpg"
                if body == "moon" else
                "https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg"
            ),
            "attribution": "Imagery: NASA/JPL Solar System Treks",
        }
    payload = json.dumps(details, ensure_ascii=False).replace("</", "<" + chr(92) + "/")
    return PLANET_MAP_TABS.replace("__PLANET_DATA__", payload)


def build_map(earth_sites, targets, scores):
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
    # Same fonts, stylesheet and nav bar as every other page (style.css: "Map page").
    world.get_root().header.add_child(folium.Element(pages.head_links()))
    world.get_root().html.add_child(folium.Element(
        f"{pages.nav()}<div class='map-info'><b>Earth analogs for Moon and Mars</b><br>Click a marker "
        f"for the site. Compared with:<ul>{target_list}</ul><small>Markers: {legend}</small></div>"))
    world.save(DOCS / "map.html")
    map_path = DOCS / "map.html"
    map_html = map_path.read_text(encoding="utf-8")
    map_html = map_html.replace("</body>", planet_map_tabs(earth_sites, targets, scores) + "\n</body>")
    map_path.write_text(map_html, encoding="utf-8")


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
    build_map(earth_sites, targets, scores)
    print(f"  Wrote docs/map.html ({len(earth_sites)} Earth sites, {len(targets)} targets)")
    write(DOCS / "index.html", findings_page.findings_page(sites, scores, DOCS))  # home page: Key findings
    write(DOCS / "slides.html", slides_page.slides_page(sites, scores, DOCS))  # 7-slide demo
    shutil.copy(Path(__file__).parent / "slides.css", DOCS / "slides.css")

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
