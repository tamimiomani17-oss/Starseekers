# StarSeekers Mars Trackers

**ملخص بالعربي:** خريطة 2D لمنطقة 10×10 كم في فوهة Jezero بالمريخ، فيها طبقة صعوبة الأرض (ميل + خشونة + نعومة تربة تقريبية)، تخطيط مسار بثلاث أولويات (أمان/سرعة/طاقة)، وتتبّع محاكى لروفر مع دائرة عدم يقين. كل النتائج "تقدير تعليمي غير معايَر".

Repo: https://github.com/tamimiomani17-oss/Starseekers

## What it is
A static web prototype (no server) built on open NASA/USGS data:
1. **Terrain cost map** from a HiRISE DTM (slope, roughness) + THEMIS thermal inertia (soft-ground proxy).
2. **Route planner** (A*) comparing safe / fast / power routes.
3. **Simulated tracker** with an uncertainty circle that grows on soft/steep ground and shrinks at landmarks.
4. Perseverance's real traverse (NASA waypoints) shown as a layer.

## How to build it (2 steps, with Claude Code)
1. Open this folder in Claude Code (`claude` in the terminal). Use the model recommended in `docs/MODEL_AND_TOKENS.md`.
2. Paste `prompts/PROMPT_1_data_and_cost_map.md` -> wait for CHECKPOINT -> `/clear`.
3. Put your Canva export (PNG/PDF pages) in `design/`.
4. Paste `prompts/PROMPT_2_web_prototype.md` -> wait for CHECKPOINT.

## Run
```
python -m http.server 8000 --directory web
# open http://localhost:8000
```

## Status
- [ ] Prompt 1: data fetched, window chosen, cost map exported
- [ ] Prompt 2: map + difficulty layer
- [ ] Prompt 2: routes (3 modes) + comparison table
- [ ] Prompt 2: tracker + alert
- [ ] Prompt 2: design applied, deployed to GitHub Pages

## Honest limits
- Soil softness comes from thermal inertia: an indicator, not a measurement.
- No rock-abundance data in v0; roughness is a stand-in.
- Speed/energy/slip factors are assumptions, not rover data.
- Perseverance data = published waypoints, not live telemetry.

See `docs/SOURCES.md` for every data source and its verification status.
