# PROMPT 2 — StarSeekers Mars Trackers: web prototype (map, routes, tracker, design). Paste after Prompt 1

Read `CLAUDE.md`. Prompt 1 must be done: `web/data/` has meta.json, cost.bin, slope.bin, softness.bin, hillshade.png, difficulty.png, traverse.json, landmarks.json.
Build `web/index.html`, `web/app.js`, `web/style.css`. Vanilla JS, Leaflet from a CDN, no build step. Do the stages in order and stop at each CHECKPOINT with a <= 8 line report.

## Facts from Prompt 1 (real data, trust these)
- Window: 10 x 10 km, case B (fallback). SW corner lon 77.2955 / lat 18.3842, NE corner lon 77.4642 / lat 18.5529. Grid 1000 x 1000, 10 m cells. Local metres: x east, y north, SW corner = (0,0).
- `cost.bin` / `slope.bin` / `softness.bin`: uint8, row-major, **first row = SOUTH**, `index = row*1000 + col`, so `row = floor(y/10)`, `col = floor(x/10)`. cost 255 = blocked (1.02% of cells). Slope range 0.1-59.9 deg (max per 10 m block).
- `hillshade.png` is 2000x2000 and `difficulty.png` is 1000x1000, both with top row = NORTH; both cover the full window.
- `traverse.json`: Perseverance real path in local metres with sol numbers, 31.7 km inside the window. **The latest waypoint (sol 2022) is OUTSIDE the window**, ~3.7 km west of the west edge (see `meta.json > latest_waypoint`). Show it as an off-map indicator ("Perseverance now: 3.7 km west of this window"), never as a marker inside.
- Known issues (Prompt 1B handles them): a red band along the west edge may be a data artifact; landmarks were re-picked; difficulty palette was regenerated with 5 classes in `web/data/classes.json`. Use `classes.json` for colours and the legend.
- Model values live in `config/params.json` (mirror them in a JS `PARAMS` object; do not hard-code numbers twice).

## Stage A — Map
- Leaflet with `L.CRS.Simple`; coordinates are local metres from `meta.json` (note Leaflet Simple uses [y, x]; mind the row order: cost.bin rows run from the SOUTH up).
- Setup that works for a 10,000 m span: `L.map(..., {crs: L.CRS.Simple, minZoom: -4, maxZoom: 2})`, bounds `[[0,0],[10000,10000]]` as [y, x], `imageOverlay` for hillshade then difficulty with those bounds, `fitBounds`. Show live cursor coordinates (x, y in m and lon/lat via the corners in `meta.json`).
- Layers: hillshade image overlay (base), difficulty overlay with an opacity slider, Perseverance traverse polyline (sol on hover), landmarks as small markers, a scale bar in metres.
- App title (page <title> and header): "StarSeekers Mars Trackers". Show the label "Educational estimate - uncalibrated model" permanently.
**CHECKPOINT A:** page loads from `python -m http.server`, layers toggle, traverse aligns with terrain.

## Stage B — Route planner
- Load `cost.bin`, `slope.bin`, `softness.bin` (fetch as ArrayBuffer).
- Click 1 = start, click 2 = end (reset on third click). 8-neighbour A* with a binary min-heap; blocked cells (255) impassable; diagonal cost x sqrt(2); run in a Web Worker if one search takes > 200 ms.
- Three modes from `params` (put the constants in a JS `PARAMS` object mirroring `config/params.json`):
  safe: `d*(1+8*risk)` · fast: `d/speed` · power: `d*energy`, where risk = cost/254, speed and energy from slope and softness as in CLAUDE.md.
