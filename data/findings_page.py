"""
findings_page.py: the home page (docs/index.html): the problem, who it is for, and the
headline findings, with buttons into the rest of the site. The map is docs/map.html.

Every number here is looked up from the current data when the site is built, so the
page can't go out of date when the data changes. Scores are never combined: each
finding is about one condition and one target.
"""
import html
import shutil

import pages        # our own data/pages.py
import score        # our own data/score.py
import scores_html  # our own data/scores_html.py (units)
import sun_angle    # our own data/sun_angle.py
import topic_pages  # our own data/topic_pages.py (coldest-surface numbers checked against the Sheet)


def best_matches(sites, scores, target_name):
    """For each scored condition: the closest site to this target (only sites compared with it)."""
    target = sites[sites["name"] == target_name].iloc[0]
    rows = scores[scores["target"] == target_name]
    lines = []
    for col, label in score.DIMENSIONS.items():
        if rows[col].notna().any():
            unit, top = scores_html.UNITS[col], rows[col].round(2).max()
            tied = rows[rows[col].round(2) == top]  # every site sharing the best (rounded) score
            names = " and ".join(
                f'<a href="sites/{pages.slugify(s)}.html">{html.escape(s.split(",")[0])}</a> '
                f'({sites.loc[sites["name"] == s, col].iloc[0]:g}{unit})' for s in tied["site"])
            lines.append(f"<li><strong>{label}:</strong> {names} vs {target[col]:g}{unit}; score {top:.2f}</li>")
    return "".join(lines)


def site_finder(docs):
    """The team's "Find a site" chat widget (data/site_finder.html). It needs data/match.js,
    so it is only added once that file exists; otherwise the button would do nothing."""
    if not (score.DATA_DIR / "match.js").exists():
        print("  Site finder widget skipped: data/match.js not found (add it to switch the widget on).")
        return ""
    shutil.copy(score.DATA_DIR / "match.js", docs / "match.js")
    return (score.DATA_DIR / "site_finder.html").read_text(encoding="utf-8")


def findings_page(sites, scores, docs):
    """HTML for docs/index.html."""
    earth = sites[sites["type"] == "earth"]
    moon = sites[sites["type"] == "moon_target"].iloc[0]
    mars = sites[sites["type"] == "mars_target"].iloc[0]
    # How many different sites come out best, across all conditions and targets.
    winners = {scores.loc[scores[scores["target"] == t][c].idxmax(), "site"]
               for t in (moon["name"], mars["name"]) for c in score.DIMENSIONS
               if scores[scores["target"] == t][c].notna().any()}
    cold = {label: value for label, value, *_ in topic_pages.COLD_BARS}
    earth_cold, moon_cold = cold["Earth: East Antarctic Plateau"], cold["Moon: shadowed crater floors"]
    buttons = "".join(f'<a class="button{extra}" href="{href}">{text}</a>' for href, text, extra in [
        ("map.html", "Explore the map", ""), ("compare.html", "Compare all sites", " ghost"),
        ("gap.html", "Where Earth falls short", " ghost"), ("about.html", "How we score &amp; sources", " ghost")])
    return pages.page("Earth Analogs for Moon and Mars", f"""
<section class="hero"><p class="eyebrow">NASA Space Apps 2026 · Earth analogs</p><h1>Where on Earth can we rehearse the Moon and Mars?</h1>
<p class="lead">Before astronauts land near the Moon's south pole or on Mars, crews, rovers and instruments
practise in similar places on Earth. We compared {len(earth)} Earth sites with two targets, one condition at a
time, so mission planners and field-test teams can see <strong>which site to use for which test</strong>, and
where no place on Earth can help.</p>{buttons}</section>
<div class="grid"><section class="card moon-card"><h2>Moon: {html.escape(moon['name'])}</h2>
<p class="meta">An Artemis candidate landing region near the lunar south pole.</p>
<p>Closest Earth site for each condition:</p><ul>{best_matches(sites, scores, moon['name'])}</ul></section>
<section class="card mars-card"><h2>Mars: {html.escape(mars['name'])}</h2>
<p class="meta">A flat, ice-rich plain proposed for future landings.</p>
<p>Closest Earth site for each condition:</p><ul>{best_matches(sites, scores, mars['name'])}</ul></section></div>
<section class="card"><h2>No single best analog</h2><p>{len(winners)} different sites come out on top across the
conditions we score. That's why we never add scores into one ranking: pick the site that matches the
test you need to run.</p></section>
<section class="card break"><h2>Where Earth falls short</h2><ul>
<li><strong>Low Sun:</strong> nowhere on Earth does the Sun's highest point of the year stay below 23.4°;
at {html.escape(moon['name'])} it never rises above {moon['sun_max_elev_deg']:.1f}°.</li>
<li><strong>Cold:</strong> Earth's coldest surface (about {earth_cold} °C) is about {earth_cold - moon_cold} °C
warmer than the Moon's shadowed craters ({moon_cold} °C).</li>
<li><strong>Everywhere:</strong> {pages.LIMITS_NOTE}</li></ul>
<p><a href="gap.html">See every condition Earth can't match →</a></p></section>
<p class="meta">Each condition is scored from 0 (as different as anything in our data) to 1 (same as the
target), using NASA data (MODIS, LRO Diviner, MOLA, POWER, planetary fact sheets), ESA's Copernicus DEM and
the LMD Mars dust climatology (built from NASA orbiter data). Sites are scored only against the target they are an analog for.
<a href="about.html">Method, sources and downloads.</a></p>""", extra=site_finder(docs))
