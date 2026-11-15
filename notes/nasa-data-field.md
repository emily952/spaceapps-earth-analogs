# NASA Data field (submission form)

Text to paste into the submission's NASA Data field, plus partner and other data.
Keep in step with the About page (`docs/about.html`), which lists every link.

## NASA data we used

- **NASA POWER (Prediction Of Worldwide Energy Resources), Climatology API v2.10.1,
  accessed 2026-11-15.** Annual TS_MAX ("the maximum hourly earth skin temperature in
  the period of interest") at each of our 12 Earth sites. Source: MERRA-2 reanalysis,
  about 50 km grid, so values describe the grid cell, not the exact spot. Used for
  the max ground temperature score against Malapert Massif.
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
  air temperatures (proxy only, not scored).
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
