# Space Apps submission: draft of every field

Draft written from what is in the repo on Nov 15. **Re-check the numbers after the last
data change** (they come from `data/scores.csv` and `data/sites.csv`). Edit freely.

---

## Project name (pick one)

1. **Earth Analogs for Moon and Mars** (current name; plain and searchable)
2. **Stand-ins: Where Earth Can (and Can't) Rehearse the Moon and Mars**
3. **Analog Atlas: Scoring Earth Sites Against Malapert and Arcadia**

## High-level summary (under 100 words)

Before astronauts work on the Moon or Mars, crews and machines practise in similar places
on Earth. We compared 12 Earth sites, including 10 lesser-known ones, with Malapert Massif
(a candidate landing region near the Moon's south pole) and Arcadia Planitia (an ice-rich
Mars plain). Using NASA and partner data, we score each site from 0 to 1 on slope, hottest
ground temperature and highest Sun angle, one condition at a time. An interactive map,
site pages and a "Where Earth falls short" page show what matches, what doesn't, and what
no place on Earth can reproduce.

## Links

- Final project (website): https://emily952.github.io/spaceapps-earth-analogs/
- Code and data (GitHub repository): https://github.com/emily952/spaceapps-earth-analogs

## Project details

**What it does.** A static website with:
- a world map of 12 Earth analog sites, filterable by Moon analogs, Mars analogs or both;
- a page per site (what matches, where it breaks, key facts, geology, suggested mission
  tests, similarity scores, sources);
- a Compare page with all sites side by side;
- a "Where Earth falls short" page with the conditions no Earth site can match;
- a mission-task table (team judgment, labelled as such);
- an About page with the scoring method, every source and downloadable data.

**Targets.**
- **Moon: Malapert Massif** (−86°, 0.3°), one of the regions on NASA's "Artemis III
  candidate regions" list (Oct 2024). We call it an Artemis candidate landing region:
  NASA has since moved the first crewed landing to a later Artemis mission.
- **Mars: Arcadia Planitia** (47.2°N, 175.7°W), an ice-rich plain proposed for future landings.

**How it works.** The team keeps its research in a spreadsheet. Python scripts (pandas,
numpy, folium, plotly) import it, download satellite data, compute the scores and write
the website as static HTML, published with GitHub Pages. No servers or databases.

**Scoring method.** For each condition separately:
`score = 1 − |Earth value − target value| / (largest − smallest value in our data)`, kept
between 0 and 1. 1 = same as the target; 0 = as different as anything in our data.
- We never add conditions into one overall score: a site can suit one test and not another.
- A condition with no exact, comparable value shows "no data". We never estimate.
- Each site is compared only with the body it is an analog for (Moon, Mars or both),
  taken from the team's "Analog for" column.

**What is scored.**

| Condition | Earth side | Target side |
|---|---|---|
| Hottest ground temperature | MODIS Aqua MYD11A1 (daily, via NASA AppEEARS): hottest good-quality daily reading in 2025 (Aqua, ~1:30 pm local), one 1 km pixel | Malapert 47 °C, LRO Diviner (McClanahan et al.) |
| Slope | Copernicus DEM GLO-30 (~30 m): mean slope over a 15 × 15 km box (the size of a NASA Artemis candidate landing region) | Malapert 5.6° ± 2.0° (Wueller et al. 2025) |
| Highest Sun angle | Calculated: 90° − max(0, \|latitude\| − axial tilt) | Malapert 5.54°, Arcadia 67.99° (tilts from NASA fact sheets) |

**Key findings.**
- **Hottest ground (Moon):** Lonar Crater, India comes closest to Malapert (52.0 vs 47 °C;
  score 0.95). The East Antarctic Plateau is the furthest (0.27).
- **Slope (Moon):** Harrat Khaybar, Saudi Arabia is the closest of the Moon-analog sites
  (3.8° vs 5.6°; 0.83).
- **Sun angle (Mars):** Western Qaidam Basin, China and Río Tinto, Spain match Arcadia
  best (about 75° vs 68°; 0.91), because they lie at a similar latitude.
- **Where Earth falls short:**
  - Nowhere on Earth is the highest Sun lower than 23.4°, so Malapert's 5.5° Sun (long
    shadows, glare) can't be found on Earth.
  - Earth's coldest surface (about −98 °C) is about 135 °C warmer than the Moon's shadowed craters.
  - Gravity, vacuum or thin atmosphere, and radiation can't be reproduced anywhere on Earth.

