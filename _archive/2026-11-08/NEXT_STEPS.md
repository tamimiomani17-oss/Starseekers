# StarSeekers Mars Trackers — كل المتبقي (بعد الجلسة الأولى)

ملف واحد: وين وصلنا بالأرقام الحقيقية، شنو لقيت بالفحص، شنو يحتاج قرار منك، والخطوات المتبقية مع البرومبتات.
(`START_HERE.md` كان للجلسة الأولى. هذا الملف هو المرجع من الحين.)

## 1) وين وصلنا (من ملفاتك الفعلية)

| البند | القيمة |
|---|---|
| النافذة | 10×10 كم، **الحالة B** (بديلة): المربع اللي يحوي أطول مسار حقيقي لـ Perseverance |
| الزوايا (lon/lat) | SW 77.2955 / 18.3842 · NE 77.4642 / 18.5529 |
| الشبكة | 1000×1000 خلية، كل خلية 10 م، إحداثيات محلية بالمتر من الركن الجنوبي الغربي |
| مصدر الارتفاع | HiRISE DTM بدقة 1 م (الملف الكامل 1.84 GB، النافذة 10000×10000 بكسل) |
| مسار الروفر داخل النافذة | **31.7 كم** |
| آخر نقطة للروفر | sol 2022، lon 77.2332، lat 18.4356: **خارج النافذة، غرب الحافة الغربية بحوالي 3.7 كم** |
| الانحدار | من 0.1° إلى 59.9° (أقصى قيمة في كل بلوك 10 م) |
| الخلايا الممنوعة | 1.02% (انحدار ≥ 25°) |
| النعومة (THEMIS) | تغطية كاملة، 0% معبّأ بالوسيط |
| فحوصات الجلسة 1 | a, b, c, d نجحت كلها |
| حجم `web/data/` | 7.99 MB |

**ملفات `web/data/`:** `cost.bin` · `slope.bin` · `softness.bin` (كل واحد 1 MB) · `hillshade.png` (2000×2000، 1.96 MB) · `difficulty.png` (1000×1000، 2.57 MB) · `traverse.json` (454 KB) · `landmarks.json` · `meta.json`.
**ترتيب الصفوف:** أول صف = **الجنوب** في ملفات `.bin`، وأول صف = **الشمال** في الصور. (أكبر مصدر أخطاء للخريطة المقلوبة.)

## 2) شنو لقيت بالفحص (بصراحة)

| # | الملاحظة | الخطورة | الإجراء |
|---|---|---|---|
| 1 | **الشريط الغربي الأحمر** (عرضه حوالي 1 كم على كل الطول). جزء من أعلاه يبدو تضاريس وعرة حقيقية، لكن الجزء الأسفل له خطوط عمودية ونعومة غير طبيعية، وقد يكون أثر دمج في الـ DTM. ولاحظت أن مسار الروفر الحقيقي يلامسه. ما أقدر أجزم من صورة المعاينة وحدها | عالية | البرومبت 1B، الخطوة 2 |
| 2 | **المعالم الخمسة** اختيرت وأغلبها (3 من 5) على الحافة الغربية (x = 305 و425 و535 م)، غالباً بسبب نفس الشريط. تتبّع يعتمد على معالم سيئة التوزيع | عالية | البرومبت 1B، الخطوة 3 |
| 3 | **مسار الروفر الحقيقي = اختبار صدق للنموذج.** الروفر مشى هناك فعلاً، فلو النموذج يعتبر أجزاء كبيرة منه "خطرة جداً" أو "ممنوعة" فالنموذج متشائم | عالية | البرومبت 1B، الخطوة 1 |
| 4 | **الألوان ما تطابق تصميمك.** تصميمك: أبيض (صخر صلب) ثم أصفر ثم برتقالي ثم أحمر غامق (ممنوع). المعاينة الحالية: رمادي/أخضر ثم أصفر ثم أحمر | متوسطة | 1B، الخطوة 4 |
| 5 | **الروفر خارج النافذة.** أي مؤشر "الروفر الآن" داخل الخريطة سيكون خطأ | متوسطة | البرومبت 2 يعالجه (مؤشر خارج الخريطة) |
| 6 | **تصميم Canva فيه أخطاء كتابة:** "TIME REAIMNING (WH)" لازم تكون "Time remaining (h)"، و"BJET" ما تعني شي، وبعض النص العربي مشوّه. والعنوان "Mars Navigator" غير اسم المشروع | متوسطة | البرومبت 2 يمنع نسخها |
| 7 | **البرومبت 2 على جهازك قديم:** ما فيه قاعدة "المسار غير الآمن". النسخة الجديدة تحته | متوسطة | استبدله |
| 8 | سمح Claude Code لنفسه يقرأ حوالي 850 MB بدون ما يسألك (لأنك قلت "بدون توقف"). مقبول هالمرة، لكن انتبه للتكلفة والتنزيلات | منخفضة | |
| 9 | الـ commit باسم "Omar Altamimi" عبر إعداد مؤقت. إعداد git العام عندك ما زال فاضي | منخفضة | شغّل مرة وحدة: `git config --global user.name "..."` و`git config --global user.email "..."` |
| 10 | اسم مجلدك عربي ويعطّل شهادة curl في GDAL. حلّه Claude Code في `python/common.py`. **لا تنقل السكربتات بدون هذا الملف** | معلومة | |

