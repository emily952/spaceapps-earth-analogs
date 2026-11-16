# NASA Data field (submission form)

Text to paste into the submission's NASA Data field, plus partner and other data.
Keep in step with the About page (`docs/about.html`), which lists every link.

## NASA data we used

- **MODIS Aqua land surface temperature, MYD11A2 v6.1 (1 km, 8-day), year 2025,
  accessed 2026-11-15, via the ORNL DAAC MODIS/VIIRS Land Product Subsets web service.**
  For each of our 12 Earth sites: the hottest 8-day average of clear-sky daytime
  (~1:30 pm) readings in the one 1 km pixel at the site. Used for the max ground
  temperature score against Malapert Massif. Citation: "ORNL DAAC. 2018. MODIS and
  VIIRS Land Product Subsets RESTful Web Service. https://doi.org/10.3334/ORNLDAAC/1600 .
  Product MYD11A2 v6.1 (Wan, Hook, Hulley)." Example request per site: `data/modis_lst.csv`.
  Why MODIS: we switched from NASA POWER (~50 km grid cell) to MODIS (1 km pixel) because it is the smallest Earth temperature data on the challenge Resources list that covers all 12 sites without a login.
- **NASA POWER, Climatology API v2.10.1, accessed 2026-11-15 (reference only, not
  scored).** Annual TS_MAX at each site (MERRA-2, about 50 km grid). Our first source
  for max temperature, replaced by MODIS.
  Citation (POWER's requested wording): "The data was obtained from National
  Aeronautics and Space Administration (NASA) Langley Research Center's Prediction Of
  Worldwide Energy Resources (POWER) project funded through the NASA Earth Science
  Division." Exact request per site: `data/power_skin_temps.csv`.
  https://power.larc.nasa.gov
- **LRO Diviner (Lunar Reconnaissance Orbiter).** Max ground surface temperature
  (47 °C) at the Malapert ridge top, via arXiv 2303.03911
  (https://arxiv.org/abs/2303.03911). Diviner polar products also support our
  "Where Earth falls short" comparison (shadowed craters about 40 K).
- **NASA EOSDIS GIBS, Blue Marble shaded relief:** the map's background imagery.
  https://nasa-gibs.github.io/gibs-api-docs/
- **NASA planetary fact sheets (NSSDC):** Moon and Mars gravity, pressure, Viking 1
  air temperatures (proxy only, not scored), and the axial tilts (Earth 23.44°, Mars
  25.19°, Moon 6.68° − 5.145° = 1.535°) behind our scored "highest Sun angle".
- **NASA Earth Observatory:** Lut Desert, Harrat Khaybar and Bodélé write-ups.
- **MODIS land surface temperature** (via Azarderakhsh et al. 2020, NASA MODIS
  science team page): Lut's 80.8 °C record, shown in text only.
- **Viking lander meteorology (Planetary Data System):** Mars air temperature proxy.

## Partner space agency data

- **ESA Mars Express:** dust devils at Arcadia Planitia.

## Notes

- No NASA logos, insignia or mission patches are used anywhere (challenge rule).
- POWER also asks users to tell them about published uses
  (larc-power-project@mail.nasa.gov). That's optional and up to the team.
