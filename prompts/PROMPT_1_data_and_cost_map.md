# PROMPT 1 — StarSeekers Mars Trackers: data + terrain cost map (paste into Claude Code)

Read `CLAUDE.md` and `docs/SOURCES.md` first. Follow the working rules there (stop at checkpoints, short reports, ask before >500 MB downloads).
Goal of this prompt: produce the exported files the web app needs, for a **10 km x 10 km window**.

## Stage 0 — Setup
- Git: follow the "Git" section in `CLAUDE.md` (init + remote if needed). Do not push.
- Create `.gitignore` (data/raw, data/processed, .venv), a venv, `requirements.txt` (rasterio, numpy, scipy, pillow, requests, pyproj), install.
- Create `config/params.json` with the Model v0 values from `CLAUDE.md` (slope_block_deg=25, weights, speed/energy/uncertainty constants).

## Stage 1 — Perseverance traverse (`python/01_fetch_waypoints.py`)
- Download the NASA JSON files listed in `docs/SOURCES.md` (waypoints, traverse, heli waypoints, heli flight path) into `data/raw/`.
- Values may be strings (e.g. "0.0"); parse defensively. Inspect the properties and print: feature count, property names, the **latest waypoint** (sol, lon, lat).

## Stage 2 — Choose the window (`python/02_choose_window.py`)
1. Find the real file size of the HiRISE DTM (`JEZ_hirise_soc_006 ... 1m`) and, if needed, the newer MSR TRN HiRISE DTM zip (5.3 GB). Use the pages in SOURCES.md. Report sizes and **ask me before downloading anything > 500 MB**.
2. Read the DTM's CRS and bounds with rasterio. Convert the latest waypoint to the DTM CRS (Mars sphere R=3396190 m; read the CRS from the file).
3. Decision rule:
   - If a 10 x 10 km square centered on the latest waypoint lies fully inside valid DTM data -> use it.
   - Else -> fallback: pick the 10 x 10 km square fully inside valid data that contains the **most Perseverance traverse length** (so the real path is still visible). Say clearly which case happened.
   - If no HiRISE DTM can be obtained, fall back to the 20 m CTX DEM and say that resolution drops (then use a 20 m grid, 500 x 500).
4. Write `config/window.json` (center lon/lat, bbox in file CRS, source, resolution, which fallback).

## Stage 3 — Crop + terrain (`03_crop_dtm.py`, `04_terrain.py`)
- Crop the DTM to the window with rasterio windowed read -> `data/processed/dem.tif`. Handle nodata.
- Slope: resample to ~5 m, compute slope in degrees (Horn/central differences), aggregate to the 10 m routing grid using **max** per block.
- Roughness: std of elevation per 10 m block (from the 1 m data), normalize 0..1 (clip at 98th percentile).
- Soft ground proxy: download the THEMIS Jezero thermal inertia GeoTIFF from Zenodo (`https://zenodo.org/record/4931348`, ~1.7 MB), treat 0 as nodata, reproject/resample to the grid (bilinear), `softness = 1 - normalize(TI)` clipped 0..1. Where TI is nodata, set softness to the window median and record the fraction filled.
- Combine into `risk` and `blocked` using the Model v0 formula in `CLAUDE.md` and `params.json`.

## Stage 4 — Export for the web (`05_export_web.py`) into `web/data/`
- `meta.json`: grid width/height, cell size (m), local origin (SW corner = 0,0), window bbox, CRS string, lon/lat of corners, data source names, generated timestamp, and the label "Educational estimate - uncalibrated".
- `cost.bin`: uint8 per cell, row-major from the SOUTH row up (state this order in meta.json), 0..254 = risk scaled, 255 = blocked.
- `slope.bin`, `softness.bin`: uint8 (slope clipped to 0..45 deg scaled to 0..255; softness 0..255), same order.
- `hillshade.png` (grayscale, from the DEM, 1000 x 1000 or larger) and `difficulty.png` (green->yellow->red->dark red, blocked = black, semi-transparent where easy is fine).
- `traverse.json`: Perseverance traverse + waypoints clipped to the window, converted to local metres `[x, y]`, with sol numbers.
- `landmarks.json`: 5 landmark points chosen automatically (e.g. highest local roughness-and-elevation features spread across the window, at least 1.5 km apart) in local metres.
- A preview PNG `data/processed/preview.png` (hillshade + difficulty + traverse) for me to eyeball.

## CHECKPOINT 1 (stop here, report in <= 10 lines)
Report: which window case was used and why; DTM source + resolution; grid size; fraction of cells blocked; slope/risk ranges; fraction of softness filled with median; sizes of the files in `web/data/` (should total a few MB); any assumption you made.
Run these sanity checks and report pass/fail: (a) no NaN in cost.bin, (b) blocked fraction between 0% and 40% (else warn me), (c) traverse points fall inside the grid, (d) preview shows craters/steep rims as high risk.
Do not start the web app.