## 3) قرارات أحتاجها منك قبل البرومبت 2

| القرار | توصيتي | ليش |
|---|---|---|
| مقياس الطاقة في اللوحة | **Energy index** (نسبي، بدون وحدة) | ما عندنا بيانات استهلاك Wh حقيقية، وأي رقم Wh سيكون مخترعاً. لو تبي Wh نكتبها "Wh (assumed)" |
| الشريط الغربي لو ثبت أنه artifact | نعرضه **بخطوط مائلة (low confidence)** ونمنع المسارات منه | أشرف من إخفائه، ويعطيك نقطة صدق في العرض |
| وضع التعليم (replay مسار Perseverance) | **اختياري، بعد ما يشتغل التتبع** | يزيد الجاذبية، لكنه ليس أساس المشروع |
| أرقام عتبة "غير آمن" (0.6 / 15% / 0.8) | نبدأ بها، ونضبطها بعد نتيجة التحقق من المسار الحقيقي | أرقامي افتراضية، والمسار الحقيقي يعطينا مرجع |

## 4) الخطوات المتبقية بالترتيب

| # | الخطوة | الموديل | الزمن (تقديري مني) |
|---|---|---|---|
| 1 | استبدل البرومبت 2 على جهازك بالنسخة اللي في آخر هذا الملف، وضع هذا الملف في المجلد | | 5 د |
| 2 | **البرومبت 1B** (تحقق وإصلاح) | Sonnet | 30-60 د |
| 3 | راجع الناتج بعينك (`west_strip.png`, `docs/VALIDATION.md`, المعالم الجديدة) وقرر | أنت | 15 د |
| 4 | `/clear` ثم **البرومبت 2** (الصفحة، المسارات، التتبع، التصميم) | Sonnet | 3-6 ساعات مع الـ checkpoints |
| 5 | مراجعة الفريق (الأسئلة في الفصل 7) | بشر | يوم |
| 6 | حزمة العرض ونشر الرابط | Haiku للنصوص | يوم |

**الأوامر:**

```
cd "<PROJECT_ROOT>"
claude
/model sonnet
```

ثم الصق البرومبت 1B. بعد الـ CHECKPOINT اكتب `/clear` ثم البرومبت 2.

### البرومبت 1B (الصقه كاملاً)

````markdown
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
````


**بعد CHECKPOINT 1B تأكد من:**

| الملف | شنو تشوف |
|---|---|
| `docs/VALIDATION.md` | متوسط الخطر على مسار الروفر الحقيقي، ونسبة "ممنوع" (لازم قريبة من 0%) |
| `data/processed/west_strip.png` | هل فيه قفزات حادة أو خطوط ثابتة؟ الحكم النهائي: artifact / حقيقي / غير واضح |
| `web/data/landmarks.json` | المعالم موزعة، وبعيدة عن الحواف |
| `web/data/classes.json` | 5 فئات بألوان تصميمك |

ثم:

```
/clear
```

### البرومبت 2 (الصقه كاملاً بعد 1B)

````markdown
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
````


## 5) تأكد عند كل CHECKPOINT

| CP | شنو تشوف بعينك |
|---|---|
| A | الخريطة تفتح، الصور منطبقة (الجنوب تحت)، مسار Perseverance على التضاريس، مؤشر "الروفر الآن 3.7 كم غرباً" |
| B | نقرتين = 3 مسارات + جدول (الطول، الوقت، الطاقة، أقصى ميل، متوسط الخطر، Status). مسار سريع خطر = **UNSAFE** ولا يُوصى به |
| C | الدائرة تكبر على الرمل والميل وتصغر عند المعالم، والتنبيه يوقف ويعيد التخطيط |
| D | الشكل يطابق التصميم، عربي + إنجليزي، بدون الأخطاء الإملائية |
| E | يشتغل على الجوال، وخطوات النشر واضحة |

