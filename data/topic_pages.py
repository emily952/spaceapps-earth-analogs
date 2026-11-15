"""
topic_pages.py: the "Where Earth falls short" page (docs/gap.html) and the
"Sites by mission task" page (docs/tasks.html).

Inputs: data/earths_limits.csv and data/mission_tasks.csv (tabs of the research
sheet), plus the "(reference)" row of data/targets.csv.
"""
import re

import plotly.graph_objects as go

import import_sheet  # our own data/import_sheet.py (reads the tab exports)
import pages         # our own data/pages.py (shared HTML helpers)
import score         # our own data/score.py

LIMITS_CSV = score.DATA_DIR / "earths_limits.csv"
TASKS_CSV = score.DATA_DIR / "mission_tasks.csv"
LIMIT_COLUMNS = ["Condition", "Moon", "Mars", "Earth's closest", "Where on Earth",
                 "Can Earth match it?", "What it means for testing"]
TASK_COLUMNS = ["Mission task", "What matters most", "Candidate sites (draft, team to decide)",
                "Moon, Mars or both"]

# Bar chart numbers, copied from the Earth's limits tab: (label, °C, row, column).
# check_chart_values() makes sure each number still appears in that cell,
# so if the sheet changes the build warns instead of showing an old number.
COLD_BARS = [
    ("Moon: shadowed crater floors", -233, "Coldest surface", "Moon"),
    ("Mars: poles", -153, "Coldest surface", "Mars"),
    ("Earth: East Antarctic Plateau", -98, "Coldest surface", "Earth's closest"),
    ("Moon: long-lit polar spots (±10)", -50, "Temperature in long-lit lunar polar spots", "Moon"),
]
EARTH_COLOUR, SPACE_COLOUR = "#eb6834", "#2a78d6"  # validated pair (dataviz palette check)


def load_limits():
    return import_sheet.read_tab(LIMITS_CSV, LIMIT_COLUMNS + ["Source URLs (plain text)"])


def load_tasks():
    return import_sheet.read_tab(TASKS_CSV, TASK_COLUMNS)


def check_chart_values(limits):
    """Warn if a chart number no longer appears in the sheet cell it came from."""
    warnings = []
    for label, value, condition, column in COLD_BARS:
        cell = limits.loc[limits["Condition"] == condition, column]
        if cell.empty or str(value) not in str(cell.iloc[0]):
            warnings.append(f"Gap chart: {value} °C ({label}) no longer matches the Earth's limits tab. "
                            "Update COLD_BARS in data/topic_pages.py.")
    return warnings


def cold_chart():
    """Horizontal bar chart of the coldest surface temperatures; Earth's bar in orange."""
    labels = [label for label, *_ in COLD_BARS]
    values = [value for _, value, *_ in COLD_BARS]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h", text=[f"{v} °C" for v in values], textposition="outside",
        marker_color=[EARTH_COLOUR if label.startswith("Earth") else SPACE_COLOUR for label in labels],
        hovertemplate="%{y}: %{x} °C<extra></extra>"))
    fig.update_layout(height=320, margin={"l": 10, "r": 30, "t": 10, "b": 40}, barcornerradius=4,
                      bargap=0.35, plot_bgcolor="#fff", yaxis={"autorange": "reversed"},
                      xaxis={"title": "Surface temperature (°C)", "range": [-270, 0], "gridcolor": "#eee"})
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def gap_page(limits):
    """Where no Earth site comes close, and what that means for testing."""
    header = "".join(f"<th>{pages.show(col)}</th>" for col in LIMIT_COLUMNS)
    rows = "".join("<tr>" + "".join(f"<td>{pages.show(row[col])}</td>" for col in LIMIT_COLUMNS) + "</tr>"
                   for _, row in limits.iterrows())
    sources = "".join(f"<h3>{pages.show(row['Condition'])}</h3>"
                      f"{pages.link_list(score.split_links(row['Source URLs (plain text)']))}"
                      for _, row in limits.iterrows())
    reference = "".join(
        f"<h3>Reference: {pages.show(r['Target'])}</h3><p>{pages.show(r['Surface temperature'])}. "
        f"{pages.show(r['Ice and water'])}.</p>{pages.link_list(score.split_links(r['Source URLs (plain text)']))}"
        for _, r in import_sheet.reference_rows().iterrows())
    return pages.page("Where Earth falls short", f"""
<h1>Where Earth falls short</h1>
<p>Some Moon and Mars conditions have no match anywhere on Earth. Tests that depend on them need
laboratory chambers or other methods, not field sites.</p>
<h2>Coldest surfaces</h2>
<p>Earth's coldest measured surface (about −98 °C, East Antarctic Plateau) is colder than sunlit
lunar polar spots, but about 135 °C warmer than the Moon's shadowed craters.</p>
{cold_chart()}
<h2>Condition by condition</h2><div class="scroll"><table><tr>{header}</tr>{rows}</table></div>
<p class="note"><strong>Limits of any Earth analog:</strong> {pages.LIMITS_NOTE}</p>
{reference}
<h2>Sources</h2>{sources}""")


def link_sites(cell, earth_names):
    """Turn 'Kharga yardangs; Lut Desert' into links to those sites' pages, where we can match them."""
    parts = []
    for part in [p.strip() for p in str(cell).split(";") if p.strip()]:
        short = re.sub(r"\s*\(.*?\)", "", part).strip()  # drop notes in brackets before matching
        match = next((name for name in earth_names if name.startswith(short)), None)
        parts.append(f'<a href="sites/{pages.slugify(match)}.html">{pages.show(part)}</a>' if match
                     else pages.show(part))
    return "<br>".join(parts)


def tasks_page(tasks, sites):
    """Which sites suit which mission tests. Team judgment, not computed from scores."""
    earth_names = list(sites.loc[sites["type"] == "earth", "name"])
    rows = "".join(
        f"<tr><td>{pages.show(t['Mission task'])}</td><td>{pages.show(t['What matters most'])}</td>"
        f"<td>{link_sites(t['Candidate sites (draft, team to decide)'], earth_names)}</td>"
        f"<td>{pages.show(t['Moon, Mars or both'])}</td></tr>" for _, t in tasks.iterrows())
    return pages.page("Sites by mission task", f"""
<h1>Sites by mission task</h1>
<p>A good place to test rover driving is not the same as a good place to test dust mitigation.
This table pairs mission tasks with candidate sites. <strong>These pairings are our team's
judgment</strong>, based on each site's features; they are not computed from scores.</p>
<div class="scroll"><table><tr><th>Mission task</th><th>What matters most</th><th>Candidate sites</th>
<th>Moon, Mars or both</th></tr>{rows}</table></div>""")