- Draw the 3 routes in 3 colours; show a comparison table: length (m), est. time (min at 0.04 m/s base speed, assumption), energy index, max slope, mean risk, % cells with softness > 0.6.
- If no route exists, say so plainly (start/end blocked or disconnected).
- **Unsafe-route flag (risk cap).** Add to `config/params.json` and mirror in `PARAMS`: `unsafe_mean_risk = 0.6`, `risk_high = 0.8`, `unsafe_high_risk_share = 0.15` (all assumptions, tell me they are adjustable). A route is **UNSAFE** if its mean risk > `unsafe_mean_risk` OR more than `unsafe_high_risk_share` of its cells have risk > `risk_high`, even if no single cell is blocked.
  - Add a "Status" column to the comparison table: OK / UNSAFE, with the reason in a tooltip (e.g. "mean risk 0.71 > 0.6").
  - Mark one route as **Recommended**: the lowest total cost among the routes that are NOT unsafe. If every route is unsafe, show them all, say "no safe route found between these points", and do not recommend any.
  - A faster route never beats a safe one: UNSAFE routes cannot be Recommended, however short or quick they are.
  - Add two cases to `web/test_astar.js`: a route over a high-risk band is flagged UNSAFE, and the Recommended route skips it when a safe alternative exists.
- Write a tiny Node test `web/test_astar.js` on a synthetic grid with a wall (route must go around it, and fail when fully walled).
**CHECKPOINT B:** 3 routes between two clicked points, table filled, test passes.

## Stage C — Tracker (simulation)
- A "Drive" button animates a rover marker along the selected route (speed slider x1..x50).
- Uncertainty circle (radius = sigma in metres, drawn to scale): starts at 2 m; per metre driven `sigma += g*d` with `g = 0.005*(1+4*softness+2*slope/25)`; when within 30 m of a landmark: `sigma = min(sigma, 3)` and flash the landmark.
- Hidden "true slip" simulation: pick one random patch of ~10 cells along the route where true slip is 2x the predicted. When the live slip estimate exceeds prediction by 50%: show an ALERT banner, pause, and offer "Re-plan": raise that patch's cost (mark as blocked), recompute from the current position, continue.
- Side panel (as in the design): distance driven (km), time remaining (h, estimate), energy index, slip alert (%), current slope/softness, alert log.
- Chart "position accuracy along the path": sigma (m) vs distance, with landmark passes marked; draw it with plain canvas or SVG (no chart library).
- Optional if time allows: "Replay Perseverance" button that animates the real traverse by sol with a slider (education mode).
**CHECKPOINT C:** circle visibly grows on soft/steep sections, shrinks at landmarks, alert + re-plan works once.

## Stage D — Apply the Canva design
- The design is the image in `design/` (a WhatsApp JPEG of the Canva concept). View it. What it shows: dark navy UI, rust/orange terrain palette, **bilingual Arabic + English labels (RTL for Arabic)**, a large map with a planned path whose colour band shows slip (little slip on solid ground, high slip on soft sand), a concentric uncertainty circle (low / moderate / high), a "Live tracking position" panel with 4 metrics (trip distance km, time remaining, energy consumption, slip alert %), a chart "position accuracy estimation along the path" with a known-crater marker, and a 5-class difficulty legend.
- Match this look and these panels. Use `classes.json` for the legend.
- **Do NOT copy the design's mistakes:** "TIME REAIMNING (WH)" must be "Time remaining (h)"; "BJET" is a typo; fix any garbled Arabic wording; the title in the image says "Mars Navigator" but the app is **StarSeekers Mars Trackers**.
- Energy metric: show it as a relative **Energy index** (unitless), not Wh, unless I say otherwise. If I ask for Wh, add `wh_per_m_base` to params.json, label it "Wh (assumed)".
- Time remaining uses the base speed assumption (0.04 m/s) and must say "estimate".
- Extract: colour palette, fonts (use the closest free Google Font), layout of panels, button styles, labels/text. Put them in CSS variables at the top of `style.css`.
- Rebuild the layout to match the design as closely as reasonable; list in 5 lines what you matched and what you could not.
**CHECKPOINT D:** side-by-side comment: design vs. result.

## Stage E — Finish
- Mobile-friendly basics (panel collapses under the map on narrow screens).
- Update `README.md` status checkboxes and run instructions.
- GitHub Pages only serves the repo root, `/docs`, or a GitHub Actions workflow (not an arbitrary `web/` folder). Pick the simplest option (e.g. an Actions workflow that publishes `web/`), create the files, and give me the exact click/command steps. Don't push without my say-so.
**FINAL:** list known limitations (use the "Honest limits" in README) and the 3 most valuable next improvements.
