# StarSeekers Mars Trackers — project rules (read first, keep short)

## Goal
Static 2D web prototype: terrain-difficulty map of a **10 km x 10 km window** on Mars (Jezero area),
click-to-route with 3 route modes (safe / fast / power), and a simulated rover tracker with a growing
uncertainty circle. For research + education. Everything is an **educational estimate, uncalibrated**.

## Scope
IN: Python data prep -> static files -> vanilla JS + Leaflet page. Runs by opening a local server, deploys to GitHub Pages.
OUT (do not build): 3D, live telemetry, backend/server, database, multi-site, user accounts.

## Structure
- `data/raw/` downloads (git-ignored) · `data/processed/` crops, grids (git-ignored except small meta)
- `python/` numbered scripts `01_...py`, `02_...py` (each runnable alone, prints a short summary)
- `config/params.json` weights/thresholds · `config/window.json` chosen window
- `web/` index.html, app.js, style.css, `web/data/` exported files (small)
- `design/` Canva export (PNG/PDF) dropped by the user · `docs/` SOURCES.md, SKILLS.md, MODEL_AND_TOKENS.md
- `prompts/` the two build prompts

## Key decisions (change only if I ask)
- Window = 10 km x 10 km. Routing grid = 10 m/pixel (1000 x 1000). Slope computed at ~5 m baseline, aggregated to 10 m with max.
- Mars sphere R = 3396190 m. Read the CRS from the GeoTIFF; never assume it. Local metric coords (x east, y north, metres from window SW corner) are used in the web app with Leaflet `L.CRS.Simple`.
- Model v0 per cell: `risk = clamp(0.5*slope/25 + 0.25*rough_norm + 0.25*softness, 0, 1)`; blocked if slope >= 25 deg (assumption, in params.json).
  `softness = 1 - norm(thermal_inertia)` (a PROXY, not a measurement). `rough_norm` = elevation std in a 10 m block (stand-in for rock density; no rock-abundance data yet).
- Route modes: safe = d*(1+8*risk) · fast = d/speed · power = d*energy. speed = max(0.15, 1-0.6*softness-0.4*slope/25); energy = 1+1.5*softness+2*slope/25. All in params.json.
- Tracker: uncertainty sigma grows per metre `g = 0.005*(1+4*softness+2*slope/25)`; landmark pass resets sigma to min(sigma, 3 m).
- Always show the label: "Educational estimate - uncalibrated model".

## Git
- Remote: https://github.com/tamimiomani17-oss/Starseekers (branch `main`). Local folder: this project root.
- If this folder is not yet a git repo: `git init`, `git branch -M main`, `git remote add origin <url>`; if the remote already has commits, `git pull origin main --allow-unrelated-histories` first and tell me about any conflict.
- Commit after every CHECKPOINT with a short message. **Never push without my explicit OK.** Never commit `data/raw` or large files (see `.gitignore`).

## Working rules (save tokens)
- Work stage by stage; stop at each CHECKPOINT and report in <= 10 lines. Do not continue past a checkpoint unless the prompt says so.
- Never print large arrays or full JSON; print shapes, ranges, counts.
- Ask before any download > 500 MB (check size with a HEAD request first).
- Prefer small edits over rewrites. No new dependencies without saying why.
- If a data source is unreachable or not covering the window, say so plainly and use the documented fallback; never invent data.
- Keep web code vanilla (no build step), < ~800 lines total, readable.

## Status after Prompt 1/1B
- Window: case B (fallback), SW lon 77.2955/lat 18.3842, NE lon 77.4642/lat 18.5529; Perseverance latest waypoint (sol 2022) is ~3.7 km WEST of the window (off-map indicator only).
- Files in `web/data/`: meta.json, cost.bin, slope.bin, softness.bin (uint8, 1000x1000, **first row = SOUTH**), hillshade.png (2000x2000), difficulty.png (1000x1000 RGBA), both **top row = north**; traverse.json, landmarks.json, classes.json. Total ~5.8 MB.
- Validation (docs/VALIDATION.md): along the real path mean risk 0.29, 0% blocked, 3.2% cells risk>0.6 -> model not too pessimistic.
- West strip: slope/roughness vary smoothly (no step >1.1x, no nodata, no stripes) -> likely REAL steep terrain, not an artifact. No buffer applied.
- Landmarks A-E re-picked (rims/bumps by DEM relief, >=800 m from edges, >=1.8 km apart).
- Classes: 5 (solid rock/easy/moderate/difficult/prohibited), risk thresholds 0.25/0.35/0.50/0.65; blocked = prohibited. Route UNSAFE cap uses mean risk 0.6.
- Known issues: softness is a THEMIS proxy (coarse); "roughness" is a rock-density stand-in; landmarks are rims, not named craters.
- Windows/Arabic path: `python/common.py::rio_env()` copies the certifi CA bundle to the temp dir for GDAL/curl. Run python via `.venv/Scripts/python.exe` from `python/` (set PYTHONIOENCODING=utf-8).
