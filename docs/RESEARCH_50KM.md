# Research: 50 x 50 km around the current window (2026-11-08)
Box centre lon 77.3798 / lat 18.4686 -> lon 76.935..77.824, lat 18.047..18.890. Numbers marked (m) were measured by me; UNVERIFIED = not checked. Data: `RESEARCH_50KM.json`. Hazards: `HAZARDS_SOURCES.md`. Educational estimate - uncalibrated.

## A) DEM for 50 km
| Source | Res | Extent / coverage of box | Size | Range-read | Verdict |
|---|---|---|---|---|---|
| **USGS Mars 2020 Science CTX DEM** `planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif` | 20 m | lon 77.00-78.58, lat 17.58-19.29; **93.1% of box valid** (m); file 99.9% valid | 90 MB | yes, but no overviews (full download is cheap) | **Best.** CRS = equirect with lat_ts 18.4663 (true scale at site) (m). Gap = west strip lon <77.0 |
| USGS TRN CTX DTM (LVS) | 20 m | only 36.6% of box (extent) (m) | 9.3 MB | yes | too small |
| USGS MSR TRN HiRISE DTM | 1 m | bbox lon 77.058-77.381, lat 18.136-18.588 -> ~19.5% of box (from XML bbox) | member 676 MB (zip 5.47 GB) | **no**: only inside zip, deflate | > 500 MB, partial; needs Omar's OK; adds only the west/south-west |
| HRSC+MOLA blend v2 (global) | 200 m | 100% (m), elev -2741..-1413 m | 11.4 GB global | yes (striped int16; 250x264 px window took 52 s) | fallback, too coarse for slope/hazards |
| MOLA 463 m | 463 m | 100% (m) | 2.1 GB global | yes | too coarse |
Pages: https://astrogeology.usgs.gov/search/map/mars_2020_science_investigation_ctx_dem_mosaic , https://astrogeology.usgs.gov/search/map/mars-sample-return-terrain-relative-navigation-hirise-dtm-mosaic
Caveat: CTX DEM vertical/horizontal accuracy: the page says new parts were localized to MOLA and partly georeferenced by hand in ArcGIS (UNVERIFIED numbers). 20 m posts: slope baseline >= 40 m, so slopes are smoother than the 10 m HiRISE product (slopes at the two resolutions are not comparable).

## B) Thermal inertia (Zenodo 4931348)
File 1.7 MB, 100 m, 890x890, 89x89 km. Extent covers **95.1%** of the box (west 2.4 km missing); non-zero (assumed valid; nodata=0) **73.6%** (m). Range 42-1655. Gaps -> fill with nearest/median and flag. Alternatives (THEMIS global TI ~ 100-300 m, USGS "mars-themis-derived-global-thermal-inertia-mosaic") not measured: UNVERIFIED size.

## C) Murray CTX mosaic (5 m)
- Tile `E076_N16`: https://murray-lab.caltech.edu/CTX/V01/tiles/MurrayLab_GlobalCTXMosaic_V01_E076_N16.zip , **1,813,053,122 B (1.81 GB)**, Accept-Ranges yes (HEAD, m). Contains Mosaic.tif 2.25 GB **deflate-compressed** (central directory read by range) -> cannot range-read the tif; a crop needs the whole zip. NOT downloaded.
- Listing page is plain index (no tile-server in it). The 3D viewer (`MurrayLabCTXmosaic.html`) streams from **Esri tile service** `https://astro.arcgis.com/arcgis/rest/services/OnMars/CTX1/MapServer` (m): 512 px JPEG tiles, `/tile/{L}/{row}/{col}`; geographic degrees, origin (-180,90). L12 = 5.09 m/px, L11 = 10.2 m/px. I fetched tiles 12/1627/5856 (55 KB) and 11/813/2928 (59 KB) OK (m).
- **Smallest way for 50 km**: L12 = **420 tiles, ~23 MB** (est. 55 KB each); L11 = 110 tiles, ~6 MB. Lossy JPEG, display backdrop only (not for slope). Service text calls it an "uncontrolled" mosaic / beta01 (older than V01); service says exportTilesAllowed=false -> bulk-fetch policy UNVERIFIED, ask Esri/Murray or throttle politely.
- License: free for all purposes; credit "NASA/JPL/MSSS/The Murray Lab" + Dickson et al. 2024, doi:10.1029/2024EA003555 (site text, m). Absolute error "< 200 m" (site text). CTX vs DEM registration is NOT guaranteed: 200 m offset vs the 20 m DEM is possible -> overlay may shift visibly.

