# Archive: stop-and-ask

## Task

- **slug:** `stop-and-ask`
- **title:** Sheep stop and ask
- **branch:** `main`
- **type:** fix

## Story

sheep emit open_questions · orchestrator asks · fresh re-spawn · pause-context for spec/subtasks · describe escalates · conflicts stay with sheep · ask lines rewritten · reviews/ graveyard cleared

## Outcome

Target `main`. `pushed_branch` null. Source-document archive from `docs/superpowers/specs/2026-08-06-stop-and-ask-design.md`. No `status.json`, no errors path — no `errors.json`. No story path — no `story.md`. Spec/subtasks cleanup skipped (no worktree artifact pointers).

## Process

Empty. No handoff pointers, no `side_effects`. Checklist at `docs/adhoc/stop-and-ask/subtasks.md` used for decisions context only.

## Decisions

- Orchestrator asks the human; sheep never do.
- Questions travel as `open_questions` entries (`question` + optional `options`/`context`); no schema.
- Host ask tool named only in `nicki-default.mdc` and `CLAUDE.md`.
- Continuation is a fresh spawn with answers; disk holds work state.
- `pause-context`: caller-named, resume-gated, deleted on completion, never a handoff.
- `describe` escalates interview/approval to the orchestrator; sheep writes the approved story.
- Merge conflicts stay with the sheep across pause and re-spawn.
- Every sheep-run "ask" line → return question and stop.
- `reviews/` and `review-validations/` cleared from live scaffolding and docs.

## Suggestions

1. **orchestration** — Dogfood a live conflict pause round-trip (inventory → AskQuestion → re-spawn apply).
2. **orchestration** — Dogfood paused-spec resume from a named pause file; confirm delete-on-complete and ignore-when-unnamed.
