# StarSeekers Mars Trackers — الخطة المحدّثة (7 نوفمبر 2026)

> يحل محل جدول الـ8 أسابيع في NEXT_STEPS.md. باقي 7 أيام للهاكاثون.

## 1. الحقائق

| البند | المعلومة |
|---|---|
| الحدث | NASA Space Apps Challenge 2026، ثيم "The Next Frontier" |
| الموعد | السبت 14 – الأحد 15 نوفمبر (48 ساعة) |
| التسليم | يفتح 14 نوفمبر 9:00 ص، يسكر 15 نوفمبر 11:59 م (توقيت المنطقة) |
| التحكيم | يبدأ 16 نوفمبر |
| الفريق | 1–6 (أنتم 5) |
| التحدي المطابق | **Interplanetary Survival Guide: Martian Map** (Human Exploration، Mars) |
| نص التحدي (ملخص) | عرض متعدد الطبقات لموقع/مسار على سطح المريخ، يجمع بيانات من عدة مهمات NASA، ويساعد مستكشفاً بشرياً على تخطيط Marswalk ناجح |
| المطلوب للتسليم | صفحة مشروع، فيديو ديمو، مراجع (Resources)، إنجليزي |
| غير مؤكد | صفحة Ibra المحلية (المكان/الجدول/محكمين محليين)، وهل الكود الجاهز مسموح |

**ميزتكم مقابل فرق ثانية على نفس التحدي (Street View، 3D، طقس):**
صعوبة التضاريس + علم UNSAFE + دائرة عدم اليقين في التتبع. لا تنافسون في الكماليات.

## 2. اسألوا المنظمين اليوم (إنجليزي، انسخ وأرسل)

```
Hello, we are team StarSeekers registered for NASA Space Apps Ibra 2026.
1) Is code and data prepared before the event allowed, or must the app be built during the 48 hours?
2) What do you need for final submission (project page, demo video, repository link)?
3) Is there a local judging round, and when/where is the venue schedule?
Thank you.
```

**لو الجواب "لازم يُبنى داخل الحدث":** نجهز قبل الحدث البيانات والـpipeline (Python) والتصميم والـprompts فقط، ونبني الواجهة (Prompt 2) يومي 14–15.

## 3. الجدول (7–15 نوفمبر)

| اليوم | الشغل | المخرج |
|---|---|---|
| **السبت 7** | Prompt 1B + إرسال سؤال المنظمين | `docs/VALIDATION.md`، معالم جديدة، classes.json |
| الأحد 8 | Prompt 2 مرحلة A (الخريطة) | خريطة Leaflet تشتغل محلياً |
| الاثنين 9 | مرحلة B (A* + 3 أنماط + UNSAFE + test_astar.js) | تخطيط مسار |
| الثلاثاء 10 | مرحلة C (التتبع + دائرة عدم اليقين + الرسم) | محاكي الروفر |
| الأربعاء 11 | مرحلة D (تصميم Canva، العنوان "StarSeekers Mars Trackers") | واجهة مطابقة للتصميم |
| الخميس 12 | مرحلة E: GitHub Pages + نسخة أوفلاين + تجربة على لابتوب ثاني | رابط يفتح بنقرة |
| الجمعة 13 | تجميد الكود، مسودة الـpitch، سكربت الفيديو | pitch 3 دقائق |
| **السبت 14** | تسجيل التحدي الرسمي، صقل، تصوير الفيديو | فيديو ديمو |
| **الأحد 15** | تعبئة صفحة المشروع، المراجع، رفع. **سلّموا قبل 9 م** (مو 11:59) | تسليم |

قاعدة: أي مرحلة تتأخر يوم، نقص منها (الاستعادة Perseverance replay أولاً) ولا نمدد.

## 4. المودل في Claude Code

| المهمة | المودل | الأمر |
|---|---|---|
| البناء الرئيسي (Prompt 1B, 2A–E) | **Sonnet 5.5** | `/model sonnet` |
| مهام خفيفة (README، تنسيق، commit message، ترجمة) | **Haiku 5.5** | `/model haiku` |
| باج صعب فقط (A* غلط، CRS، تحويل إحداثيات) | **Opus 5.5** | `/model opus` ثم ارجع Sonnet |
| لا تحتاجون | Fable / Mythos | — |

توفير التوكنز: `/clear` بين كل Prompt، CLAUDE.md هو الذاكرة، لا تلصق ملفات كبيرة، اطلب "لا تنزل ملفات كبيرة بدون سؤالي".

## 5. الأوامر (PowerShell داخل مجلد المشروع)

```powershell
cd "<PROJECT_ROOT>"
git config --global user.name "Omar Altamimi"
git config --global user.email "<your-email>"
git status
claude --model sonnet
```

داخل Claude Code:

```
/clear
اقرأ CLAUDE.md ثم نفّذ prompts/PROMPT_1B_validate_and_fix.md بالكامل. لا تنزّل ملفات كبيرة بدون سؤالي. لا تعمل push.
```

بعد 1B:

```
/clear
اقرأ CLAUDE.md ثم نفّذ prompts/PROMPT_2_web_prototype.md مرحلة A فقط. توقف بعدها وأعطني ملخصاً قصيراً.
```

وهكذا B ثم C ثم D ثم E (كل مرة `/clear` ثم مرحلة واحدة).

تشغيل الموقع محلياً (Python):

