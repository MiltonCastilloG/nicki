# Archive: adhoc-direct-sheep-invocation

## Task

- **slug:** `adhoc-direct-sheep-invocation`
- **title:** Ad-hoc is direct sheep invocation
- **branch:** `main`
- **type:** refactor

## Story

ad-hoc = direct sheep spawn · no task · no status write · parent agent dispatches · Nicki keeps normal + jump · --mode adhoc removed · archive always prefix/docs/archive/slug · start/close/status stay Nicki-only

## Outcome

`pending_integrate` (skill default). Target `main`. No feature branch, no integrate handoff. Work already on local `main` (design `52432f0`, implementation `755616b`, archive path/input fix `3f4e757`). Final artifact: `docs/archive/adhoc-direct-sheep-invocation/report.json`.

This is the **second** live ad-hoc direct invocation of `sheep-archive`, after the path/input fix. First live-test scratch stays under `docs/adhoc/adhoc-direct-sheep-invocation/` (untouched).

## Process

Empty. No task `status.json`, no handoff pointers, no `side_effects`. Format only sources process from those; inventing git/design history is out of contract. Source document: `docs/superpowers/specs/2026-08-05-adhoc-direct-sheep-invocation-design.md`.

## Decisions

- Ad-hoc = parent agent spawns a sheep directly; not a status write mode.
- Nicki keeps `normal` and `jump` only; `--mode adhoc` removed.
- Ad-hoc writes no pipeline state.
- Archive always `<prefix>/docs/archive/<slug>/` (caller packs `prefix` + `slug`).
- `sheep-start` / `sheep-close` / `sheep-status` stay Nicki-only.
- `task.side_effects[]` kept for jump.

## Open questions

- Path/input contract matches this prompt: `prefix` + `slug`, no close-scope, no no-status ask, errors only if named. No errors path here — no `errors.json`. No task — deleted nothing.
- Output-shape issues remain (see `docs/adhoc/adhoc-direct-sheep-invocation/output_problem_example.md`): forced `pending_integrate`, `story.md` not written (no story artifact), empty `process`, `meta.source_context` is the design path.

## Suggestions

1. **orchestration** — Let caller set or waive `outcome.status` for main-landed / ad-hoc archives.
2. **orchestration** — Treat `story.md` as optional when there is no `artifacts.story`.
3. **orchestration** — Sanction a process source (or empty-OK) for source-document archives.
