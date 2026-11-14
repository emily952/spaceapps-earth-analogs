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

## 6. Submission (check the official Space Apps rules)

- [ ] What exactly must be submitted (project page, video, slides, demo link)?
- [ ] Which time zone does the deadline use?
- [ ] Space Apps rules on AI use and disclosure (our README already has a
  "Use of AI" section; keep it updated).
- [ ] Data terms: every provider we used is credited.
- [ ] No NASA logos, insignia or mission patches anywhere.
