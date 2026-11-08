# Archive log 2026-11-08 (moved, not deleted; restore with `git mv`; safety tag `pre-organize-2026-11-08`)
| File | Why moved | Restore |
|---|---|---|
| START_HERE.md | old setup guide, superseded by README/CLAUDE.md; only referenced by archived files | `git mv _archive/2026-11-08/START_HERE.md .` |
| NEXT_STEPS.md | old plan, superseded | `git mv _archive/2026-11-08/NEXT_STEPS.md .` |
| HACKATHON_PLAN.md | old plan, superseded | `git mv _archive/2026-11-08/HACKATHON_PLAN.md .` |
| CLAUDE_CODE_COMMANDS.md | old command cheat-sheet | `git mv _archive/2026-11-08/CLAUDE_CODE_COMMANDS.md .` |
| CLAUDE_CODE_2_PROMPTS.md | old prompts copy (real ones are in `prompts/`) | `git mv _archive/2026-11-08/CLAUDE_CODE_2_PROMPTS.md .` |
Also: local paths/email in these files replaced by `<PROJECT_ROOT>` / `<your-email>`; `design/` WhatsApp image renamed to `concept_canva_2026-11-06.jpeg`.
| web/data/wide/mask.bin | not read by the web app (no-data already encoded in wide/cost.bin = 255 and wide/difficulty.png); now written to data/processed/mask_wide.bin by `12_export_wide.py` | `git mv _archive/2026-11-08/web/data/wide/mask.bin web/data/wide/` |
Kept on purpose: `web/data/traverse.json` (not loaded by the web app any more, but read by `python/06_validate.py`).
Deleted (allowed exception): auto-generated `__pycache__`.
