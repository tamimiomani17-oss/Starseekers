# Which model, and how to spend fewer tokens

## Model choice (relative, no price claims)
| Task | Model | Why |
|---|---|---|
| Whole build (Prompt 1 + 2) | **Sonnet 5.5** (`/model sonnet`) | Strong enough for Python + vanilla JS + A*, much lighter than the top tiers |
| Mechanical chores: README text, renames, small CSS tweaks, formatting | **Haiku 5.5** | Cheapest, fine for simple edits |
| Stuck on a hard bug (CRS/projection mismatch, A* performance) | Opus 5.5, only for that one problem, then switch back | Use sparingly |
| Not needed | Fable / Mythos tier | Overkill for this project |

## Token-saving habits
1. `CLAUDE.md` carries the context, so run `/clear` between Prompt 1 and Prompt 2.
2. Stop at every CHECKPOINT. Don't let it free-run.
3. Never paste data into the chat. Scripts print summaries only (shapes, ranges, counts).
4. Keep the design as 3-6 exported images, not a huge PDF.
5. One problem per message when debugging; include the exact error, not the whole log.
6. Use plan mode (Shift+Tab) for Prompt 2 stage A only if you want to review before it writes.
7. Commit after each checkpoint so a bad turn is cheap to undo.
