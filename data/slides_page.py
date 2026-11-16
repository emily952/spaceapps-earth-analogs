"""
slides_page.py: our 7-slide demo (docs/slides.html), the "Project Demonstration" link.

Seven full-screen slides in one page. Scroll, or press Space / the arrow keys, to move
between them (CSS scroll-snap, no JavaScript). All numbers come from the live data, so the
slides always match the website. No NASA logos and no AI-generated images: the only
picture is a screenshot of our own map page (data/slides_map.png, NASA GIBS imagery).
"""
import html
import shutil

import pages        # our own data/pages.py
import score        # our own data/score.py
import topic_pages  # our own data/topic_pages.py (coldest-surface numbers checked against the Sheet)

SITE = "https://emily952.github.io/spaceapps-earth-analogs/"
REPO = "https://github.com/emily952/spaceapps-earth-analogs"


def best(sites, scores, target, col):
    """(site name, Earth value, score) of the closest site to a target on one condition."""
    rows = scores[(scores["target"] == target) & scores[col].notna()]
    row = rows.loc[rows[col].idxmax()]
    site = sites[sites["name"] == row["site"]].iloc[0]
    short = site["name"].split(",")[0].split(" (")[0].split(" and ")[0]  # e.g. "Harrat Khaybar"
    return short, site[col], row[col]


def result(label, name, value, unit, target_value, score_value):
    """One finding: condition, site, the two values, and the score as a bar."""
    return (f'<div class="result"><div class="cond">{label}</div><div class="site">{html.escape(name)}</div>'
            f'<div class="vals">{value:g}{unit} vs {target_value:g}{unit}</div>'
            f'<div class="sbar"><span style="width:{score_value * 100:.0f}%"></span></div>'
            f'<div class="score">{score_value:.2f}</div></div>')


def slides_page(sites, scores, docs):
    """Write docs/slides.html (and copy the map screenshot next to it)."""
    shutil.copy(score.DATA_DIR / "slides_map.png", docs / "slides_map.png")
    moon = sites[sites["type"] == "moon_target"].iloc[0]
    mars = sites[sites["type"] == "mars_target"].iloc[0]
    earth = sites[sites["type"] == "earth"]
    cold = {label: value for label, value, *_ in topic_pages.COLD_BARS}
    moon_results = "".join(result(label, *best(sites, scores, moon["name"], col)[:2], unit, moon[col],
                                  best(sites, scores, moon["name"], col)[2])
                           for col, label, unit in [("temp_max_c", "Hottest ground", " °C"),
                                                    ("slope_deg", "Slope", "°")])
    mars_results = "".join(result(label, *best(sites, scores, mars["name"], col)[:2], unit, mars[col],
                                  best(sites, scores, mars["name"], col)[2])
                           for col, label, unit in [("slope_463m_deg", "Slope", "°"), ("dust_aod", "Dusty air", "")])
    slides = [
        f"""<p class="kicker">Project JES · NASA Space Apps 2026</p>
<h1>Where on Earth can we rehearse the Moon and Mars?</h1>
<p class="big-lead">We compared {len(earth)} places on Earth with a landing region at the Moon's south pole
and an icy plain on Mars, one condition at a time.</p>
<p class="link">{SITE}</p>""",
        f"""<p class="kicker">The question</p>
<h2>Crews and rovers practise on Earth first. But which site is like the target, and in what way?</h2>
<div class="two"><div class="target moon"><h3>{html.escape(moon['name'])}, Moon</h3>
<p>Artemis candidate landing region near the south pole. The Sun never climbs above
{moon['sun_max_elev_deg']:.1f}°. Ridge-top ground reaches {moon['temp_max_c']:g} °C.</p></div>
<div class="target mars"><h3>{html.escape(mars['name'])}, Mars</h3>
<p>Flat, ice-rich plain at {mars['lat']:g}°N, proposed for future landings. Average slope {mars['slope_463m_deg']:g}°.</p></div></div>""",
        f"""<p class="kicker">12 sites</p>
<h2>Ten of our sites are lesser-known analogs, from Kamil Crater in Egypt to the Qaidam Basin in China.</h2>
<img src="slides_map.png" alt="Map of our 12 Earth analog sites">""",
        """<p class="kicker">How we score</p>
<h2>Each condition gets its own score from 0 to 1, and a site is only compared with the body it stands in for.</h2>
<p class="formula">score = 1 − |Earth − target| / (largest − smallest in our data)</p>
<p>Data: NASA POWER, MOLA and LRO Diviner, the NASA planetary fact sheets, ESA's Copernicus elevation model
and the LMD Mars dust maps. If we have no comparable number, the site says "no data". We never add scores up.</p>""",
        f"""<p class="kicker">What we found</p>
<h2>There is no single best analog. It depends on the test.</h2>
<div class="two"><div class="col-moon"><h3 class="moon-t">vs {html.escape(moon['name'])}</h3>{moon_results}</div>
<div class="col-mars"><h3 class="mars-t">vs {html.escape(mars['name'])}</h3>{mars_results}</div></div>""",
        f"""<p class="kicker">Where Earth falls short</p>
<h2>Some tests can't happen outdoors anywhere on Earth.</h2>
<div class="two"><div class="fact"><div class="num">23.4°</div><p>is the lowest the Sun's highest point of
the year gets anywhere on Earth. At Malapert it never rises above {moon['sun_max_elev_deg']:.1f}°.</p></div>
<div class="fact"><div class="num">{cold['Earth: East Antarctic Plateau'] - cold['Moon: shadowed crater floors']} °C</div>
<p>warmer: Earth's coldest surface ({cold['Earth: East Antarctic Plateau']} °C) vs the Moon's shadowed craters
({cold['Moon: shadowed crater floors']} °C).</p></div></div>
<p>Low gravity, vacuum, thin air and space radiation need chambers and other methods.</p>""",
        f"""<p class="kicker">Try it</p>
<h2>Every number on the site links back to its source, and the data can be downloaded.</h2>
<p class="link">{SITE}</p><p class="small">Code and data: {REPO}</p>
<p class="small">Next: ground brightness (albedo), a measured Mars ground temperature, more sites.</p>
<p class="small">AI tools (Claude, Claude Code, Cursor) helped with research and code. Our team chose the sites
and sources and made the method decisions. No AI-generated images are used.</p>""",
    ]
    body = "".join(f'<section class="slide" id="s{i}"><div class="inner">{s}</div><div class="count">{i} / {len(slides)}</div></section>'
                   for i, s in enumerate(slides, start=1))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Project JES: 7-slide demo</title>{pages.head_links()}
<link rel="stylesheet" href="slides.css"></head><body class="deck">{body}</body></html>"""
