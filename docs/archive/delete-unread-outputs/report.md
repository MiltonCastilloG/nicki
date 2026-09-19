# Archive: delete-unread-outputs

## Task

- **slug:** `delete-unread-outputs`
- **title:** Delete outputs nothing reads
- **branch:** `main`
- **type:** refactor

## Story

drop source_context · drop outcome.status/final_artifact · story.md optional · completed_status gone · open_questions holds next_step · fallback no artifact · start returns worktree only · no status after start · close tail gate deleted · phantom syncs/integrates prose fixed

## Outcome

Target `main`. No feature branch pushed (`pushed_branch` null). Landed on local `main`.

Ad-hoc source-document archive from `docs/superpowers/specs/2026-08-05-delete-unread-outputs-design.md`. No `status.json`, no errors path — no `errors.json`. No `story.md` (no story path). Checklist at `docs/adhoc/delete-unread-outputs/subtasks.md` used for process/decisions context only. Design ADR now lives at `docs/archive/delete-unread-outputs/2026-08-05-delete-unread-outputs-design.md`.

## Process

Prior archive had empty process: no handoff pointers, no `side_effects`. Source: design doc (status implemented) plus checked ad-hoc subtasks.

- **archive** — Design ADR paired into archive as `2026-08-05-delete-unread-outputs-design.md`; live `docs/superpowers/specs/2026-08-05-delete-unread-outputs-design.md` deleted.

## Decisions

- No caller-owned output contract — delete unread fields instead.
- Archive: drop `meta.source_context`, `outcome.status`, `outcome.final_artifact`; keep `target` / `pushed_branch`.
- `story.md` optional when present.
- Drop `completed_status`; non-empty `open_questions` holds `next_step`.
- Precedence: explicit summary `next_step` → open_questions hold → routing.
- Fallback returns no `artifact`; start returns `worktree` / `open_questions` / `summary` only; no status write after start.
- Close integrate-handoff tail gate deleted; Nicki confirm stays.
- Review/sync stay prose; no new validation.

## Suggestions

1. **subtasking** — Collapse confirm-already-matches lines into one acceptance/smoke pass; keep real edit lines.
2. **orchestration** — Dogfood this archive shape: no `source_context` / `outcome.status` / `final_artifact`; skip `story.md` when no story path.
