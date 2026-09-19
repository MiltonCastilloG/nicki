# Archive: flexibility

## Task

- **slug:** `flexibility`
- **title:** Flexibility — ad-hoc, informal jump, drop-sequence, artifact ownership
- **branch:** `main`
- **type:** docs

## Story

ad-hoc direct sheep · informal jump · drop sequence/override · artifact ownership/position · jump blocker resolved

## Outcome

Target `main`. No feature branch (`pushed_branch` null). Source-document join — no task, no `status.json`.

## Process

Joined flexibility writeups + `jump_blocker` + ADR trio into one archive under `docs/archive/flexibility/`. Shipped model documented in archived sources. Pending leftovers (quoting, CI, dogfood) remain for live thin `flexibility.md`.

Copied verbatim: `flexibility.md`, `flexibility_next_steps.md`, `jump_blocker.md`, `2026-07-30-informal-jump-and-drop-execution-design.md`, `2026-07-31-drop-sequence-and-override-design.md`, `2026-08-01-artifact-ownership-and-position-design.md`. Removed from live: next-steps, jump-blocker, and the three ADR files. Left live: `docs/flexibility.md` for thin rewrite.

## Decisions

- One flexibility archive owns the three ADRs (informal-jump, drop-sequence, artifact-ownership).
- Live docs should point at `docs/archive/flexibility/report.md`.

## Suggestions

- Thin-rewrite `docs/flexibility.md` to summary + pointer here + pending only.
