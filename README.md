# StarSeekers Mars Trackers

**ملخص بالعربي:** خريطة 2D لمنطقة 10×10 كم قرب فوهة Jezero بالمريخ: طبقة صعوبة الأرض (ميل + خشونة + نعومة تربة تقريبية)، تخطيط مسار بثلاث أولويات (أمان/سرعة/طاقة)، وتتبّع محاكى لروفر مع دائرة عدم يقين. كل النتائج **تقدير تعليمي غير معايَر**.

> **Educational estimate - uncalibrated model.** Research and education only; not for real rover operations.

Repo: https://github.com/tamimiomani17-oss/Starseekers
Live (after Pages is enabled): https://tamimiomani17-oss.github.io/Starseekers/

## What it is
A static web prototype (no backend) built on open NASA/USGS data:
1. **Terrain difficulty map** of a 10 km x 10 km window (10 m/pixel): slope, roughness, softness proxy; 5 classes.
2. **Route planner** (A* in Web Workers) comparing safe / fast / power routes, with an UNSAFE flag.
3. **Simulated tracker**: uncertainty circle grows on soft/steep ground, resets at landmarks; slip alert and re-plan.
4. Perseverance's published traverse (NASA waypoints) as a layer.

## Run locally
```
python -m http.server 8000 --directory web
# open http://localhost:8000
```
Data prep (optional, outputs are already in `web/data/`): scripts in `python/` (`01_...py` ...), params in `config/params.json`.

## Deploy (GitHub Pages)
`.github/workflows/pages.yml` publishes the `web/` folder on every push to `main`.
One-time: repo **Settings -> Pages -> Source: GitHub Actions**.

## Status
- [x] Data fetched, window chosen, cost map exported (see `docs/VALIDATION.md`)
- [x] Map + difficulty layer
- [x] Routes (3 modes) + comparison table
- [x] Tracker + slip alert + re-plan
- [x] Design applied (Canva concept, typos fixed)
- [ ] Deployed to GitHub Pages (needs push + Pages setting)

## Honest limits
- Soil softness comes from thermal inertia (coarse THEMIS): an indicator, not a measurement.
- No rock-abundance data in v0; roughness is a stand-in.
- Speed/energy/slip factors are assumptions, not rover data. Energy is a unitless index; time uses an assumed 0.04 m/s.
- Perseverance data = published waypoints, not live telemetry. Latest waypoint is outside this window.
- Landmarks are DEM rims/bumps, not named craters. Risk weights and the 25 deg block threshold are assumptions.

## AI-assisted disclosure
This project was built with AI assistance (Anthropic Claude via Claude Code): code, data-prep scripts, and documentation were drafted by the AI and directed and reviewed by the team. The UI design is a team Canva concept. Model parameters are assumptions and have not been independently validated.

## References / data sources
- NASA Mars 2020 MMGIS - Perseverance waypoints/traverse: https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json ; location page https://science.nasa.gov/mission/mars-2020-perseverance/location-map/
- USGS Astrogeology - HiRISE DTM mosaics (Mars 2020 / MSR TRN): https://astrogeology.usgs.gov/search/map/mars-sample-return-terrain-relative-navigation-hirise-dtm-mosaic ; landing-site products https://astrogeology.usgs.gov/search/map/mars-2020-jezero-crater-landing-site-products
- THEMIS thermal inertia of Jezero (Zenodo): https://zenodo.org/record/4931348
- USGS Gazetteer of Planetary Nomenclature: https://planetarynames.wr.usgs.gov
- Leaflet 1.9.4: https://leafletjs.com (BSD-2) · Cairo font: Google Fonts (OFL)
- Full list with verification status: `docs/SOURCES.md`
