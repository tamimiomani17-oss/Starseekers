# StarSeekers Mars Trackers — ابدأ من هنا

ملف واحد فيه كل شي: الموديل، الخطوات، الأوامر، والبرومبتين. اتبعه من فوق لتحت.

**المستودع:** https://github.com/tamimiomani17-oss/Starseekers
**المجلد على جهازك:** `C:\Users\intel11\Desktop\Life\هاكاثون ناسا\26\starseekers-mars-trackers`

## 1) الصورة الكاملة

| | |
|---|---|
| **شنو نبني** | خريطة 2D لمنطقة **10×10 كم** في Jezero: طبقة صعوبة الأرض + 3 مسارات (أمان / سرعة / طاقة) + تتبّع محاكى لروفر بدائرة عدم يقين |
| **الأدوات** | Python (تجهيز البيانات) + JavaScript/Leaflet (الصفحة). بدون سيرفر |
| **عدد الخطوات** | برومبتين فقط، كل واحد ينتهي بـ CHECKPOINT |
| **ملاحظة صريحة** | كل النتائج "تقدير تعليمي غير معايَر". معاملات السرعة والطاقة والانزلاق افتراضات، وليست بيانات روفر |

```
البرومبت 1 (بيانات + خريطة الصعوبة)  ->  /clear  ->  تصدير Canva  ->  البرومبت 2 (الصفحة + المسارات + التتبّع + التصميم)
```

## 2) أي موديل تستخدم

| المهمة | الموديل | الأمر |
|---|---|---|
| **البناء كله** (البرومبت 1 و2) | **Sonnet 5.5** | `/model sonnet` |
| تعديلات بسيطة: نصوص، ألوان، إعادة تسمية | Haiku 5.5 | `/model haiku` |
| علقت على bug صعب (إسقاط/CRS أو بطء A*) | Opus 5.5، للمشكلة هذي فقط ثم ارجع Sonnet | `/model opus` |
| ما تحتاجه | Fable / Mythos | زيادة بلا فايدة هنا |

**عشان توفر توكنز:** `CLAUDE.md` يحمل السياق فاكتب `/clear` بين البرومبتين، ولا تخلي Claude يكمل بعد CHECKPOINT، ولا تلصق بيانات كبيرة بالشات (السكربتات تطبع ملخصات فقط).

## 3) قبل ما تبدأ (5 دقائق)

افتح PowerShell وجرّب:

```
python --version
git --version
claude --version
```

| لو ما اشتغل | الحل |
|---|---|
| `python` | ثبّت Python 3.10 أو أحدث من python.org وفعّل "Add to PATH" |
| `git` | ثبّت Git for Windows |
| `claude` | ثبّت Claude Code حسب https://docs.claude.com/en/docs/claude-code |

**مساحة القرص:** إذا احتاج Claude Code ملف USGS الأحدث (zip بحجم **5.3 GB**) فاحجز 10 GB فاضية على الأقل. هو بيسألك قبل أي تنزيل فوق 500 MB.

## 4) الخطوات

### الخطوة 1 — افتح المشروع في Claude Code

```
cd "C:\Users\intel11\Desktop\Life\هاكاثون ناسا\26\starseekers-mars-trackers"
claude
```

ثم اكتب:

```
/model sonnet
```

Claude Code يقرأ `CLAUDE.md` تلقائياً. فيه القواعد (نافذة 10 كم، شبكة 10 م، التوقف عند كل CHECKPOINT، ما يسوي push بدون إذنك).

### الخطوة 2 — الصق البرومبت 1 (البيانات + خريطة الصعوبة)

الصقه كاملاً (من السطر الأول إلى آخر سطر داخل المربع):

````markdown
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
````


**لما يوصل CHECKPOINT 1:** لازم يعطيك تقرير قصير: أي نافذة اختار وليش، دقة الارتفاعات، نسبة الخلايا الممنوعة، وفحوصات النجاح/الفشل.

| تتأكد من | الطبيعي |
|---|---|
| الملف `data/processed/preview.png` | الفوهات والحواف شديدة الميل ملوّنة بالأحمر، والمسار الحقيقي ظاهر |
| نسبة الخلايا الممنوعة | بين 0% و40% (غيرها يحذّرك) |
| حجم `web/data/` | بضعة ميجابايت فقط |

