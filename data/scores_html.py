"""
scores_html.py: the "Similarity scores" part of each site page.

For every scored condition it shows one card per target (the score, plus both
values it compares) and says who measured what. A radar chart is drawn only
when a site has at least 3 scored conditions: with 1 or 2 points it can't be read.
"""
import html

import pandas as pd
import plotly.graph_objects as go

import score  # our own data/score.py

# Shown when a site has no real scores at all (project rule: no empty charts).
NOT_SCORED_NOTE = ("Not scored yet. We only score a condition when we have an exact, ground-surface "
                   "value for both this site and a Moon or Mars target. We don't have such a pair "
                   "yet, so we show no chart rather than an empty or misleading one.")

# Who measured what, shown under each scored condition. Keep in step with import_sheet.py.
DIMENSION_SOURCES = {
    "temp_max_c": "Earth: NASA POWER skin temperature (MERRA-2, ~50 km grid). "
                  "Moon: LRO Diviner, Malapert ridge top.",
}
UNITS = {"slope_deg": "°", "temp_max_c": " °C", "temp_min_c": " °C", "temp_range_c": " °C",
         "precip_mm_yr": " mm/yr", "dust_aod": ""}
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


def scores_section(site, site_scores, sites):
    """Score cards (and a radar chart if 3+ conditions are scored) for one Earth site."""
    scored = [col for col in score.DIMENSIONS if site_scores[col].notna().any()]
    if not scored:
        return f'<p class="meta">{NOT_SCORED_NOTE}</p>'
    parts = []
    for col in scored:
        cards = "".join(score_card(col, site, sites[sites["name"] == row["target"]].iloc[0], row[col])
                        for _, row in site_scores.iterrows())
        value_range = f"{sites[col].min():g} to {sites[col].max():g}{UNITS[col]}"
        parts.append(f'<div class="tiles">{cards}</div><p class="meta"><strong>Data:</strong> '
                     f'{DIMENSION_SOURCES.get(col, "")} <strong>Scale:</strong> 1 = same value as the '
                     f'target, 0 = as different as anything in our dataset ({value_range}).</p>')
    if len(scored) >= 3:
        parts.append(radar_chart(site_scores))
    parts.append('<p class="meta">Other conditions are not scored yet: we have no exact, '
                 'comparable values for them.</p>')
    return "".join(parts)


# NASA POWER's requested citation (from power.larc.nasa.gov/docs/referencing/).
POWER_CSV = score.DATA_DIR / "power_skin_temps.csv"
POWER_REFERENCE = ("The data was obtained from National Aeronautics and Space Administration (NASA) "
                   "Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project "
                   "funded through the NASA Earth Science Division.")


def power_credit():
    """About page section: POWER's citation, version, access date and each site's exact request."""
    if not POWER_CSV.exists():
        return ""
    power = pd.read_csv(POWER_CSV)
    first = power.iloc[0]
    requests = "".join(f'<li>{html.escape(r.site)}: <a href="{html.escape(r.request_url)}">'
                       f'{html.escape(r.request_url)}</a></li>' for r in power.itertuples())
    return (f'<section class="card"><h2>Ground temperatures: NASA POWER</h2><p>{POWER_REFERENCE}</p>'
            f'<p>Data reference: {html.escape(first["api"])}, accessed {html.escape(first["accessed"])}. '
            f'Parameter TS_MAX ({html.escape(first["TS_MAX_definition"])}), annual climatology, '
            f'source MERRA-2 (~50 km grid). Home: <a href="https://power.larc.nasa.gov">power.larc.nasa.gov</a></p>'
            f'<details><summary>Exact request for each site</summary><ul>{requests}</ul></details></section>')