**Limitations.**
- **Only a few conditions are scored.** Arcadia is scored on Sun angle only: we found no
  comparable Mars ground temperature or slope for it.
- **Temperatures are measured differently.** Earth is the hottest reading at one fixed
  time of day (~1:30 pm), averaged over a 1 km pixel; Malapert is Diviner's maximum.
  Cloudy and low-quality days are dropped (about half the year at Lonar: 185 of 365 days, mostly monsoon cloud).
- **Slope depends on the box and pixel size.** At 30 m, measurement noise adds about
  0.5–1° on flat ground, and Malapert's source doesn't state its map resolution.
- **Sun angle is calculated, not measured.** It assumes a flat horizon.
- **Scores are relative to our own dataset:** adding a site shifts every score a little.
- **Each place is one point.** Three Earth coordinates are approximate.

**Future work.**
- Ground brightness (albedo): Arcadia's value (0.236, MGS TES) is ready; Earth's needs MODIS MCD43A3.
- A Mars ground temperature for Arcadia, and minimum temperatures for both targets.
- More sites, and a global "analog finder" that scores every place on Earth.

## NASA data used

| Dataset | What for | Link |
|---|---|---|
| MODIS Aqua daily land surface temperature, MYD11A1 v6.1 (doi:10.5067/MODIS/MYD11A1.061), via NASA AppEEARS (LP DAAC) | Earth hottest ground temperature (scored) | https://appeears.earthdatacloud.nasa.gov |
| MODIS 8-day MYD11A2 via ORNL DAAC | Earlier temperature source; reference only, not scored | https://modis.ornl.gov |
| LRO Diviner surface temperatures (via McClanahan et al., arXiv 2303.03911) | Malapert 47 °C maximum (scored); shadowed-crater cold (gap page) | https://arxiv.org/abs/2303.03911 |
| NASA planetary fact sheets (NSSDC) | Axial tilts for Sun angle (scored); gravity and pressure (text) | https://nssdc.gsfc.nasa.gov/planetary/factsheet/ |
| NASA release 22-089 (Artemis candidate regions, ~15 × 15 km) | Size of the slope box | https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/ |
| NASA EOSDIS GIBS, Blue Marble | Map background imagery | https://nasa-gibs.github.io/gibs-api-docs/ |
| NASA Earth Observatory | Lut, Harrat Khaybar and Bodélé write-ups | https://science.nasa.gov/earth/earth-observatory/ |
| Viking lander meteorology (PDS) | Mars air temperature, text only (not scored) | https://arcnav.psi.edu/urn:nasa:pds:context:instrument:met.vl2 |
| MGS TES bolometric albedo map (PDS Geosciences) | Arcadia albedo, prepared, not yet scored | https://pds-geosciences.wustl.edu/missions/mgs/tesspecial.html |
| NASA POWER (MERRA-2) | First temperature source; kept for reference, not scored | https://power.larc.nasa.gov |

## Space agency partner data

| Dataset | Agency | What for | Link |
|---|---|---|---|
| Copernicus DEM GLO-30 (doi:10.5270/ESA-c5d3d65) | ESA / European Union | Earth slope (scored) | https://copernicus-dem-30m.s3.amazonaws.com/readme.html |
| Mars Express | ESA | Arcadia dust devils; Mars facts (text) | https://www.esa.int/Science_Exploration/Space_Science/Mars_Express/Earth_tones_on_Mars |

## References

The website's About page lists every link automatically. ⚠ marks links that were dead on
Nov 15 (see [link-check.md](link-check.md)); fix them in the Sheet before submitting.

