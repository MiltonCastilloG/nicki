# host-runtime-symlink

## Task

- **slug:** host-runtime-symlink
- **title:** Host runtime symlink (Approach A)
- **branch:** chore/host-runtime-symlink
- **type:** chore

## Story

RUNTIME_ROOT · link_dir · agents/skills symlinks · CLAUDE.md adapter · copy fallback · README · Approach B backlog

## Outcome

`pending_integrate` — feature branch `chore/host-runtime-symlink` synced and pushed (`573aa7d`). Sync handoff: `current-task/syncs/host-runtime-symlink.yaml`. Integrate not run yet.

## Process

**describe** — Gherkin story for Approach A: symlink `.claude` agents/skills into `.cursor/`; `CLAUDE.md` stays generated adapter.

**spec** — Captured `RUNTIME_ROOT`, `link_dir`, symlink install, copy fallback, README, Approach B backlog row.

**subtasks** — Ten checklist items for installer refactor, docs, temp-clone manual check.

**execute** — Complete (10/10). Changed `install-claude.py`, `README.md`, `docs/tasks.md`. Temp-clone asserts exit 0.

**review** — Approved; readiness `ready_for_acceptance`; no blocking or deferred findings.

**sync** — Committed and pushed `chore/host-runtime-symlink` (`573aa7d`); `pre_push_merge` merged.

## Decisions

- Canonical runtime stays under `.cursor/agents` and `.cursor/skills`.
- Claude install uses relative directory symlinks via `link_dir`; `CLAUDE.md` remains a generated adapter.
- `RUNTIME_ROOT = .cursor` is the sole source-path knob for Approach B.
- Symlink rejection falls back to copytree with a re-run warning (exit 0).
- Scope is Approach A only — no neutral-dir extract, `install-cursor.py`, or host registry.
