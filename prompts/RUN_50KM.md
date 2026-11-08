# تشغيل أمري 50 كم (الترتيب مهم)

**قاعدة مهمة:** `/clear` يُرسل **لوحده** ثم Enter. لا تلصقه مع النص (النص بعده يضيع). الجلسة الجديدة من `claude` ما تحتاج `/clear`.

```powershell
cd "C:\Users\intel11\Desktop\Life\هاكاثون ناسا\26\starseekers-mars-trackers"
claude --model sonnet
```

## الأمر 1 — بحث دقيق (بدون بناء)
الصق هذا فقط (الجلسة جديدة):
```
اقرأ CLAUDE.md. نفّذ prompts/PROMPT_3_research_50km.md بالكامل. لا تبني ولا تعدّل web/. لا تنزّل شي > 500 MB. commit بدون push. ملخص 10 أسطر.
```
بعده: اقرأ `docs/RESEARCH_50KM.md` وجاوب على "أسئلة لعمر" (خاصة أي تنزيل كبير).

## الأمر 2 — بناء + تنظيم
1) أرسل `/clear` لوحده، Enter، انتظر "Context cleared".
2) ثم الصق:
```
اقرأ CLAUDE.md و docs/RESEARCH_50KM.md. نفّذ prompts/PROMPT_4_build_50km.md بالترتيب (O ثم 1 ثم 1ب ثم 2 ثم 3 ثم 4 ثم 5)، commit بعد كل مرحلة بدون push. لو فشل شي مرتين وقف. ملخص 10 أسطر.
```

## قبل أي push
افتح `http://localhost:8000` وجرّب بنفسك، ثم `git push origin main`. الموقع الحي: https://starseekers-three.vercel.app

## لو علق
| الحالة | الحل |
|---|---|
| وقفت الجلسة بنصف الأمر 2 | `/clear` لوحده، ثم: "اقرأ CLAUDE.md وآخر Checkpoint بـ git log وكمّل من اللي بعده" |
| باج ما انحل بمحاولتين | `/model opus` ثم رجّع `/model sonnet` |
