"""
scores_html.py: the "Similarity scores" part of each site page.

For every scored condition it shows one card per target (the score, plus both
values it compares) and says who measured what. A radar chart is drawn only
when a site has at least 3 scored conditions: with 1 or 2 points it can't be read.
"""
import html
import re

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
    "temp_max_c": "Earth: NASA POWER TS_MAX, the highest hourly ground (skin) temperature in its 2001–2025 record (MERRA-2, ~50 km grid cell). "
                  "Moon: LRO Diviner, Malapert ridge top.",
    "sun_max_elev_deg": sun_angle.SOURCE,
    "slope_deg": "Earth: Copernicus DEM GLO-30 (~30 m pixels; wider east-west near the poles), mean "
                 "slope over a 15 × 15 km box around the site, the size of a NASA Artemis candidate landing region. "
                 "At this pixel size, measurement noise adds about 0.5–1° on flat ground. "
                 "Moon: Wueller et al. 2025, Malapert candidate landing area, 5.6° ± 2.0° (their map "
                 "resolution is not given in the table we used, so the two may not be measured at the "
                 "same pixel size).",
    "slope_463m_deg": "Earth: Copernicus DEM GLO-30 heights averaged into ~463 m blocks, mean slope over a "
                      "15 × 15 km box. Mars: MOLA laser-altimeter map (MEGDR, 128 pixels per degree, ~463 m), "
                      "same box; between laser tracks the map is filled in, so it is smoother than the ground. "
                      "Both sides use the same pixel size, because bigger pixels make slopes look gentler.",
    "dust_aod": "Earth: NASA POWER aerosol optical depth at 0.55 µm (all aerosols: dust, smoke, salt), "
                "2001–2025 average, ~1° (~100 km) grid. Mars: LMD Mars dust climatology from orbiter "
                "measurements (Montabone et al. 2015), Mars Years 24–36 average, 3° (~180 km) grid, for the full local "
                "air column at Arcadia's surface pressure (~830 Pa average, from the Mars Climate Database; not "
                "the 610 Pa reference), 9.3 µm "
                "dust optical depth × 2.6 for the visible-light equivalent (LMD's conversion). Different "
                "wavelengths and grid sizes, so treat the match as approximate.",
    # Ready for when Earth albedo arrives from AppEEARS (not scored yet):
    "albedo": "Earth: MODIS MCD43A3 white-sky shortwave albedo, 2025 average, one 500 m pixel. "
              "Mars: MGS TES bolometric albedo map, one ~7.4 km pixel (8 per degree); dust in the "
              "air was not removed, which can make dark areas look brighter. Moon: no value yet.",
}
UNITS = {"slope_deg": "°", "temp_max_c": " °C", "temp_min_c": " °C", "temp_range_c": " °C",
         "precip_mm_yr": " mm/yr", "dust_aod": "", "sun_max_elev_deg": "°", "slope_463m_deg": "°"}
COLOURS = {"moon_target": "#5a8fd8", "mars_target": "#d9693a"}  # radar colour per target (= pages.MOON/MARS_COLOUR)


def source_for(col, compared):
    """The data label for one condition, without the Moon or Mars part if this site isn't compared with it."""
    parts = re.split(r"\s(?=(?:Moon|Mars): )", DIMENSION_SOURCES.get(col, ""))
    drop = {"Moon: ": "moon_target", "Mars: ": "mars_target"}
    return " ".join(p for p in parts if not any(p.startswith(w) and kind not in compared
                                                for w, kind in drop.items()))


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


def radar_chart(panels):
    """One full-width radar per target (stacked, so they stay readable on phones), each on the
    conditions scored against that target, so every shape closes. panels = [(score row, [columns])]."""
    grid, charts = "#3b4a70", []  # grid colour = style.css --line
    for row, scored in panels:
        labels = [score.DIMENSIONS[col].replace(" (463 m pixels)", "<br>(463 m)") for col in scored]  # fits phones
        values = [row[col] for col in scored]
        hover = [f"{v:.2f}" for v in values]
        fig = go.Figure(go.Scatterpolar(  # repeat the first point at the end so the shape closes
            r=values + values[:1], theta=labels + labels[:1], customdata=hover + hover[:1], name=row["target"],
            fill="toself", line_color=COLOURS[row["target_type"]],
            hovertemplate="%{theta}: %{customdata}<extra>%{fullData.name}</extra>"))
        fig.update_layout(title={"text": f"vs {row['target']}", "x": 0.5, "font": {"size": 15}},
                          polar={"bgcolor": "rgba(0,0,0,0)", "radialaxis": {"range": [0, 1], "gridcolor": grid},
                                 "angularaxis": {"gridcolor": grid}}, height=360, paper_bgcolor="rgba(0,0,0,0)",
                          font={"color": "#e6ebf5", "size": 12}, showlegend=False,
                          margin={"t": 60, "b": 40, "l": 80, "r": 80})
        charts.append(fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True}))
    return "".join(f'<div class="radar">{chart}</div>' for chart in charts)


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
        # Show the range's numbers only if neither end comes from a target this page hides.
        shown = sites[(sites["type"] == "earth") | sites["type"].isin(site_scores["target_type"])]
        lo, hi = sites[col].min(), sites[col].max()
        value_range = (f" ({lo:g} to {hi:g}{UNITS[col]})" if (shown[col].min(), shown[col].max()) == (lo, hi)
                       else "")
        parts.append(f'<div class="tiles">{cards}</div><p class="meta"><strong>Data:</strong> '
                     f'{source_for(col, list(site_scores["target_type"]))} <strong>Scale:</strong> 1 = same value as the '
                     f'target, 0 = as different as anything in our dataset{value_range}.</p>')
    # One radar per target, drawn only when that target has 3+ scored conditions (fewer can't be read).
    panels = [(row, cols) for _, row in site_scores.iterrows()
              if len(cols := [c for c in score.DIMENSIONS if pd.notna(row[c])]) >= 3]
    if panels:
        parts.append(radar_chart(panels))
    parts.append('<p class="meta">Other conditions are not scored yet: we have no exact, '
                 'comparable values for them.</p>')
    return "".join(parts)
