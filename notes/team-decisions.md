# Team decisions and open questions

Things we need to decide or find out. When something is settled, tick it,
write the decision and who agreed, and commit. Deadline: **Sun Nov 15, 11:59 PM**.

## 1. Targets (decide first: every score depends on these)

- [x] **Which Artemis III candidate region** is our Moon target, and its lat/lon?
  Decision: Malapert Massif (−86, 0.3). Lunar south pole shadowed craters are a
  reference row only, used on the gap page.
- [x] **Which Mars ice landing zone** is our Mars target, and its lat/lon?
  Decision: Arcadia Planitia (47.2, −175.7).
- [ ] **Point or area?** Is a target (and each Earth site) one point, or an average
  over an area? If an area, how big?
  Decision:

## 2. How to measure each column (so all rows compare like with like)

> **Status (Nov 15):** no site can be scored yet, so no radar charts are shown. The
> targets have no exact ground-surface values: Malapert's −50 ± 10 °C is a general
> figure for sunlit polar spots, and Arcadia's figures are Viking *air* temperatures.
> To get charts, someone needs ground-surface numbers for a target (e.g. Diviner for
> Malapert) and for Earth sites (e.g. MODIS land surface temperature), entered in
> plain-number columns. See "Updating the data" in the README.

- [x] **Temperature type**: ground surface temperature for every row (matches Diviner).
  Decision: yes. Air temperatures stay in the text only.
- [x] **Precipitation upper bounds** ("<30", "<4"): Decision: blank in scoring,
  kept word for word in the site pages' "Climate and conditions" notes.
- [ ] **Max/min meaning**: the most extreme value ever recorded, or the average daily
  max/min? Over which years?
  Decision:
- [ ] **`temp_range_c`**: always calculate it as max − min in the sheet, so it can't
  disagree with the other two columns?
  Recommended: yes. Decision:
- [ ] **Slope**: average slope over what area, at what map resolution?
  Decision:
- [ ] **Precipitation on the Moon and Mars**: enter 0 (with a citation), or leave
  blank ("no data")? Mars does get frost and snow, so 0 may be wrong there.
  Decision:
- [ ] **Dust on the Moon**: the Moon has no atmosphere. Blank or 0?
  Decision:
- [ ] **Dust on Mars**: compare Mars dust opacity with Earth AOD despite the
  wavelength difference, or leave Mars dust blank?
  Decision:

## 3. Earth sites

- [x] Final list of Earth sites: the 12 in the research sheet (10 new finds,
  2 baselines: Atacama and Haughton Crater).
- [x] Every site has matches, breaks and source links filled in.
- [ ] **Check each source link opens and supports its number** (the sheet's own rule).
- [ ] **Swap weak sources where possible.** Some links are to a tour company
  (Kharga rainfall), a camping site listing (Río Tinto coordinates), Wondermondo
  (Atacama coordinates), volcanodb and Wikipedia. They're public, but judges may
  trust primary sources more.
- [ ] **Small fix in the Earth's limits tab**, "Hottest surface" row: Lut's 80.8 °C
  is about 19 °C short of the Moon's "over 100 °C", not "at least 20 °C".
- [x] Mission tasks: shown on the site as a table labelled "team judgment".
  Review the pairings before submitting.

## 4. Scoring: things to be aware of

- [ ] **Scores depend on the whole dataset.** "0" means "as different as anything in
  our dataset", so adding or removing a site can change everyone's scores. Fine,
  but we should say so in the presentation.
- [ ] **The Moon will dominate temperature.** Lunar polar temperatures are so extreme
  that every Earth site may score low on them. That's honest, not a bug.
- [ ] **Overall score?** Project rule: no combined score unless the team asks.
  Do we want one? Decision:

## 5. Website and code

- [x] Review and merge the `sample-data-pipeline` branch into `main`.
- [ ] Turn on GitHub Pages (Settings → Pages → branch `main`, folder `/docs`).
- [ ] Who does the final export of the sheet tabs into `data/`, and when?
- [x] **Remove all FAKE rows.** Done: real sheet data replaced them.
- [x] Gap page (`docs/gap.html`) and task page (`docs/tasks.html`) built from the sheet.
- [x] Add a credits/about section listing data providers. Done: `docs/about.html`,
  built automatically from every row's `source_links`.
- [ ] Check the site on a phone.
- [x] `data/build.py` was at the 150-line limit. Done: page HTML moved to `data/pages.py`.
- [x] `build.py` now prints a "BEFORE SUBMITTING" list (FAKE rows, missing
  sources, links that may need a login).

## 6. Submission rules (official)

> - Deadline: Sun Nov 15, 11:59 PM local time
> - Demo: 30-second video (English subtitles) or max 7 slides
> - AI disclosure required, AI images watermarked, no NASA logos
> - Every source cited
> - Public links only

- [ ] **Demo format**: 30-second video with English subtitles, OR at most 7 slides.
  Decision:  Owner:
- [x] **AI disclosure**: README "Use of AI" section, repeated on the website's
  About page. Also mention it in the video or slides.
- [ ] **AI images**: any AI-generated image (slides, video, site) carries a visible
  watermark. We have none in the repo so far.
- [ ] **No NASA logos**: none in the repo. The map uses NASA GIBS satellite
  *imagery* (not a logo), credited in the map's corner. Check slides and video too.
- [ ] **Every source cited**: every CSV row has `source_links`; also credit the
  map imagery (NASA GIBS Blue Marble) and tools (Leaflet/folium, plotly) in the
  demo. The site's About page lists all of these automatically.
- [ ] **Public links only**: every link in `source_links` and the demo must open
  without logging in. No links to our private Google Sheet. The GitHub repo
  and GitHub Pages site must be public.
- [x] Final check that nothing FAKE is left. `build.py` warns if any row says FAKE.
