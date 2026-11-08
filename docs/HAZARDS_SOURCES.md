# Hazards: claims vs official sources (checked 2026-11-08)

Status: VERIFIED = matches an official NASA/ESA page I fetched · PARTIAL = official page found but value differs or is derived · UNVERIFIED = no primary source reached.

| Claim (team file) | Verified value | Source | Status |
|---|---|---|---|
| One-way comms delay 4-24 min | **~3.0 - 22.3 min** (Earth-Mars distance 54.6 - 401.4 million km / c; derived). ESA blog quotes ~4-24 min (different endpoints). Use 3-22. | NASA Mars Fact Sheet https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html ; ESA https://blogs.esa.int/mex/?p=257 (via search snippet only) | PARTIAL (derived from NASA distances; "NASA says 3-22" is second-hand) |
| Night temp below -80 C | Jezero air temp ~ -83 C pre-dawn, ~ -23 C afternoon (MEDA); NASA fact-sheet global surface min 184 K (-89 C), mean 214 K (-59 C) | https://science.nasa.gov/?p=354920 (found via search, archived page) ; https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html | PARTIAL (MEDA figure seen only in search summary) |
| Gravity 0.38 g | 3.73 m/s2 mean = 0.380 g (3.73/9.81) | NASA Fact Sheet (same URL) | VERIFIED |
| Atmosphere CO2 ~95% | 95.1% by volume | NASA Fact Sheet | VERIFIED |
| Surface pressure | 6.36 mb mean (4.0 - 8.7 seasonal). Jezero-specific value not checked. | NASA Fact Sheet | VERIFIED (global) / Jezero UNVERIFIED |
| Dust storms cut energy | NASA: winds can create storms covering much of the planet; months for dust to settle (https://science.nasa.gov/mars/facts/). Solar rovers lose power (Opportunity, 2018). **Perseverance is powered by an MMRTG (~110 W at launch, declining a few %/yr), not solar** -> the "energy" hazard is weak for this rover; dust matters for visibility/thermal. | https://science.nasa.gov/mars/facts/ ; https://science.nasa.gov/mission/mars-2020-perseverance/rover-components/ ; Opportunity: https://www.space.com/40888-mars-dust-storm-2018-and-opportunity-rover-images.html (secondary) | VERIFIED (storms, MMRTG) / quantitative effect UNVERIFIED |
| Radiation | Curiosity RAD: avg GCR dose equivalent ~0.67 mSv/day on surface (Aug 2012 - Jun 2013); cruise ~1.9 mSv/day. Quoted from press summaries, not the Science paper. | https://www.swri.org/press-release/swri-scientists-publish-first-radiation-measurements-surface-mars ; https://www.sci.news/space/science-mars-radiation-measurements-surface-01629.html | PARTIAL (secondary) |

Notes: the NASA /mars/facts page itself gives no gravity/pressure/delay/radiation numbers; those come from the Fact Sheet. Radiation and dust are irrelevant to the terrain model (no effect on routing); keep them as education text only.