تشغيل محلي:

```
python -m http.server 8000 --directory web
```

ثم http://localhost:8000

## 6) بعد البرومبت 2: تسليم الهاكاثون

**نشر:** GitHub Pages لا ينشر مجلد `web/` مباشرة. البرومبت 2 يرتب Actions workflow ويعطيك خطوات النقر. احفظ **نسخة offline** (zip + `python -m http.server`) احتياطاً لو الإنترنت وقع بالعرض.

**قصة العرض (3 دقائق):**

| الدقيقة | المحتوى |
|---|---|
| 0:00 | المشكلة: لا GPS، تأخير 3-22 د، الرمل علّق Spirit وOpportunity |
| 0:40 | خريطة الصعوبة على Jezero (بيانات HiRISE وTHEMIS الحقيقية) |
| 1:10 | **ديمو:** تنقر نقطتين، 3 مسارات، السريع منها مصنّف UNSAFE |
| 1:50 | **ديمو:** الروفر يمشي، الدائرة تكبر على الرمل وتصغر عند معلم، تنبيه انزلاق، إعادة تخطيط |
| 2:30 | **الصدق:** معاملات غير معايَرة، ومسار Perseverance الحقيقي استخدمناه للتحقق |
| 2:50 | الخطوة القادمة: معايرة من بيانات انزلاق منشورة، مواقع أكثر |

**نقطتك القوية:** تحقق النموذج على مسار الروفر الحقيقي (`docs/VALIDATION.md`). قلّة من الفرق تفعل هذا.

**أسئلة متوقعة من المحكمين وإجاباتها الصادقة:**

| السؤال | الجواب |
|---|---|
| ليش الأرقام "غير معايَرة"؟ | لأن معاملات السرعة والطاقة افتراضات. التحقق على مسار الروفر الحقيقي هو الخطوة الأولى، والمعايرة من منحنيات slip-vs-slope المنشورة هي الخطوة التالية |
| ليش thermal inertia؟ | مؤشر تقريبي لنعومة التربة، ما عندنا قياس مباشر عند كل خلية |
| ليش موقع واحد؟ | البيانات عالية الدقة (HiRISE 1 م) متوفرة لمواقع محدودة، وبدأنا بالأفضل تغطية |
| هل هو تتبع حي؟ | لا، محاكاة. بيانات Perseverance منشورة كنقاط وليست telemetry حي |

## 7) مراجعة الفريق (أسئلة محددة تعطي ملاحظات أحسن)

| المراجع | يراجع | الأسئلة |
|---|---|---|
| Python | `python/04_terrain.py` وصيغة الخطر | هل حساب الميل (baseline 5 م ثم max لكل 10 م) منطقي؟ هل الأوزان معقولة؟ هل المعاينة تبدو واقعية؟ |
| C++ | A* في `web/app.js` | هل المسار يتجنب الخلايا الممنوعة؟ هل تكلفة القطر صحيحة؟ هل الـ heap سليم؟ الاختبار `test_astar.js` يغطي الحالات؟ |
| ميكانيكي (أنت) | `config/params.json` | هل معاملات السرعة والطاقة والانزلاق معقولة بفيزياء العجلة والتربة؟ |
| أي شخص | الواجهة | يقدر يستخدمها بدون شرح؟ |

إذا ما أحد يعرف JavaScript، قل لـ Claude Code يبقي الكود صغير وموثّق بالتعليقات.

## 8) أسئلة ما زالت مفتوحة عندي

1. **متى الهاكاثون وكم مدته؟ وهل له موضوع ومعايير تحكيم؟** (ما أجبتني للحين. بدونها ما أقدر أحدد جدول الأسابيع الأخيرة.)
2. هل فريقك يعرف JavaScript؟
3. قرار الطاقة: index أو Wh (assumed)؟

## 9) الحدود الصريحة

- نعومة التربة من thermal inertia: مؤشر وليس قياساً. ما عندنا rock abundance، فالخشونة بديل.
- معاملات السرعة والطاقة والانزلاق والعتبات (0.6، 15%، 0.8) افتراضات حتى تُعايَر.
- المسارات تُحسب على شبكة 10 م، وهذا ليس دقة روفر حقيقي.
- بيانات Perseverance نقاط منشورة، وآخر نقطة (sol 2022) خارج النافذة.
- الأزمنة في هذا الملف تقديرية مني.
