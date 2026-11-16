"""
compare_page.py: the "Compare sites" page (docs/compare.html).

It puts all 12 Earth sites side by side:
  1. A dot chart of each site's max ground temperature, with a line at the
     Moon target's value, so you can see at a glance who comes closest.
  2. A table of every site with its scores against each target, best first.
Each condition is shown on its own: we never add scores into one overall number.
"""
import pandas as pd
import plotly.graph_objects as go

import pages        # our own data/pages.py
import score        # our own data/score.py
import scores_html  # our own data/scores_html.py

DOT_COLOUR = "#2a78d6"   # Earth sites (same blue as the gap chart)
LINE_COLOUR = "#5b6474"  # the target's value: neutral grey, so it doesn't look like a site


def short_name(name):
    """'Lut Desert (Dasht-e Lut), Iran' -> 'Lut Desert': short enough for a chart label."""
    return str(name).split(",")[0].split(" (")[0]


def temp_chart(earth, target, site_scores):
    """Dot per Earth site (hottest 8-day ground temperature) and a dashed line at the target's value."""
    rows = earth.dropna(subset=["temp_max_c"]).sort_values("temp_max_c")
    # Hover text: full name, value and score, so nothing depends on reading colour.
    hover = [f"{pages.show(r['name'])}<br>{r['temp_max_c']:g} °C<br>Score vs {pages.show(target['name'])}: "
             f"{site_scores.get(r['name'], float('nan')):.2f}" for _, r in rows.iterrows()]
    fig = go.Figure(go.Scatter(
        x=rows["temp_max_c"], y=[short_name(n) for n in rows["name"]], mode="markers",
        marker={"size": 11, "color": DOT_COLOUR, "line": {"width": 2, "color": "#fff"}},
        hovertext=hover, hoverinfo="text"))
    # The Moon target's value as a dashed line with its own label.
    fig.add_vline(x=target["temp_max_c"], line_dash="dash", line_width=2, line_color=LINE_COLOUR,
                  annotation_text=f"{pages.show(target['name'])}: {target['temp_max_c']:g} °C",
                  annotation_position="top")
    fig.update_layout(height=460, margin={"l": 10, "r": 20, "t": 40, "b": 40}, plot_bgcolor="#fff",
                      xaxis={"title": "Hottest 8-day ground temperature, 2025 (°C)", "gridcolor": "#eee",
                             "zeroline": False},
                      yaxis={"gridcolor": "#f2f2f2"}, showlegend=False)
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def score_cell(value):
    """A score as a number with a small bar behind it (CSS only), or 'no data'."""
    if pd.isna(value):
        return '<td class="muted">no data</td>'
    return (f'<td><span class="bar"><span style="width:{value * 100:.0f}%"></span></span>'
            f'{value:.2f}</td>')


def score_table(earth, scores, targets, col):
    """One row per Earth site: its value, then one score column per target (best first)."""
    wide = scores.pivot(index="site", columns="target", values=col)
    first = targets.iloc[0]["name"]
    earth = earth.assign(sort=earth["name"].map(wide[first])).sort_values("sort", ascending=False)
    head = "".join(f"<th>Score vs {pages.show(t)}</th>" for t in targets["name"])
    body = ""
    for _, site in earth.iterrows():
        link = f'<a href="sites/{pages.slugify(site["name"])}.html">{pages.show(site["name"])}</a>'
        cells = "".join(score_cell(wide.loc[site["name"], t]) for t in targets["name"])
        body += (f"<tr><td>{link}</td><td>{pages.category_badge(site['category'])}</td>"
                 f"<td>{pages.show(site['analog_for'])}</td>"
                 f"<td>{scores_html.fmt(site[col], col)}</td>{cells}</tr>")
    return (f'<div class="scroll"><table class="compare"><tr><th>Site</th><th>Category</th>'
            f"<th>Analog for</th><th>{score.DIMENSIONS[col]}</th>{head}</tr>{body}</table></div>")


def compare_page(sites, scores):
    """The whole page. Only conditions that have at least one real score are shown."""
    earth = sites[sites["type"] == "earth"]
    targets = sites[sites["type"].isin(score.TARGET_TYPES)]
    moon = targets[targets["type"] == "moon_target"].iloc[0]
    moon_scores = scores[scores["target"] == moon["name"]].set_index("site")["temp_max_c"]
    scored = [col for col in score.DIMENSIONS if scores[col].notna().any()]
    tables = "".join(f'<section class="card"><h2>{score.DIMENSIONS[col]}</h2>'
                     f'<p class="meta"><strong>Data:</strong> {scores_html.DIMENSION_SOURCES.get(col, "")}</p>'
                     f"{score_table(earth, scores, targets, col)}</section>" for col in scored)
    return pages.page("Compare sites", f"""
<h1>Compare sites</h1>
<p class="lead">All {len(earth)} Earth sites side by side. Each condition is compared on its own:
we don't add scores into one overall ranking, because a site can be a great analog for one
test and a poor one for another.</p>
<section class="card"><h2>How close does each site get to {pages.show(moon['name'])}'s hottest ground?</h2>
{temp_chart(earth, moon, moon_scores)}
<p class="meta">Each dot is one site's hottest 8-day average of clear-sky daytime readings in 2025
(MODIS Aqua, which passes over at about 1:30 pm local time), one 1 km pixel at the site. The dashed line is
{pages.show(moon['name'])}'s ridge top measured by LRO Diviner. The closer a dot is to the line, the higher
the score. Averaging over 8 days lowers the peaks: single MODIS readings of 80.8 °C have been recorded
in the Lut Desert.</p></section>
{tables}
<p class="meta">Scale: 1 = same value as the target, 0 = as different as anything in our dataset.
Click a site for its matches, limits and sources. "no data" means we have no exact, comparable value:
we never estimate one.</p>""")
