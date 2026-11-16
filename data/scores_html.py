"""
scores_html.py: the "Similarity scores" part of each site page.

For every scored condition it shows one card per target (the score, plus both
values it compares) and says who measured what. A radar chart is drawn only
when a site has at least 3 scored conditions: with 1 or 2 points it can't be read.
"""
import html

import pandas as pd
import plotly.graph_objects as go

import score      # our own data/score.py
import sun_angle  # our own data/sun_angle.py

# Shown when a site has no real scores at all (project rule: no empty charts).
NOT_SCORED_NOTE = ("Not scored yet. We only score a condition when we have an exact, ground-surface "
                   "value for both this site and a Moon or Mars target. We don't have such a pair "
                   "yet, so we show no chart rather than an empty or misleading one.")

# Who measured what, shown under each scored condition. Keep in step with import_sheet.py.
DIMENSION_SOURCES = {
    "temp_max_c": "Earth: MODIS Aqua land surface temperature (MYD11A2), hottest 8-day average "
                  "of clear-sky ~1:30 pm readings in 2025, one 1 km pixel. "
                  "Moon: LRO Diviner, Malapert ridge top.",
    "sun_max_elev_deg": sun_angle.SOURCE,
    "slope_deg": "Earth: Copernicus DEM GLO-30 (~30 m pixels; wider east-west near the poles), mean "
                 "slope over a 15 × 15 km box around the site, the size of an Artemis III landing region. "
                 "At this pixel size, measurement noise adds about 0.5–1° on flat ground. "
                 "Moon: Wueller et al. 2025, Malapert candidate landing area, 5.6° ± 2.0° (their map "
                 "resolution is not given in the table we used, so the two may not be measured at the "
                 "same pixel size).",
    # Ready for when Earth albedo arrives from AppEEARS (not scored yet):
    "albedo": "Earth: MODIS MCD43A3 white-sky shortwave albedo, 2025 average, one 500 m pixel. "
              "Mars: MGS TES bolometric albedo map, one ~7.4 km pixel (8 per degree); dust in the "
              "air was not removed, which can make dark areas look brighter. Moon: no value yet.",
}
UNITS = {"slope_deg": "°", "temp_max_c": " °C", "temp_min_c": " °C", "temp_range_c": " °C",
         "precip_mm_yr": " mm/yr", "dust_aod": "", "sun_max_elev_deg": "°"}
COLOURS = {"moon_target": "#7f8c8d", "mars_target": "#c0392b"}  # radar chart colour per target type


def fmt(value, col):
    """A measured value with its unit, or 'no data'."""
    return "no data" if pd.isna(value) else f"{value:g}{UNITS[col]}"


def score_card(col, site, target, value):
    """One card: the score for one condition against one target, or why there is none."""
    title = f"{score.DIMENSIONS[col]} vs {html.escape(str(target['name']))}"
    if pd.isna(value):
        why = ("no exact ground-surface value for this target yet" if pd.isna(target[col])
               else "no exact value for this site yet")
        return (f'<div class="tile"><div class="tile-title">{title}</div>'
                f'<div class="big muted">no data</div><p class="meta">{why}</p></div>')
    return (f'<div class="tile"><div class="tile-title">{title}</div><div class="big">{value:.2f}</div>'
            f'<p class="meta">This site {fmt(site[col], col)} · target {fmt(target[col], col)}</p></div>')


def radar_chart(site_scores, scored):
    """Radar chart with one shape per target, on the scored conditions only. Missing scores leave a gap."""
    labels = [score.DIMENSIONS[col] for col in scored]
    fig = go.Figure()
    for _, row in site_scores.iterrows():
        values = [row[col] for col in scored]
        hover = ["no data" if pd.isna(v) else f"{v:.2f}" for v in values]
        # Repeat the first point at the end so the shape closes.
        fig.add_trace(go.Scatterpolar(
            r=values + values[:1], theta=labels + labels[:1], customdata=hover + hover[:1],
            name=row["target"], fill="toself", line_color=COLOURS[row["target_type"]],
            hovertemplate="%{theta}: %{customdata}<extra>%{fullData.name}</extra>"))
    fig.update_layout(polar={"radialaxis": {"range": [0, 1]}}, height=480,
                      legend={"orientation": "h"}, margin={"t": 30, "b": 30})
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def scores_section(site, site_scores, sites):
    """Score cards (and a radar chart if 3+ conditions are scored) for one Earth site."""
    names = " and ".join(html.escape(str(t)) for t in site_scores["target"])
    only = " only" if len(site_scores) == 1 else ""
    intro = (f'<p class="meta">Compared with {names}{only}, because this site is listed as an analog for '
             f'{html.escape(str(site["analog_for"]))}.</p>')
    scored = [col for col in score.DIMENSIONS if site_scores[col].notna().any()]
    if not scored:
        return f'{intro}<p class="meta">{NOT_SCORED_NOTE}</p>'
    parts = [intro]
    for col in scored:
        cards = "".join(score_card(col, site, sites[sites["name"] == row["target"]].iloc[0], row[col])
                        for _, row in site_scores.iterrows())
        value_range = f"{sites[col].min():g} to {sites[col].max():g}{UNITS[col]}"
        parts.append(f'<div class="tiles">{cards}</div><p class="meta"><strong>Data:</strong> '
                     f'{DIMENSION_SOURCES.get(col, "")} <strong>Scale:</strong> 1 = same value as the '
                     f'target, 0 = as different as anything in our dataset ({value_range}).</p>')
    if len(scored) >= 3:
        parts.append(radar_chart(site_scores, scored))
    parts.append('<p class="meta">Other conditions are not scored yet: we have no exact, '
                 'comparable values for them.</p>')
    return "".join(parts)


# MODIS citation (from the top of fetch_modis.py). One example request per site is in modis_lst.csv.
MODIS_CSV = score.DATA_DIR / "modis_lst.csv"
MODIS_REFERENCE = ("ORNL DAAC. 2018. MODIS and VIIRS Land Product Subsets RESTful Web Service. "
                   "https://doi.org/10.3334/ORNLDAAC/1600 . Product MYD11A2 v6.1 (Wan, Hook, Hulley).")


def modis_credit():
    """About page section: MODIS citation, product, year, access date and each site's example request."""
    if not MODIS_CSV.exists():
        return ""
    modis = pd.read_csv(MODIS_CSV)
    first = modis.iloc[0]
    requests = "".join(f'<li>{html.escape(r.site)}: <a href="{html.escape(r.example_request_url)}">'
                       f'{html.escape(r.example_request_url)}</a></li>' for r in modis.itertuples())
    return (f'<section class="card"><h2>Ground temperatures: MODIS (1 km)</h2><p>{html.escape(MODIS_REFERENCE)}</p>'
            f'<p>Product MYD11A2 v6.1 (MODIS Aqua, 8-day land surface temperature, band LST_Day_1km), '
            f'year 2025, accessed {html.escape(first["accessed"])}. For each site we keep the hottest '
            f'8-day average of clear-sky daytime readings (Aqua passes about 1:30 pm local time) in the '
            f'one 1 km pixel at its coordinates. Service: <a href="https://modis.ornl.gov">modis.ornl.gov</a></p>'
            f'<p class="meta">We first used NASA POWER (~50 km grid cell) and switched to MODIS because it is the '
            f'smallest Earth temperature data on the challenge Resources list that covers all 12 sites without '
            f'a login. The POWER download is kept in our repository for reference; it is not scored.</p>'
            f'<details><summary>Example request for each site</summary><ul>{requests}</ul></details></section>')