**Data and method**
- Christensen, P. R. et al. (2001), MGS Thermal Emission Spectrometer experiment, *JGR* 106(E10), doi:10.1029/2000JE001370
- McClanahan, T. P. et al., Evidence for widespread hydrogen sequestration within the Moon's south polar cold traps, arXiv:2303.03911
- Wueller et al. (2025), *JGR Planets*, doi:10.1029/2025JE009127
- Wan, Z., Hook, S., & Hulley, G. (2021), MODIS/Aqua Land Surface Temperature/Emissivity Daily L3 Global 1km SIN Grid V061, NASA LP DAAC, doi:10.5067/MODIS/MYD11A1.061
- AppEEARS Team (2026), Application for Extracting and Exploring Analysis Ready Samples (AppEEARS), Ver. 3.137, NASA EOSDIS LP DAAC, https://appeears.earthdatacloud.nasa.gov
- ORNL DAAC (2018), MODIS and VIIRS Land Product Subsets RESTful Web Service, doi:10.3334/ORNLDAAC/1600 (8-day data, reference only)
- Copernicus DEM GLO-30, ESA / European Union, doi:10.5270/ESA-c5d3d65
- NASA (2022), release 22-089; NASA (2024), "NASA Provides Update on Artemis III Moon Landing Regions"
- NASA POWER: "The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division." (reference only)

**Per site and target** (from the research sheet)
- **Kamil Crater:** https://www.earth-prints.org/handle/2122/7013 ; https://fieldmuseum.org/digitization-gebel-kamil
- **Kharga yardangs:** https://www.usgs.gov/publications/eolian-features-western-desert-egypt-and-some-applications-mars ; https://ntrs.nasa.gov/citations/19840015443
- **Lut Desert:** https://science.nasa.gov/earth/earth-observatory/irans-lut-desert-153634 ; ⚠ https://modarch.gsfc.nasa.gov/sci_team/pubs/abstract_new.php?id=38105 (use doi:10.1109/LGRS.2019.2962055) ; ⚠ https://c2c.wii.gov.in/lut-desert
- **Western Qaidam Basin:** https://hub.hku.hk/bitstream/10722/244904/1/content.pdf ; https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2022.875547/full ; https://hub.hku.hk/bitstream/10722/233282/1/Abstract.pdf
- **Bodélé Depression:** https://pmc.ncbi.nlm.nih.gov/articles/PMC2791565 ; https://science.nasa.gov/?p=1066952 ; https://en.wikipedia.org/wiki/Bod%C3%A9l%C3%A9_Depression
- **Harrat Khaybar:** https://www.livescience.com/archaeology/humans-were-living-in-a-lava-tube-7000-years-ago-on-the-arabian-peninsula ; https://earthdate.org/node/1161 ; https://www.earthobservatory.nasa.gov/images/152839/white-and-black-volcanoes-of-saudi-arabia ; https://volcanodb.com/190/Khaybar
- **Lonar Crater:** ⚠ https://nosamsresearch.whoi.edu/geology-lonar-crater-india ; https://www.usgs.gov/publications/hydrothermal-alteration-lonar-lake-impact-structure-india-implications-impact ; https://ricerca.unich.it/retrieve/e4233f15-09e0-2860-e053-6605fe0a460a/Lonar_age_2014_g-cubed_standard.pdf
- **Dallol:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6380227 ; https://phys.org/news/2019-05-ultra-small-microbes-extreme-survival-skills.pdf ; https://en.wikipedia.org/wiki/Dallol_(hydrothermal_system)
- **Río Tinto:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4206857 ; https://core.ac.uk/download/36024574.pdf ; https://www.campercontact.com/en/spain/andalusia/nerva/74619/undefined
- **East Antarctic Plateau:** https://repository.library.noaa.gov/view/noaa/26979/noaa_26979_DS1.pdf ; https://news.agu.org/press-release/coldest-place-on-earth-is-colder-than-scientists-thought/ ; https://en.wikipedia.org/wiki/Dome_A
- **Atacama (Yungay):** https://doi.org/10.3389/fspas.2021.810426 ; https://link.springer.com/10.1038/s41598-018-35051-w ; https://wondermondo.com/yungay
- **Haughton Crater:** https://openpolar.no/Record/ftciteseerx:oai:CiteSeerX.psu:10.1.1.471.7911 ; https://en.wikipedia.org/wiki/Haughton_impact_crater
- **Malapert Massif:** https://data.lroc.im-ldi.com/lroc/view_rdr/NAC_ROI_MALAPERTLOD ; https://www.astronomy.com/space-exploration/here-are-the-nine-sites-where-artemis-3-might-land-on-the-moon/ ; https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025JE009127 ; https://arxiv.org/pdf/2303.03911 ; ⚠ https://www.airspacemag.com/daily-planet/new-light-on-the-lunar-poles-156800678/ ; https://www.universetoday.com/articles/heres-where-artemis-iii-might-land-it-looks-inviting ; https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html
- **Arcadia Planitia:** https://www.esa.int/Science_Exploration/Space_Science/Mars_Express/Earth_tones_on_Mars ; https://swim.psi.edu/ ; https://www.jpl.nasa.gov/news/where-should-future-astronauts-land-on-mars-follow-the-water/ ; https://en.wikipedia.org/wiki/Arcadia_Planitia ; https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html ; https://arcnav.psi.edu/urn:nasa:pds:context:instrument:met.vl2
- **Earth's limits:** ⚠ https://m.esa.int/Our_Activities/Space_Science/Mars_Express/Facts_about_Mars ; https://meetingorganizer.copernicus.org/EPSC2013/EPSC2013-864.pdf ; https://solarsystem.nasa.gov/planets/mars/in-depth.amp ; https://weforum.org/agenda/2018/06/scientists-record-earths-lowest-temperature-ever-heres-how-cold-it-got ; https://www.exeter.ac.uk/research/groups/physics/astrophysics/outreach/learningresources/landerresources/intrasolarbodies/
- **Lunar shadowed craters (reference):** https://www.diviner.ucla.edu/single-post/2020/07/20/new-diviner-seasonal-polar-data-products

