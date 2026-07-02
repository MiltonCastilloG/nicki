---
name: task-archive
description: "Write docs/archive/<slug>/ (report.yaml, report.md, story.md); erase spec and subtasks."
disable-model-invocation: true
---

# Task Archive

Draft + write archive. Format: [archive-format.md](archive-format.md).

## Inputs

| Input | Req |
|-------|-----|
| Worktree path | yes — from [close-scope](../close-scope/SKILL.md) resolve |
| `current-task/status.json` | preferred |

## Steps

1. Resolve `slug`, `repo_root`, `archive_dir` = `docs/archive/<slug>/` under `repo_root` (close-scope §1 or inline).
2. Load handoffs via status `artifacts` — [status-format.md](../current-task-update/status-format.md).
3. Set `outcome.status: pending_integrate` — integrate has not run yet.
4. Draft `report.yaml` — task, story, outcome, process (from artifact handoffs per archive-format, not status history), decisions, open_questions, suggestions.
5. Draft `report.md` — terse per caveman; mirror report.yaml.
6. Write `report.yaml` and `report.md` under `docs/archive/<slug>/`.
7. Copy `artifacts.story` → `docs/archive/<slug>/story.md`; when `current-task/specs/errors.yaml` exists, copy it verbatim → `docs/archive/<slug>/errors.yaml`; delete `artifacts.spec` and `artifacts.subtasks` from worktree when present.
8. When archived `errors.yaml` exists, note harness errors were recorded in `report.yaml` / `report.md` and reference `docs/archive/<slug>/errors.yaml` — do not paste full failure bodies.

(Commit and push via next sync step.)
