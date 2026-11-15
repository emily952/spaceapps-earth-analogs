# Where to get data for each column

From the challenge's official Resources list. Any source is fine as long as
**every value has its source in the `source_links` column** of the Google Sheet.

## Column by column

| Column | Earth sites | Moon target | Mars target |
|---|---|---|---|
| `slope_deg` | Copernicus DEM (Copernicus Data Space) or SRTM (NASA Earthdata Search) | LRO **LOLA** slope maps (PDS) | MOLA or HiRISE terrain models (PDS) |
| `temp_max_c`, `temp_min_c`, `temp_range_c` | **In use:** NASA POWER skin temperature, TS_MAX (`data/fetch_power.py`). Also: MODIS **land surface** temperature (NASA Earthdata Search) | LRO **Diviner** polar products | PDS atmospheres archive (e.g. Mars Climate Sounder, TES) |
| `precip_mm_yr` | GPM IMERG (Earthdata Search) or GSMaP (JAXA G-Portal) | Team decision, see [team-decisions.md](team-decisions.md) | Team decision, see [team-decisions.md](team-decisions.md) |
| `dust_aod` | MODIS aerosol optical depth (Earthdata Search, preview in Worldview) or Sentinel-5P (Copernicus Data Space) | Team decision, see [team-decisions.md](team-decisions.md) | Rover or orbiter dust opacity (PDS) |

## Watch out for

- **Same kind of temperature everywhere.** Diviner measures the *ground surface*
  temperature. For Earth, use satellite land surface temperature (MODIS), not
  weather-station air temperature. Mixing the two makes the scores meaningless.
- **Mars dust vs Earth dust.** Mars dust "opacity" is often measured at different
  wavelengths than Earth AOD (usually 550 nm). Write down the wavelength, and
  mention the mismatch in the site's `breaks` text if we compare them.
- **Don't fill gaps.** If we can't find a value, leave the cell blank. It shows as
  "no data" on the site. Never estimate.

## Other sources on the list (not tied to a column)

- **NASA Worldview**: quick visual check of a site; good for screenshots in our notes.
- **RADARSAT (RCM, RADARSAT-1) and the SAR Python tutorial**: radar imagery. Useful
  for describing ice, permafrost or terrain in the `matches` / `breaks` text.
- **ESA Open Science Catalog**: browse for extra datasets.

## Links

- NASA Earthdata Search: https://search.earthdata.nasa.gov
- NASA Worldview: https://worldview.earthdata.nasa.gov
- NASA Planetary Data System (PDS): https://pds.nasa.gov
- Copernicus Data Space Ecosystem: https://dataspace.copernicus.eu
- JAXA G-Portal: https://gportal.jaxa.jp
- LRO, Diviner, CSA RADARSAT and ESA catalog: see the challenge's Resources page.

## Terms of use

The challenge says: *"participants must comply with any data use parameters of that
specific website."* Several providers (e.g. Copernicus, JAXA) ask to be credited.
Keeping every link in `source_links` gives us the credits list we need.
