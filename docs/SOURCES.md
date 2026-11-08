# Sources and verification status (checked 6 Nov 2026)

VERIFIED = seen in a search/page during this check. UNVERIFIED = needs checking by Claude Code on your PC.

| Need | Source | URL | Status |
|---|---|---|---|
| Perseverance traverse (real) | NASA MMGIS GeoJSON: waypoints, traverse, heli | https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json (also `M20_traverse.json`, `m20_heli_waypoints.json`, `m20_heli_flight_path.json`) | VERIFIED (used in 2025 public scripts). CORS in browser: UNVERIFIED -> download with Python |
| Perseverance location page | NASA Science | https://science.nasa.gov/mission/mars-2020-perseverance/location-map/ | VERIFIED |
| Elevation 1 m (Jezero) | USGS HiRISE DTM mosaic JEZ_hirise_soc_006 (1 m, equirectangular) | https://astrogeology.usgs.gov/search/map/Mars/Mars2020/JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40 | VERIFIED product link (from a published paper). File size + direct link: UNVERIFIED (find on the page) |
| Elevation, newer westward extension | USGS MSR TRN HiRISE DTM + orthoimage mosaics (2025) | https://astrogeology.usgs.gov/search/map/mars-sample-return-terrain-relative-navigation-hirise-dtm-mosaic | VERIFIED. Zip is **5.3 GB** (GeoTIFFs inside) |
| Elevation, coarse fallback | USGS CTX DEM mosaic, 20 m/pixel, Jezero | https://astrogeology.usgs.gov/search/map/mars-2020-jezero-crater-landing-site-products | VERIFIED product list |
| Raw landing-site folder | USGS Astropedia | https://planetarymaps.usgs.gov/mosaic/mars2020_trn/HiRISE/ | VERIFIED (cited in a paper) |
| Soil softness proxy | THEMIS thermal inertia of Jezero, GeoTIFF, **1.7 MB**, null = 0, units J m-2 K-1 s-1/2 | https://zenodo.org/record/4931348 (file `Jezero_Thermal_Inertia_v1.tiff`) | VERIFIED |
| Thermal inertia, global alternative | USGS THEMIS TI mosaics 100 m (tiles ~2.5 GB each) | https://astrogeology.usgs.gov/search/map/themis_thermal_inertia_mosaic_quantitative_30s060e_100mpp | VERIFIED (accuracy ~20%) |
| Base tiles (context only) | Mars Trek WMTS, e.g. MOLA colour shade 463 m | `https://trek.nasa.gov/tiles/Mars/EQ/Mars_MGS_MOLA_ClrShade_merge_global_463m/1.0.0/default/default028mm/{Z}/{Y}/{X}.jpg` · catalog https://api.nasa.gov/mars-wmts/catalog | VERIFIED |
| Place names | USGS Gazetteer of Planetary Nomenclature | https://planetarynames.wr.usgs.gov | VERIFIED |
| Rock abundance for Jezero | not found | - | UNVERIFIED / missing -> use roughness proxy |
| "stiles" GitHub waypoints repo (mentioned in the voice call) | could not confirm it exists | - | UNVERIFIED -> use NASA JSON above |

## Things to check first (Prompt 1 does this)
1. Does the HiRISE DTM actually cover a 10 km window around Perseverance's latest waypoint? The rover has driven far from the original 2021 crater-floor coverage. If not covered, use the fallback in Prompt 1.
2. Real file sizes before downloading.
3. CRS of every GeoTIFF (read it, don't assume).

## Added for the 50 km zone (research 8 Nov 2026; details + measurements in `RESEARCH_50KM.md`)
| Need | Source | URL | Status |
|---|---|---|---|
| Wide DEM 20 m | USGS Mars 2020 Science CTX DEM (90 MB) | https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif | MEASURED: covers 93.1% of the 50 km box; west strip lon<77.0 missing. Accuracy numbers UNVERIFIED |
| Thermal inertia (wide) | Zenodo 4931348, 100 m | https://zenodo.org/record/4931348 | MEASURED: 95.1% extent, 73.6% non-zero; zeros = nodata |
| CTX imagery (optional) | Murray Lab CTX mosaic via Esri tiles (L11 ~10 m) | https://astro.arcgis.com/arcgis/rest/services/OnMars/CTX1/MapServer | tile fetch tested; bulk policy UNVERIFIED. Credit: NASA/JPL/MSSS/The Murray Lab; Dickson et al. 2024, doi:10.1029/2024EA003555; abs. offset < 200 m |
| Hazards numbers | `HAZARDS_SOURCES.md` | - | verified items only |
| Not used (too big/coarse) | MSR HiRISE DTM (676 MB member), Murray zip (1.81 GB), HRSC+MOLA 200 m | see research | not downloaded |
