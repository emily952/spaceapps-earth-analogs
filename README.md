# Earth Analogs for Moon and Mars

NASA Space Apps Challenge 2026 entry. We score Earth sites against a Moon target
(Artemis III south pole region) and a Mars target (ice landing zone), one dimension
at a time, and show the results as an interactive map with a radar chart per site.

> **Current data is FAKE.** `data/sites.csv` holds placeholder rows for testing.
> Replace them with the export from the team Google Sheet.

## How it fits together

```
data/sites.csv  ->  data/score.py  ->  data/build.py  ->  docs/index.html (map)
(team sheet)        (0-1 scores)       (makes website)    docs/sites/*.html (radar charts)
```

| Path | What it is |
|---|---|
| `data/sites.csv` | Input data, one row per Earth site or Moon/Mars target |
| `data/score.py` | Computes similarity scores; also writes `data/scores.csv` |
| `data/build.py` | Builds the website in `docs/` (runs the scoring itself) |
| `docs/` | Generated website for GitHub Pages. **Don't hand-edit.** |
| `notes/` | Site write-ups and citations (markdown) |
| `notes/data-sources.md` | Where to get data for each CSV column |
| `notes/team-decisions.md` | Open questions and decisions the team still needs to make |

## Run it

```bash
git pull
python3 -m venv .venv              # first time only
.venv/bin/pip install -r requirements.txt   # first time only
.venv/bin/python data/build.py
open docs/index.html               # macOS; or double-click the file
```

## Updating the data

1. Export the team Google Sheet as CSV and save it over `data/sites.csv`.
2. Keep the column names exactly:
   `name, type, lat, lon, slope_deg, temp_max_c, temp_min_c, temp_range_c, precip_mm_yr, dust_aod, matches, breaks, source_links`
3. `type` must be `earth`, `moon_target` or `mars_target`.
4. Leave a cell **blank** if we have no data. Never guess a value. Blanks show as "no data".
5. Put several source links in one cell separated by `;`.
6. Run `build.py`, check the map, then commit.

## How scores work

For each dimension separately:
`score = 1 - |earth_value - target_value| / (max - min of that column across all rows)`, clipped to 0..1.
1 = same as the target, 0 = as different as anything in our dataset.
We never combine dimensions into one overall score.

Every site page also notes that no Earth site can reproduce lunar or Martian gravity,
vacuum or thin atmosphere, or radiation.

## Use of AI

This code is written with AI assistance (Claude Code, Cursor) and reviewed by the team.
- Claude Code wrote the first versions of `data/score.py`, `data/build.py`, the
  FAKE sample `data/sites.csv` and this README.
- All site data, write-ups and citations are gathered and checked by team members.
