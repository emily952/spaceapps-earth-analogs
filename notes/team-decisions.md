# Team decisions and open questions

Things we need to decide or find out. When something is settled, tick it,
write the decision and who agreed, and commit. Deadline: **Sun Nov 15, 11:59 PM**.

## 1. Targets (decide first: every score depends on these)

- [ ] **Which Artemis III candidate region** is our Moon target, and its lat/lon?
  Decision:
- [ ] **Which Mars ice landing zone** is our Mars target, and its lat/lon?
  Decision:
- [ ] **Point or area?** Is a target (and each Earth site) one point, or an average
  over an area? If an area, how big?
  Decision:

## 2. How to measure each column (so all rows compare like with like)

- [ ] **Temperature type**: ground surface temperature for every row (matches Diviner)?
  Recommended: yes. Decision:
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

- [ ] Final list of Earth sites (how many? aim for quality over quantity).
- [ ] Who researches which site (one owner per row in the Google Sheet).
- [ ] Every site has `matches`, `breaks` and `source_links` filled in.
- [ ] A write-up in `notes/` for each site? (Not linked from the website yet.)

## 4. Scoring: things to be aware of

- [ ] **Scores depend on the whole dataset.** "0" means "as different as anything in
  our dataset", so adding or removing a site can change everyone's scores. Fine,
  but we should say so in the presentation.
- [ ] **The Moon will dominate temperature.** Lunar polar temperatures are so extreme
  that every Earth site may score low on them. That's honest, not a bug.
- [ ] **Overall score?** Project rule: no combined score unless the team asks.
  Do we want one? Decision:

## 5. Website and code

- [ ] Review and merge the `sample-data-pipeline` branch into `main`.
- [ ] Turn on GitHub Pages (Settings → Pages → branch `main`, folder `/docs`).
- [ ] Who exports the Google Sheet to `data/sites.csv`, and when is the final export?
- [ ] **Remove all FAKE rows** before submitting.
- [ ] Add a credits/about section listing data providers?
- [ ] Check the site on a phone.
- [ ] `data/build.py` is at the 150-line limit: move site-page code into its own
  file before adding more features.

## 6. Submission rules (official)

> - Deadline: Sun Nov 15, 11:59 PM local time
> - Demo: 30-second video (English subtitles) or max 7 slides
> - AI disclosure required, AI images watermarked, no NASA logos
> - Every source cited
> - Public links only

- [ ] **Demo format**: 30-second video with English subtitles, OR at most 7 slides.
  Decision:  Owner:
- [ ] **AI disclosure**: README "Use of AI" section is up to date. Also add a
  one-line AI note on the website itself?
- [ ] **AI images**: any AI-generated image (slides, video, site) carries a visible
  watermark. We have none in the repo so far.
- [ ] **No NASA logos**: none in the repo. The map uses NASA GIBS satellite
  *imagery* (not a logo), credited in the map's corner. Check slides and video too.
- [ ] **Every source cited**: every CSV row has `source_links`; also credit the
  map imagery (NASA GIBS Blue Marble) and tools (Leaflet/folium, plotly) in the
  demo. A credits section on the site would help.
- [ ] **Public links only**: every link in `source_links` and the demo must open
  without logging in. No links to our private Google Sheet. The GitHub repo
  and GitHub Pages site must be public.
- [ ] Final check that nothing FAKE is left (see section 5).