**Tools:** Python, pandas, numpy, folium (Leaflet), plotly, GitHub Pages.

## Use of AI

AI tools helped with research and coding; the team made the decisions and checked the work.

- **What AI did (Claude Code; Cursor also used):**
  - wrote the Python scripts and the website code, and the project notes;
  - wrote the scripts that download or read data (MODIS, AppEEARS, Copernicus DEM, TES);
  - checked links;
  - suggested methods, such as the 15 km slope box and the sun-angle formula check;
  - flagged problems, such as a dead source link and a temperature citation to clarify.
- **AI also helped with research:** finding candidate sites, facts and sources.
- **What the team decided:**
  - the targets, the 12 sites and everything in the research sheet;
  - which data to trust: MODIS 1 km daily readings with a quality filter, ground-surface values only, never estimating;
  - comparing each site only with its own body;
  - which conditions to score.
- **What the team checked:** the source links before numbers were used, and the code.
- **No AI-generated images are used.** Any that appear in the demo must carry a visible watermark.

## Demo: 7 slides (one line each)

1. **Problem:** before the Moon and Mars, crews rehearse on Earth, but which places really match?
2. **Targets:** Malapert Massif (an Artemis candidate landing region) and Arcadia Planitia (icy Mars plain).
3. **12 Earth sites on one map,** including 10 lesser-known ones, filterable by Moon / Mars analogs.
4. **How we score:** one condition at a time, 0 to 1, from NASA MODIS, LRO Diviner, NASA fact sheets and ESA Copernicus data.
5. **Findings:** Lonar matches Malapert's hottest ground; Qaidam and Río Tinto match Arcadia's Sun; no single best site.
6. **Where Earth falls short:** no Sun below 23.4°, no −233 °C cold, no low gravity, vacuum or Mars radiation.
7. **Use it:** live site + open data and code; AI disclosure; next steps (albedo, Mars temperatures, more sites).

## Rule check (before submitting)

- [ ] **Public links only:**
  - 5 source links are dead and 7 need a click-check in a browser (see [link-check.md](link-check.md)). Fix them in the Sheet and re-export.
  - The Wiley paper (Wueller et al. 2025) may be paywalled; add an open copy if one exists.
- [x] **Repository and website are public:** both open without logging in (checked Nov 15).
- [x] **No NASA logos:** no image files at all in the repo, and no logos on the site. **Still check the demo slides/video.**
- [x] **AI images watermarked:** none in the repo. **Still check the demo.**
- [x] **Every source cited:** the About page lists every Sheet source, plus the data used for scores (added Nov 15: Copernicus DEM, NASA 22-089, fact sheets, MODIS).
  - [ ] The dead links above still need replacing.
- [x] **AI disclosure:** README "Use of AI" and the website's About page. **Add one line to the demo** (slide 7).
- [ ] **Demo format:** 30-second video with English subtitles, OR at most 7 slides.
