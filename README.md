# Earth Analogs for Moon and Mars

NASA Space Apps Challenge 2026 entry. We compare 12 Earth sites with a Moon target
(Malapert Massif, an Artemis candidate landing region from NASA's "Artemis III candidate regions" list) and a Mars target (Arcadia Planitia,
an ice-rich plain): what matches, where each falls short, which mission tests each
could support, and which Moon/Mars conditions no place on Earth can match.

## How it fits together

```
Google Sheet tabs  ->  import_sheet.py  ->  sites.csv  ->  score.py  ->  build.py  ->  docs/
(exported as CSV)      (copies text)                       (0-1 scores)  (website)
```

The website (`docs/`): a **Key findings** home page (`index.html`), a map (`map.html`, with
Moon/Mars filter checkboxes), one page per
site (`sites/`), **Compare sites** (`compare.html`: all sites side by side),
**Where Earth falls short** (`gap.html`), **Sites by mission task** (`tasks.html`) and
**About & credits** (`about.html`). A site gets a radar chart only once it has real
scores; until then its page says "Not scored yet" and why.

| Path | What it is |
|---|---|
| `data/site_options.csv`, `targets.csv`, `earths_limits.csv`, `mission_tasks.csv`, `datasets.csv` | The research sheet's tabs, exported as CSV. **These are the inputs.** |
| `data/import_sheet.py` | Turns `site_options.csv` + `targets.csv` into `data/sites.csv` |
| `data/fetch_modis.py` | MODIS 8-day (MYD11A2) temperatures into `data/modis_lst.csv`. Reference only: replaced by the daily AppEEARS data |
| `data/fetch_power.py` | NASA POWER (~50 km) skin temperatures into `data/power_skin_temps.csv`. Kept for reference only: no longer scored |
| `data/appeears_points.csv` | Our 12 sites as a point file for NASA AppEEARS (ID, Category, Latitude, Longitude) |
| `data/scores_html.py` | The score cards on site pages and the MODIS citation |
| `data/sites.csv` | Generated: one row per site or target. **Don't hand-edit.** |
| `data/score.py` | Computes similarity scores (writes `data/scores.csv`) and checks the data |
| `data/pages.py` | Shared HTML helpers and each site page |
| `data/fetch_slope.py` | Average slope in a 15 × 15 km box per site from Copernicus DEM GLO-30 → `data/copernicus_slope.csv` (scored vs Malapert's 5.6°; also saves 1 km and 5 km boxes) |
| `data/fetch_mars_slope.py` | Arcadia's slope from NASA MOLA (463 m pixels) and Earth slopes averaged to the same pixel size → `data/slope_463m.csv` (scored vs Arcadia) |
| `data/fetch_dust.py` | Dust/haze optical depth: Earth from NASA POWER AOD_55, Mars from the LMD Mars dust climatology → `data/dust_aod.csv`, `data/mars_dust.csv` (scored vs Arcadia) |
| `data/sun_angle.py` | Calculates each row's highest Sun angle from latitude and axial tilt (scored, Moon and Mars) |
| `data/downloads.py` | The About page's "How we score" (with a live worked example) and "Download our data" (copies CSVs to `docs/data/`) |
| `data/read_appeears.py` | Reads AppEEARS results: daily MODIS temperature (MYD11A1 → `modis_daily_lst.csv`, **the scored Earth max temperature**) or ground brightness (MCD43A3, not scored yet) |
| `data/appeears/` | AppEEARS request record, metadata and README (citations) for the daily MODIS file |
| `data/fetch_tes_albedo.py` | Arcadia's ground brightness (albedo 0.236) from NASA's TES map (one ~7.4 km pixel; dust in the air not removed) → `data/mars_albedo.csv` (not scored until Earth albedo, 500 m MODIS pixels, arrives) |
| `data/analog.py` | Decides which target(s) each site is compared with, from its "Analog for" text (Moon / Mars / both); a typo shows both and triggers a build warning |
| `data/findings_page.py` | The home page: the problem, who it's for and the best match per condition, computed from the live scores |
| `data/compare_page.py` | The Compare sites page: a temperature dot chart and a score table for all sites |
| `data/topic_pages.py` | HTML for the gap page (with its chart), the task page and the About & credits page |
| `data/style.css` | The look of every page except the map (copied to `docs/` by the build) |
| `data/build.py` | Runs all of the above and prints warnings about anything that breaks the challenge rules |
| `docs/` | Generated website for GitHub Pages. **Don't hand-edit.** |
| `notes/` | Site write-ups and citations (markdown) |
| `notes/data-sources.md` | Where to get data for each CSV column |
| `notes/nasa-data-field.md` | Text for the submission form's NASA Data field |
| `notes/submission.md` | Draft of every Space Apps submission field, the 7-slide outline and the rule check |
| `notes/link-check.md` | Results of checking every external link, with suggested replacements |
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

1. Edit the research Google Sheet. Don't rename column headers: the import checks them
   and stops with a clear message if one changed.
2. Export each changed tab (File → Download → CSV) and save it over the matching file
   in `data/` (`site_options.csv`, `targets.csv`, `earths_limits.csv`, `mission_tasks.csv`).
3. Put several source links in the "Source URLs (plain text)" cell separated by `;`.
   Links must be public (open without logging in).
4. **Scores so far:** vs Arcadia: **slope at 463 m** (`data/fetch_mars_slope.py`) and **dust** (`data/fetch_dust.py`); **slope** vs Malapert (Copernicus DEM GLO-30, 15 × 15 km box = the size of a NASA Artemis
   candidate landing region; `data/fetch_slope.py`); (a) **highest Sun angle** vs Malapert *and* Arcadia, calculated in
   `data/sun_angle.py` from latitude and axial tilt (NASA planetary fact sheets; no download);
   (b) max ground temperature vs Malapert. Earth values come from
   MODIS Aqua daily land surface temperature, MYD11A1 v6.1: the hottest good-quality daily reading in 2025 (Aqua, ~1:30 pm local), one 1 km pixel,
   extracted with NASA AppEEARS (`data/earth-analogs-lst-2025-MYD11A1-061-results.csv`,
   request record in `data/appeears/`) and read by `data/read_appeears.py MYD11A1` →
   `data/modis_daily_lst.csv`. Days are kept only if MODLAND quality is 00/01 and the LST
   error is 2 K or less. History: NASA POWER (~50 km cell), then MODIS 8-day averages
   (MYD11A2, `data/fetch_modis.py`); both kept for reference only. Malapert's value comes from the Targets tab column
   "Max ground surface temp (°C)" (LRO Diviner). Each score shows as a card; a
   radar chart appears once a site has 3 or more scored conditions.
   **To score more conditions:** add columns named exactly `slope_deg`, `temp_max_c`,
   `temp_min_c`, `temp_range_c`, `precip_mm_yr` or `dust_aod` to the Site options and
   Targets tabs, holding plain numbers (ground-surface values only). A site is scored
   on a column only when both it and a target have a number there. Leave cells
   **blank** when there's no exact value. Never guess.
5. Run `build.py` and read the **"BEFORE SUBMITTING"** list it prints (missing sources,
   links that may need a login, gap-chart numbers that no longer match the sheet).
   Fix them, check the site, commit.

The gap chart's four numbers are copied into `COLD_BARS` in `data/topic_pages.py`.
The build warns if the Earth's limits tab no longer contains them.

## How scores work

For each dimension separately:
`score = 1 - |earth_value - target_value| / (max - min of that column across all rows)`, clipped to 0..1.
1 = same as the target, 0 = as different as anything in our dataset.
We never combine dimensions into one overall score.

Every site page also notes that no Earth site can reproduce lunar or Martian gravity,
vacuum or thin atmosphere, or radiation.

## Use of AI

AI tools helped with this project's research and coding. Team members verified
the sources and reviewed the code.
- **Coding:** Claude Code wrote the first versions of `data/score.py`,
  `data/build.py`, `data/pages.py`, the notes in `notes/` and this README.
  Cursor was also used. The team reviewed the code.
- **Research:** Claude (chat) did background research and compiled the research spreadsheet, research doc and source list; the team reviewed them, chose the targets and sites, and made the method decisions.
  Team members checked the source links before the numbers were used.
- The website's About page (`docs/about.html`) repeats this disclosure. If you
  change one, change the `AI_NOTE` text in `data/pages.py` too.
