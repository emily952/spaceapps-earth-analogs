# Team decisions and open questions

Things we need to decide or find out. When something is settled, tick it,
write the decision and who agreed, and commit. Deadline: **Sun Nov 15, 11:59 PM**.

## 1. Targets (decide first: every score depends on these)

- [x] **Which Artemis III candidate region** is our Moon target, and its lat/lon?
  Decision: Malapert Massif (−86, 0.3). Lunar south pole shadowed craters are a
  reference row only, used on the gap page.
- [x] **Which Mars ice landing zone** is our Mars target, and its lat/lon?
  Decision: Arcadia Planitia (47.2, −175.7).
- [x] **Point or area?** Is a target (and each Earth site) one point, or an average
  over an area? If an area, how big?
  Decision: Point. Each Earth site and Moon/Mars target is represented by one named location and a representative point (coordinate). The coordinate is used for mapping and point-based data requests.

## 2. How to measure each column (so all rows compare like with like)

> **Status (Nov 15):** one condition is scored: **max ground temperature vs Malapert**.
> Earth: NASA POWER annual TS_MAX (maximum hourly skin temperature, MERRA-2 ~50 km
> grid; `data/fetch_power.py`). Moon: LRO Diviner 47 °C at the Malapert ridge top.
> Scores range from 0.98 (Qaidam, Atacama) to 0.20 (East Antarctic Plateau); 10 of 12
> sites score ≥ 0.80, so this score mainly separates cold sites from hot ones.
> Arcadia has no ground-temperature value (only Viking *air* temperatures): "no data".
> Malapert's slope (5.6°) is in the sheet but not scored: no Earth slope values yet.
> No radar charts until a site has 3+ scored conditions; scores show as cards.
> Note: POWER's grid smooths extremes (Lut 63.86 °C vs the 80.8 °C satellite record).

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

## 7. How we'll be judged (official Judging & Awards Guide)

Source: https://www.spaceappschallenge.org/resources/judging-awards-guide
Each criterion is scored 1 to 5, at every level of judging.

- **Impact:** how big a problem it addresses and how many it could help or inspire.
- **Creativity:** originality; a new idea or a meaningful improvement on existing ones.
- **Validity:** scientifically sound, feasible, complete, and *usable and user-friendly*.
- **Relevance:** answers the challenge directly; **NASA data is a core part, not an add-on**.
- **Presentation:** clear story of the challenge, solution and why it matters. "Judges
  evaluate the demo and full project", and the guide says teams often underweight this one.

Global awards that fit us best: **Best Use of Data** ("makes space data accessible or
leverages it to a unique application"), **Best Use of Science** ("most valid use of the
scientific method"), **Best Storytelling**.
