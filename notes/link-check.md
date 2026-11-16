# Link check (Nov 15)

Every external link on the website (70) was opened by a script, and failures were
re-opened in a real browser engine. **Fix these in the Google Sheet**, re-export the
tab, rebuild. Our rule: every link must open without logging in.

## 1. Dead: replace (these do not open for anyone)

| Tab / row | Dead link | Suggested replacement (checked, opens) |
|---|---|---|
| Site options: Lut Desert; Earth's limits: Hottest surface | modarch.gsfc.nasa.gov/...?id=38105 (Azarderakhsh et al. 2020; the **80.8 °C** record) | The paper's DOI: https://doi.org/10.1109/LGRS.2019.2962055 (Azarderakhsh, Prakash, Zhao, AghaKouchak 2020, *IEEE GRSL* 17(12): 2025–2029). NASA Earth Observatory's Lut page (already cited) also gives 80.8 °C. |
| Site options: Lut Desert | c2c.wii.gov.in/lut-desert ("UNESCO summary": times out) | UNESCO World Heritage page for Lut Desert: https://whc.unesco.org/en/list/1505 (please check it opens) |
| Site options: Lonar Crater | nosamsresearch.whoi.edu/geology-lonar-crater-india (page removed: 404) | Remove; Lonar has other sources. Or the Earth Impact Database: http://www.passc.net/EarthImpactDatabase/index.html |
| Earth's limits (Mars row) | m.esa.int/Our_Activities/.../Facts_about_Mars (old ESA address, no longer exists) | https://www.esa.int/Science_Exploration/Space_Science/Mars_Express/Facts_about_Mars |
| Targets: Malapert; Earth's limits: lunar polar rows | airspacemag.com/daily-planet/new-light-on-the-lunar-poles-156800678/ (Air & Space magazine closed; redirects to an error) | Find the same article on smithsonianmag.com, or cite Diviner directly: https://www.diviner.ucla.edu/single-post/2020/07/20/new-diviner-seasonal-polar-data-products (already used elsewhere) |

## 2. Block scripts, probably fine for people: **click each once in a browser**

These show a "Just a moment..." bot check to scripts. Judges using a browser should get
through, but please confirm each opens:
- agupubs.onlinelibrary.wiley.com/doi/10.1029/2025JE009127 (Wueller et al. 2025, Malapert slope)
- core.ac.uk/download/36024574.pdf
- hub.hku.hk/bitstream/10722/233282/1/Abstract.pdf and .../244904/1/content.pdf (Qaidam)
- ricerca.unich.it/...Lonar_age_2014_g-cubed_standard.pdf
- phys.org/news/2019-05-ultra-small-microbes-extreme-survival-skills.pdf (Dallol)
- repository.library.noaa.gov/view/noaa/26979/noaa_26979_DS1.pdf

## 3. Weak sources: stronger replacements to consider

Public but not primary. Swap or add a primary source next to them:

| Row | Weak source | Primary source (checked) |
|---|---|---|
| Dallol | phys.org PDF; Wikipedia | Gómez et al. 2019, *Scientific Reports*: https://www.nature.com/articles/s41598-019-44440-8 (open access) |
| East Antarctic Plateau | Wikipedia (Dome A); weforum.org | Scambos et al. 2018, *GRL*: https://doi.org/10.1029/2018GL078133, plus AGU's press release (opens without a bot check): https://news.agu.org/press-release/coldest-place-on-earth-is-colder-than-scientists-thought/ |
| Malapert | astronomy.com; universetoday.com | NASA's own release: https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/ |
| Harrat Khaybar | volcanodb.com | Smithsonian Global Volcanism Program, volcano 231060: https://volcano.si.edu/volcano.cfm?vn=231060 (was "temporarily unavailable" during our check: retry) |
| Haughton | Wikipedia | Earth Impact Database (Univ. of New Brunswick): http://www.passc.net/EarthImpactDatabase/index.html |
| Atacama (Yungay) | wondermondo.com (coordinates) | Navarro-González et al. 2003, *Science* ("Mars-like soils in the Atacama Desert"): https://doi.org/10.1126/science.1089143. **Check our coordinates (−24.066, −69.864) against it.** |
| Río Tinto | campercontact.com (coordinates) | No primary source found yet. Look for a Peña de Hierro / IPBSL drilling paper that gives the site's coordinates |
| Bodélé, Arcadia | Wikipedia | Both rows already have NASA/ESA sources, so the Wikipedia links can simply be removed |

The 2025 Wiley paper (Malapert slope) is behind a bot check and may be paywalled:
also add its NASA ADS record or an open copy if one exists.
