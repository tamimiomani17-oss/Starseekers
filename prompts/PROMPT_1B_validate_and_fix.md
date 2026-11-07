# PROMPT 1B — Validate + fix (run BEFORE Prompt 2)

Read `CLAUDE.md`. Prompt 1 is done and pushed. Do NOT re-download large data: `data/processed/dem.tif` and `terrain.npz` already exist. Do not push. Stop at the checkpoint.

## 1. Validate the model against the real Perseverance path (`python/06_validate.py`)
- Densify `web/data/traverse.json` segments every 10 m, map points to grid cells (x east, y north, metres; cost.bin rows run from the SOUTH).
- Print: points inside window, risk along the path (mean, median, p90, max), % cells blocked, % with risk > 0.6, % with risk > 0.8, slope percentiles, mean softness.
- Rule: a real rover drove this path. If > 5% of it is "blocked" or mean risk > 0.5, say the model is too pessimistic and name which parameter to relax (`slope_block_deg`, weights). Do NOT change params.json yourself; propose.
- Save the table to `docs/VALIDATION.md`.

## 2. Check the western strip (suspected artifact)
- In the preview, a red band ~1 km wide runs along the whole west edge, and the real traverse touches it. Also check a straight-edged seam near x ≈ 4.1-4.3 km, y ≈ 0.5-2 km (bottom centre of the preview).
- From `dem.tif` compute mean slope and roughness per 100 m column band for x = 0..1500 m; look for step changes (> 3x the neighbour), constant-value stripes, nodata or DTM blend footprints; compare with the hillshade.
- Save a profile plot to `data/processed/west_strip.png`. Conclude: likely artifact / likely real / unclear, with the evidence. If artifact: propose a low-confidence buffer (drawn hatched, and treated as blocked or penalised) and ASK me before applying.

## 3. Re-pick the 5 landmarks
- Current landmarks sit mostly in the west strip (x = 305, 425, 535 m), which is bad. Re-pick 5 landmarks: crater-like closed depressions or rims (use DEM curvature / rim prominence), none within 600 m of any window edge, at least 1.5 km apart, spread across the window.
- Name them "Landmark A..E" and write `web/data/landmarks.json` in the same format (x, y, elev_m).
- Optional, only if simple: official names from the USGS Gazetteer for features inside the window. Skip if it needs more than one small download.

## 4. Palette + legend from my Canva design
- The design legend has 5 classes: solid rock (white) -> easy (yellow) -> moderate (light orange) -> difficult (orange) -> prohibited (dark red). Regenerate `web/data/difficulty.png` with this palette (blocked cells = dark red).
- Print the risk histogram first. Default class thresholds on risk: 0.15 / 0.30 / 0.50 / 0.70, blocked = prohibited. Propose better ones if the histogram says so, and keep in mind the route "unsafe" cap is 0.6.
- Export `web/data/classes.json`: for each class the Arabic name, English name, colour hex, risk range.
- Keep `web/data/` total <= 8 MB.

## 5. Notes + commit
- Add a "Status after Prompt 1/1B" block (<= 14 lines) to `CLAUDE.md`: window case B and bbox, latest waypoint outside the window (3.7 km west), file list, south-up row order, image sizes (hillshade 2000x2000, difficulty 1000x1000, top row = north), known issues, the Arabic-path/GDAL certificate workaround in `python/common.py`.
- `git add -A` and commit "Checkpoint 1B". No push.

## CHECKPOINT 1B (report in <= 10 lines)
Validation numbers, strip verdict, new landmarks (table), class thresholds chosen, files changed, anything you want me to decide.
