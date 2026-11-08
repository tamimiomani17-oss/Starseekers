# Architecture (short)
Static site: Python makes data once -> files in `web/data/` -> vanilla JS + Leaflet reads them. No backend.

## Files
- `config/params.json` weights, thresholds, grid, route factors · `window.json` detail zone · `window_wide.json` wide zone
- `python/` numbered scripts (each runs alone, prints a short summary); `common.py` shared paths + GDAL env
- `data/raw`, `data/processed` local downloads/crops (git-ignored)
- `web/index.html` page · `style.css` · `app.js` map, layers, UI · `astar.js` router · `worker.js` runs A* off the main thread · `tracker.js` simulated tracker · `test_astar.js` Node test
- `web/data/` detail: meta, cost/slope/softness .bin, hillshade/difficulty .png, traverse, landmarks, classes · `web/data/wide/` same for the 50 km zone
- `docs/` SOURCES, VALIDATION, RESEARCH_50KM, HAZARDS_SOURCES, ARCHITECTURE · `prompts/` build prompts · `_archive/` moved old files + LOG.md

## Who reads what
- `app.js` reads meta*.json, difficulty/hillshade PNGs, traverse/landmarks/classes; sends cost/slope/softness bins to `worker.js`.
- `worker.js` imports `astar.js`; `tracker.js` reads slope/softness for sigma growth.
- Bins are uint8, row-major, FIRST ROW = SOUTH. PNGs top row = north.

## Script order
01 waypoints -> 02 window -> 03 crop DEM -> 04 terrain -> 05 export web -> 06 validate -> 07 west strip -> 08 landmarks -> 09 classes
Wide zone: 10 fetch wide DEM -> 11 terrain wide -> 12 export wide.

## Run / test
`python -m http.server 8000 --directory web` · `node web/test_astar.js`
