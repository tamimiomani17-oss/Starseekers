# أوامر Claude Code — انسخ والصق بالترتيب

## 0) تجهيز (مرة وحدة)

```powershell
cd "<PROJECT_ROOT>"
git config --global user.name "Omar Altamimi"
git config --global user.email "<your-email>"
claude --model sonnet
```

## 1) Prompt 1B (Sonnet)

```
/clear
اقرأ CLAUDE.md ثم نفّذ prompts/PROMPT_1B_validate_and_fix.md بالكامل. لا تنزّل ملفات كبيرة بدون سؤالي. لا تعمل push. اختم بملخص 5 أسطر.
```

## 2) Prompt 2 — مرحلة A: الخريطة (Sonnet)

```
/clear
اقرأ CLAUDE.md ثم نفّذ prompts/PROMPT_2_web_prototype.md مرحلة A فقط. اختبرها محلياً، اعمل commit "Checkpoint 2A" بدون push، وتوقف بملخص 5 أسطر.
```

## 3) مرحلة B: المسار + UNSAFE (Sonnet)

```
/clear
اقرأ CLAUDE.md ثم نفّذ prompts/PROMPT_2_web_prototype.md مرحلة B فقط (A*، 3 أنماط، علم UNSAFE، test_astar.js). شغّل الاختبار، commit "Checkpoint 2B" بدون push، وتوقف بملخص 5 أسطر.
```

## 4) مرحلة C: التتبع (Sonnet)

```
/clear
اقرأ CLAUDE.md ثم نفّذ prompts/PROMPT_2_web_prototype.md مرحلة C فقط (الروفر المحاكى، دائرة عدم اليقين، رسم الدقة). commit "Checkpoint 2C" بدون push، وتوقف بملخص 5 أسطر.
```

## 5) مرحلة D: التصميم (Sonnet)

```
/clear
اقرأ CLAUDE.md ثم نفّذ prompts/PROMPT_2_web_prototype.md مرحلة D فقط. طبّق تصميم design/ (صحّح الأخطاء الإملائية، العنوان "StarSeekers Mars Trackers"). commit "Checkpoint 2D" بدون push، وتوقف بملخص 5 أسطر.
```

## 6) مرحلة E: النشر (Sonnet)

```
/clear
اقرأ CLAUDE.md ثم نفّذ prompts/PROMPT_2_web_prototype.md مرحلة E فقط (workflow لـGitHub Pages، README بالمراجع وإفصاح AI-assisted). لا تعمل push، أعطني أوامر الـpush فقط.
```

## 7) تشغيل الموقع محلياً (نافذة PowerShell ثانية)

```powershell
cd "<PROJECT_ROOT>\web"
python -m http.server 8000
```

افتح `http://localhost:8000`

## 8) Push (بعد موافقتك فقط)

```powershell
git push origin main
```

ثم: GitHub → Settings → Pages → Source: GitHub Actions.

## متى تغيّر المودل

| الحالة | الأمر |
|---|---|
| باج ما انحل بمحاولتين (A*، إحداثيات) | `/model opus` ثم ارجع `/model sonnet` |
| README / ترجمة / commit message | `/model haiku` |

## لو علق أو غلط

```
/clear
اقرأ CLAUDE.md. المشكلة: <اكتبها بسطر>. صلّحها فقط، لا تغيّر غيرها.
```
