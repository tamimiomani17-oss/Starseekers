# Claude Code — أمرين فقط

## تجهيز (مرة وحدة)

```powershell
cd "<PROJECT_ROOT>"
git config --global user.name "Omar Altamimi"
git config --global user.email "<your-email>"
claude --model sonnet
```

## الأمر 1 — البيانات + الموقع الأساسي (Sonnet)

```
/clear
اقرأ CLAUDE.md. نفّذ بالترتيب بدون توقف بينهم:
1) prompts/PROMPT_1B_validate_and_fix.md بالكامل.
2) prompts/PROMPT_2_web_prototype.md المراحل A و B و C (الخريطة، المسار مع UNSAFE واختبار A*، التتبع مع دائرة عدم اليقين).
بعد كل مرحلة: شغّل الاختبار، واعمل commit باسم "Checkpoint <المرحلة>" بدون push.
لا تنزّل ملفات كبيرة بدون سؤالي.
لو فشل شي مرتين: وقف واكتب المشكلة بسطرين ولا تكمل.
في الآخر: ملخص 8 أسطر (شنو اشتغل، شنو ما اشتغل).
```

## الأمر 2 — التصميم + النشر (Sonnet)

```
/clear
اقرأ CLAUDE.md. نفّذ prompts/PROMPT_2_web_prototype.md المرحلتين D و E:
D) طبّق تصميم design/ (صحّح الأخطاء الإملائية، العنوان "StarSeekers Mars Trackers").
E) workflow لـGitHub Pages، README فيه المراجع وإفصاح AI-assisted.
commit "Checkpoint D" و"Checkpoint E" بدون push. أعطني أوامر الـpush في الآخر فقط.
ملخص 8 أسطر.
```

## تشغيل الموقع (نافذة PowerShell ثانية)

```powershell
cd "<PROJECT_ROOT>\web"
python -m http.server 8000
```

افتح `http://localhost:8000`

## Push (بعد موافقتك)

```powershell
git push origin main
```

## لو علق

| الحالة | الحل |
|---|---|
| الجلسة وقفت بنص الأمر 1 | افتح جلسة جديدة، `/clear`، وقل: "اقرأ CLAUDE.md وشوف آخر Checkpoint بـ`git log`، وكمّل من المرحلة اللي بعده" |
| باج ما انحل بمحاولتين | `/model opus` ثم ارجع `/model sonnet` |
