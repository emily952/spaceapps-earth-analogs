# Space Apps 2026: Earth Analogs for Moon and Mars

## What this project is
Our team's entry for the NASA Space Apps Challenge 2026 challenge "Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars."
We score Earth sites against Moon and Mars targets (an Artemis III south pole region and a Mars ice landing zone) on several dimensions, then show the results as an interactive map and a radar chart per site.
Deadline: Sunday Nov 15, 11:59 PM local time. Simple and working beats ambitious and broken.

## Stack (do not add anything else)
- Python 3 with pandas, folium, plotly only.
- No JavaScript frameworks, no servers, no databases.
- The output is static HTML files in `docs/`, published by GitHub Pages.

## Folder layout
- `data/sites.csv`: input data, exported from our team Google Sheet. One row per site or target.
- `data/score.py`: computes the 0 to 1 similarity scores per dimension.
- `data/build.py`: reads the scores, writes `docs/index.html` (map) and one radar chart page per site.
- `docs/`: generated website. Do not hand-edit generated files.
- `notes/`: site write-ups and citations (plain markdown).

## CSV columns
name, type (earth / moon_target / mars_target), lat, lon, slope_deg, temp_max_c, temp_min_c, temp_range_c, precip_mm_yr, dust_aod, matches, breaks, source_links

## Scoring rules
- Score each dimension separately: 1 = same value as the target, 0 = as different as anything in the dataset.
  Formula: score = 1 - abs(earth_value - target_value) / (max - min of that column across all rows), clipped to 0..1.
- Never combine dimensions into one overall number unless a teammate asks.
- A blank cell means "no data": skip it and show "no data" in charts. Never invent, estimate or fill in values.
- Every site page must show the "matches" and "breaks" text, plus a fixed note that Earth cannot reproduce lunar or Martian gravity, vacuum or thin atmosphere, or radiation.

## How to work
- Always run `git pull` before changing anything.
- Make small changes and commit after each working step, with a clear message.
- Comment every step in plain English. A teammate who knows basic Python must be able to follow it.
- Keep each script short (aim for under 150 lines).
- After a change, run `python3 data/build.py` and confirm `docs/index.html` opens in a browser.
- Do not use NASA logos, insignia or mission patches anywhere.

## AI disclosure
This code is written with AI assistance (Claude Code, Cursor) and reviewed by the team. Keep the README's "Use of AI" section up to date.