## D) Traverse
`M20_traverse.json`: 559 segments, 47.4 km (measured in file-CRS metres); **all of it inside** the 50 km box (m). Latest waypoint (sol 2022, lon 77.2332 lat 18.4356) **inside** the box, ~3.7 km west of the 10 km window.

## E) Equirectangular error (CONFIRMED)
`04_terrain.py` calls `horn_slope_deg(z5, 5.0)` -> same cell for x and y; the file is lat_ts=0 so file x-metres are 1/cos(18.4686 deg) = **1.0543x** ground. Measured on the real window DEM (m):
- Window ground width = 10000 x 0.9485 = **9.49 km** (height 10 km exact).
- E-W distances/route lengths overstated 5.4%; N-S exact; typical route ~+2-3% (estimate).
- Slope: x-gradient understated 5.4%. Corrected vs as-built: mean 7.11 -> 7.34 deg, p95 18.6 -> 19.2, max delta +1.5 deg; blocked (>=25 deg) cells **1.02% -> 1.21%**; tan ratio +3.2%. Small but systematic (risk slightly low). Fix: pass `dx = cell*cos(lat)` in the x term, scale x by cos(lat) in local coords (or reproject with lat_ts = 18.47; the CTX DEM already does). Not applied (scope).

## F) Hazards: see `HAZARDS_SOURCES.md` (delay is 3-22 min not 4-24; gravity, CO2 verified; Perseverance is MMRTG, not solar).

## G) Size / performance budget (web/ <= 25 MB proposed)
| Option | cells | bins (3 x uint8) | est. web/ total | A* corner-to-corner (Node, m) |
|---|---|---|---|---|
| detail 10 km @10 m (now) | 1.0 M | 3.0 MB | 5.8 MB (m) | 1.3 s |
| wide 50 km @40 m | 1.56 M | 4.7 MB | ~11 MB with detail + images (est.) | 2.0 s |
| wide 50 km @20 m | 6.25 M | 18.8 MB | ~31 MB (est.; > 25 MB unless gzip: current bins gzip to 0.4-0.9x) | **10.8 s** |
Benchmark = my 8-neighbour binary-heap A*, worst case; browser/mobile maybe 2-4x slower (assumption). 20 m wide needs hierarchical routing or a web worker -> not recommended for v1.

## H) Recommendation
| Option | Res | Size | Risk | Recommended? |
|---|---|---|---|---|
| Keep 10 km only | 10 m | 5.8 MB | none | baseline |
| detail 10 m + **wide 40 m from CTX DEM 20 m** | 40 m | ~11 MB | 7% of box has no data (west strip); coarse slope; DEM offset vs HiRISE | **YES** |
| wide at 20 m | 20 m | ~31 MB | slow A*, size | no (later, with worker) |
| MSR HiRISE DTM for west | 1 m | 676 MB DL | > 500 MB, covers only 19% | only if Omar approves |
| CTX imagery backdrop via Esri tiles L11 | 10 m | ~6 MB | JPEG, bulk policy, 200 m offset | optional |
| CTX imagery from Murray zip (L12 quality) | 5 m | 1.8 GB DL | huge | no |

### Questions for Omar
1. Approve building wide @40 m from the 90 MB CTX DEM (download < 500 MB, OK)?
2. Fix the cos(lat) error in the 10 km window now (changes risk/blocked slightly, ~+0.2% blocked)?
3. Approve downloading the 1.81 GB Murray zip (> 500 MB)? Or use Esri tiles L11/L12 (6 / 23 MB)?
4. Approve the 676 MB MSR HiRISE DTM member (needs a 5.4 GB-zip range read of 676 MB)?
5. West 2.4 km strip of thermal inertia and DEM missing: accept a "no data" band?