```powershell
cd web
python -m http.server 8000
```

ثم افتح `http://localhost:8000`.

## 6. Prompt 1B (ملخص، النص الكامل في prompts/)

1. شغّل `python/06_validate.py`: قارن النموذج بمسار Perseverance الحقيقي → `docs/VALIDATION.md`
2. افحص الشريط الأحمر الغربي (artifact أو حقيقي؟) → `data/processed/west_strip.png`
3. اختر 5 معالم جديدة: بعيدة ≥600 م عن الحواف و≥1.5 كم عن بعض
4. أعد توليد `difficulty.png` بألوان Canva (5 فئات) وصدّر `web/data/classes.json`
5. أضف "Status after Prompt 1/1B" في CLAUDE.md
6. commit باسم "Checkpoint 1B"، بدون push

## 7. Prompt 2 المراحل

| المرحلة | المحتوى |
|---|---|
| A | خريطة Leaflet (`L.CRS.Simple`)، طبقات: hillshade / difficulty / traverse / landmarks |
| B | A* (8 جيران، heap)، أنماط safe/fast/power، علم UNSAFE، `test_astar.js` |
| C | تتبع روفر محاكى، دائرة عدم اليقين (تكبر وتصغر عند المعلم)، رسم الدقة على المسار، إعادة تشغيل Perseverance اختياري |
| D | تطبيق تصميم Canva (تصحيح الأخطاء الإملائية، العنوان الجديد) |
| E | ختام + GitHub Pages عبر Actions |

نموذج الخطر (افتراضات غير معايرة، اكتب على الواجهة "Educational estimate - uncalibrated"):
`risk = clamp(0.5*slope/25 + 0.25*rough_norm + 0.25*softness, 0, 1)`، محجوب إذا الميل ≥ 25°.
UNSAFE: متوسط risk > 0.6 أو أكثر من 15% خلايا risk > 0.8.

## 8. البيانات: ثابتة + تحديث مجدول

- التضاريس (DTM, THEMIS): ملفات ثابتة، ما تتغير.
- مسار Perseverance: سكربت `python/01_fetch_waypoints.py` يحمّل آخر ملف NASA ويعيد كتابة `traverse.json`. شغّلوه يدوياً قبل الديمو (أو GitHub Action يومي).
- الصفحة تعرض "Data updated on: <تاريخ>".
- موقع الروفر الأخير خارج النافذة، اعرضوه كمؤشر خارج الخريطة.
- لا Supabase ولا Vercel ولا خادم. المتصفح ما يستدعي NASA مباشرة (خطر حجب/بطء).

## 9. GitHub

```powershell
git add .
git commit -m "Checkpoint"
git push origin main
```

- لا تعملوا push إلا بعد موافقتك.
- الملف 1.84 GB (DTM) مستثنى من git، مجلد `web/data` (~8 MB) يُرفع.
- راجعوا الـprompts والملاحظات: لا كلمات سر ولا معلومات شخصية.
- GitHub Pages: Settings → Pages → Source: GitHub Actions (المرحلة E تكتب الـworkflow).
- أبقوا نسخة أوفلاين على USB ولابتوب ثاني للديمو.

## 10. التسليم (قائمة تحقق)

- [ ] تسجيل الفريق والتحدي "Interplanetary Survival Guide: Martian Map" على الموقع الرسمي
- [ ] فيديو ديمو (2–3 دقائق): مشكلة → خريطة صعوبة → 3 مسارات → UNSAFE → تتبع وعدم يقين
- [ ] صفحة المشروع بالإنجليزي: وصف، رابط GitHub Pages، رابط الريبو
- [ ] **المراجع:** Mars Trek (NASA/JPL)، USGS HiRISE DTM JEZ_hirise_soc_006، THEMIS thermal inertia (Zenodo 4931348)، NASA MMGIS M20 waypoints، Leaflet
- [ ] إفصاح: البناء بمساعدة Claude Code (AI-assisted)، والأرقام تقديرية غير معايرة
- [ ] أوفلاين: الموقع شغال بدون إنترنت

## 11. Pitch (3 دقائق)

| الوقت | المحتوى |
|---|---|
| 0:00 | المشكلة: المستكشف يحتاج يعرف أين الأرض صعبة، مو بس أين الطريق |
| 0:30 | البيانات: HiRISE + THEMIS + مسار Perseverance (3 مهمات) |
| 1:00 | ديمو: خريطة الصعوبة → 3 مسارات → UNSAFE |
| 2:00 | التتبع: دائرة عدم اليقين تكبر وتصغر عند المعالم |
| 2:40 | حدودنا بصراحة + خطوات قادمة (معايرة بالروفر الحقيقي) |

أسئلة محتملة من المحكمين: كيف تحققتم؟ (VALIDATION.md) · ليش هذه الأوزان؟ (افتراضات، قابلة للمعايرة) · الفرق عن الخرائط الموجودة؟ (الصعوبة + المخاطر + عدم اليقين).

## 12. حدود صريحة

- الأوزان والعتبات افتراضات غير معايرة.
- THEMIS بدقة منخفضة كبديل للتربة الرخوة.
- الروفر المحاكى مو بيانات حقيقية للتتبع.
- لم أتمكن من قراءة الصفحات الرسمية للتحديات مباشرة (الموقع يمنع القراءة الآلية). النص من مصادر ثانوية، فتأكدوا منه من الموقع الرسمي.
