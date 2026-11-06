# PROMPT 2 — StarSeekers Mars Trackers: web prototype (map, routes, tracker, design). Paste after Prompt 1

Read `CLAUDE.md`. Prompt 1 must be done: `web/data/` has meta.json, cost.bin, slope.bin, softness.bin, hillshade.png, difficulty.png, traverse.json, landmarks.json.
Build `web/index.html`, `web/app.js`, `web/style.css`. Vanilla JS, Leaflet from a CDN, no build step. Do the stages in order and stop at each CHECKPOINT with a <= 8 line report.

## Stage A — Map
- Leaflet with `L.CRS.Simple`; coordinates are local metres from `meta.json` (note Leaflet Simple uses [y, x]; mind the row order: cost.bin rows run from the SOUTH up).
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
- Write a tiny Node test `web/test_astar.js` on a synthetic grid with a wall (route must go around it, and fail when fully walled).
**CHECKPOINT B:** 3 routes between two clicked points, table filled, test passes.

## Stage C — Tracker (simulation)
- A "Drive" button animates a rover marker along the selected route (speed slider x1..x50).
- Uncertainty circle (radius = sigma in metres, drawn to scale): starts at 2 m; per metre driven `sigma += g*d` with `g = 0.005*(1+4*softness+2*slope/25)`; when within 30 m of a landmark: `sigma = min(sigma, 3)` and flash the landmark.
- Hidden "true slip" simulation: pick one random patch of ~10 cells along the route where true slip is 2x the predicted. When the live slip estimate exceeds prediction by 50%: show an ALERT banner, pause, and offer "Re-plan": raise that patch's cost (mark as blocked), recompute from the current position, continue.
- Side panel: distance driven, sigma, current slope/softness, alert log.
**CHECKPOINT C:** circle visibly grows on soft/steep sections, shrinks at landmarks, alert + re-plan works once.

## Stage D — Apply the Canva design
- Look at every image/PDF page in `design/` (view them). If `design/` is empty, STOP and tell me to add the export; do not guess a design.
- Extract: colour palette, fonts (use the closest free Google Font), layout of panels, button styles, labels/text. Put them in CSS variables at the top of `style.css`.
- Rebuild the layout to match the design as closely as reasonable; list in 5 lines what you matched and what you could not.
**CHECKPOINT D:** side-by-side comment: design vs. result.

## Stage E — Finish
- Mobile-friendly basics (panel collapses under the map on narrow screens).
- Update `README.md` status checkboxes and run instructions.
- GitHub Pages only serves the repo root, `/docs`, or a GitHub Actions workflow (not an arbitrary `web/` folder). Pick the simplest option (e.g. an Actions workflow that publishes `web/`), create the files, and give me the exact click/command steps. Don't push without my say-so.
**FINAL:** list known limitations (use the "Honest limits" in README) and the 3 most valuable next improvements.
