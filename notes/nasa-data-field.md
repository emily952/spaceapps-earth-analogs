# NASA Data field (submission form)

Text to paste into the submission's NASA Data field, plus partner and other data.
Keep in step with the About page (`docs/about.html`), which lists every link.

## NASA data we used

- **NASA POWER TS_MAX (scored):** the maximum hourly ground (skin) temperature, 2001–2025,
  MERRA-2 ~50 km grid; used for the max temperature score vs Malapert (team decision (Nov 15): max = the highest hourly ground (skin) temperature reported by the dataset in its stated period).
  POWER citation: see the NASA POWER entry below.
- **MODIS Aqua daily land surface temperature, MYD11A1 v6.1 (1 km), 2025, via NASA AppEEARS
  (reference only, not scored).** For each site: the hottest good-quality daily reading. Quality filter:
  MODLAND 00/01 and LST error 2 K or less (days kept vs dropped are on the About page).
  Citations: Wan, Z., Hook, S., & Hulley, G. (2021). MODIS/Aqua Land Surface
  Temperature/Emissivity Daily L3 Global 1km SIN Grid V061. NASA LP DAAC.
  https://doi.org/10.5067/MODIS/MYD11A1.061. AppEEARS Team (2026), AppEEARS Ver. 3.137,
  NASA EOSDIS LP DAAC, https://appeears.earthdatacloud.nasa.gov. Request record: `data/appeears/`.
- **MODIS 8-day MYD11A2 via ORNL DAAC (doi:10.3334/ORNLDAAC/1600): reference only,
  not scored.** Our second temperature source, replaced by the daily data.
  Why MODIS: we switched from NASA POWER (~50 km grid cell) to MODIS (1 km pixel) because it is the smallest Earth temperature data on the challenge Resources list that covers all 12 sites without a login.
- **NASA POWER, Climatology API v2.10.1, accessed 2026-11-15 (TS_MAX is scored).** Annual TS_MAX at each site (MERRA-2, about 50 km grid). Our first source
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
  25.19°, Moon 6.68° − 5.145° = 1.54°) behind our scored "highest Sun angle".
- **NASA Earth Observatory:** Lut Desert, Harrat Khaybar and Bodélé write-ups.
- **MODIS land surface temperature** (via Azarderakhsh et al. 2020, NASA MODIS
  science team page): Lut's 80.8 °C record, shown in text only.
- **Viking lander meteorology (Planetary Data System):** Mars air temperature proxy.

- **NASA POWER AOD_55** (aerosol optical depth at 0.55 µm, CERES SYN1deg, 2001–2025
  climatology): Earth dust/haze, scored against Arcadia.
- **MOLA MEGDR** (Mars Global Surveyor laser altimeter, 128 pixels/degree, Smith et al.
  2003, PDS): Arcadia slope (0.36°), scored against Earth slopes at the same pixel size.

## Partner space agency data

- **ESA Mars Express:** dust devils at Arcadia Planitia.
- **Copernicus DEM GLO-30 (ESA / European Union), doi:10.5270/ESA-c5d3d65,** via AWS open
  data: average slope in a 15 × 15 km box at each Earth site, scored against Malapert's
  landing-area slope (5.6° ± 2.0°, Wueller et al. 2025). Box size = the size of a NASA
  Artemis candidate landing region (NASA release 22-089, Aug 2022).

## Notes

- No NASA logos, insignia or mission patches are used anywhere (challenge rule).
- POWER also asks users to tell them about published uses
  (larc-power-project@mail.nasa.gov). That's optional and up to the team.