لو النافذة ما تغطي موقع الروفر الأخير: هذا متوقع، وحينها يختار أفضل مربع 10×10 كم يغطي أكبر جزء من مساره الحقيقي ويقول لك.

ثم احفظ التقدم:

```
git add -A
git commit -m "Checkpoint 1: data and cost map"
```

### الخطوة 3 — نظّف السياق

```
/clear
```

### الخطوة 4 — حط تصميم Canva

صدّر الصفحات من Canva: **Share > Download > PNG** (كل الصفحات) وسمّها مثل `01_main.png` و`02_routes.png`، وحطها في:

```
starseekers-mars-trackers\design\
```

أنا ما قدرت أفتح رابط Canva (رفض الوصول)، فالتصدير هو الطريق. لو المجلد فاضي، البرومبت 2 يوقف عند المرحلة D ويقول لك، ولا يخترع تصميم.

### الخطوة 5 — الصق البرومبت 2 (الصفحة + المسارات + التتبّع + التصميم)

ما زال الموديل Sonnet. الصقه كاملاً:

````markdown
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
````


**يوقف عند 4 نقاط (A و B و C و D) ثم يكمل E.** عند كل نقطة افتح الصفحة وتأكد بعينك:

| CHECKPOINT | شنو تشوف |
|---|---|
| A | الخريطة تفتح، الطبقات تشتغل، مسار Perseverance منطبق على التضاريس |
| B | تنقر نقطتين فيطلع 3 مسارات وجدول مقارنة (الطول، الوقت، الطاقة، الميل، المخاطرة) |
| C | الدائرة تكبر على الرمل والميل، وتصغر عند المعالم، والتنبيه يوقف الروفر ويعيد التخطيط |
| D | الشكل يطابق تصميم Canva قدر الإمكان |

## 5) تشغيل الصفحة

```
python -m http.server 8000 --directory web
```

افتح: http://localhost:8000

## 6) حفظ ونشر على GitHub

بعد كل CHECKPOINT:

```
git add -A
git commit -m "وصف قصير"
```

لما تكون جاهز (وبعد ما تراجع):

```
git push -u origin main
```

**ملاحظة:** GitHub Pages ما ينشر أي مجلد، فقط الجذر أو `docs` أو workflow جاهز. البرومبت 2 يرتّبها لك ويعطيك خطوات النقر بالضبط.

## 7) لو صار خلل

| المشكلة | الحل |
|---|---|
| الخريطة فاضية أو مقلوبة | غالباً ترتيب الصفوف (cost.bin يبدأ من **الجنوب**) أو إحداثيات `[y, x]` في Leaflet. اكتب له: "الخريطة مقلوبة، افحص ترتيب الصفوف والإسقاط" |
| لا يلقى بيانات الروفر | رابط NASA JSON ممكن يتغير. قل له يوريك الخطأ ويبحث عن الرابط الحالي |
| مسار التنزيل بطيء أو فشل | لا تعيد من الصفر، قل له يكمل من الملف الجزئي أو يستخدم DEM الـ20 م كبديل |
| يسألك صلاحيات | وافق على قراءة وتشغيل Python داخل المجلد فقط |
| التكلفة عالية | `/clear`، وارجع Sonnet، ورسالة وحدة لكل مشكلة مع الخطأ بالنص فقط |
| `git push` رفض | المستودع فيه commits قديمة. قل له: "اعمل pull مع دمج التاريخ وأخبرني بأي تعارض" |

## 8) الحدود الصريحة

- نعومة التربة من thermal inertia: **مؤشر تقريبي**، وليست قياساً مباشراً.
- ما لقيت بيانات rock abundance لـ Jezero، فالخشونة بديل مؤقت.
- معاملات السرعة والطاقة والانزلاق افتراضات: راجعها بخبرتك الميكانيكية في `config/params.json`.
- بيانات Perseverance هي **نقاط منشورة**، مو تتبّع حي.
- ما قدرت أتأكد من مستودع GitHub اللي ذكرناه بالمكالمة، فنستخدم روابط NASA المباشرة (التفاصيل في `docs/SOURCES.md`).

## 9) أين باقي الملفات

| الملف | وظيفته |
|---|---|
| `CLAUDE.md` | القواعد التي يقرأها Claude Code تلقائياً |
| `docs/SOURCES.md` | كل المصادر وحالة التحقق |
| `docs/SKILLS.md` | المهارات المطلوبة منك |
| `prompts/` | نفس البرومبتين منفصلين |
