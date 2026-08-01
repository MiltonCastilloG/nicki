# Design: Artifact ownership and position-as-truth

Date: 2026-08-01  
Status: **draft**  
Related: [`docs/flexibility.md`](../../flexibility.md), [`2026-07-30-informal-jump-and-drop-execution-design.md`](./2026-07-30-informal-jump-and-drop-execution-design.md), [`2026-07-31-drop-sequence-and-override-design.md`](./2026-07-31-drop-sequence-and-override-design.md)

## Problem

1. Sheep were thinned (no input catalogs), but write ownership stayed blurry: agent docs and skills both say “write the artifact,” while operational steps also drop thin handoff files (`syncs/`, `integrates/`, `review-validations/`) that mostly duplicate what pipeline position already means.
2. A hard rule that “sheep never write” is wrong: describe, spec, subtasks, and archive exist to produce documents.
3. Operational outcomes and many gates re-check the same facts as `current_step` / `next_step`, creating redundant status blobs and file contracts.

## Goal

- Split sheep into **document** vs **operational** jobs with clear write ownership.
- **Nicki owns the output path** for document writes (usually under the task worktree; adhoc may name another path explicitly).
- Drop operational handoff files; do **not** fold readiness/sync/integrate summaries into `status.json`.
- Treat **`task.next_step` (with `task.current_step`) as the workflow source of truth** for operational progress; keep `open_questions` for blockers.
- Eliminate gates that only re-derive what position already says; keep chat consent and document-file checks where a later step truly needs the file.

## Constraints

| Constraint | Means |
|---|---|
| Nicki stays non-writer of app/task bodies | She packs prompts and forwards returns; she does not author story/spec/code |
| `sheep-status` / `update-status.py` sole status writer | Only they write `current-task/status.json` |
| Worktree location already known | `global-status.json` (`worktree_path`, `status_path`), `scope.worktree_path`, bootstrap |
| No new unused position fields | Do **not** add or persist `completed_step` on status if nothing reads it — **`next_step` is enough** to maintain the workflow (`current_step` may still update as today’s write script does from Nicki’s `--step`) |
| Consent stays in chat | Explicit user yes for sync / archive / integrate / close — not a fat status object |

## Decision summary

| Topic | Decision |
|---|---|
| Document sheep | describe, spec, subtasks, archive — write the document **only** at the path Nicki puts in the prompt |
| Path ownership | **Nicki owns the path**; most cases are under the task worktree; adhoc = Nicki points at the write target |
| Operational sheep | execute, review, sync, integrate, close — job + return JSON; **no** handoff files |
| Execute | Position only — completing the step advances the workflow; no execute artifact or summary object |
| Operational status | **No** inline `readiness` / `sync` / `integrate` objects; position + `open_questions` only |
| Operational handoffs | Delete as pipeline contracts (`syncs/`, `integrates/`, `review-validations/`, etc.) |
| Gates | Drop redundant operational re-checks; keep consent flags + document/archive existence where needed |
| `completed_step` | Do not add to status schema for consumers; if nothing reads it, omit — **`next_step` maintains the workflow** |
| Gate redundancy | In scope now: remove gates that only echo position; leave consent + document-file checks |

## Roles

| Actor | Owns |
|---|---|
| **Nicki** | Pipeline; **output path** in every document-sheep prompt; worktree context when working under a task; forwards sheep return + `--step` / `--mode` to `sheep-status` |
| **Document sheep + skill** | Document content; write only where Nicki said |
| **Operational sheep + skill** | Do the job; return `completed_status`, `open_questions`, optional chat `summary` — never invent operational handoff paths |
| **sheep-status** | Persist position, document `artifacts.*` pointers, `open_questions` |

### Where path info already lives

| Source | Fields |
|---|---|
| `global-status.json` | `worktree_path`, `status_path` |
| `current-task/status.json` | `scope.worktree_path`, document `artifacts.*` |
| `bootstrap-context.py` | Resolves registry → status path, steps |
| `create-worktree.py` | Creates worktree + scaffolds `current-task/` |

## Data flow

### Document steps

1. Nicki packs prompt with **output path** (normally under worktree relatives: `current-task/story.md`, `specs/<slug>.json`, `subtasks/<slug>.md`, `docs/archive/<slug>/…`; adhoc = explicit path).
2. Sheep/skill writes the body there when clear; blocked → `open_questions`, no write.
3. Nicki → `sheep-status`: register pointer + advance position per routing.

### Operational steps

1. Nicki packs prompt (worktree / task id / chat as today; no operational output path).
2. Sheep returns thin JSON (no `artifact`).
3. Nicki → `sheep-status`: update **position** and `open_questions` only. Routing derives `next_step` (e.g. after review → acceptance or execute). Chat carries human-facing review/sync narrative.

## Status schema impact

**Keep**

- `task.current_step`, `task.next_step`
- `open_questions`
- Document pointers: `artifacts.story`, `spec`, `subtasks`, `archive`

**Remove as required pipeline surface**

- `artifacts.sync`, `artifacts.integrate`, `artifacts.review_validation`, `artifacts.review_input` (and file contracts behind them)
- Any plan to mirror readiness/sync/integrate handoff bodies onto status

**Do not introduce**

- Persisted `completed_step` (or reintroduce `completed_steps`) for workflow consumers — **`next_step` is enough**. Internal use of Nicki’s `--step` inside `update-status.py` to set `current_step` may remain an implementation detail; it is not a status field others must read.

## Gates

- **Remove / stop relying on:** checks that only re-read operational handoff files or readiness files to learn what `next_step` already encodes.
- **Keep:** `user_confirm_required` (chat consent); document/archive file presence when a later step needs that file; input-error behavior on bad status writes.
- Acceptance before first sync remains **Nicki chat confirm** (already not a sequence gate).

## Sheep return contract

| Kind | Return |
|---|---|
| Document | `artifact` (Nicki’s path), `completed_status`, `open_questions`, `summary` |
| Operational | no `artifact`; `completed_status`, `open_questions`, optional `summary` for chat |
| Execute / close | no artifact; position (close also tears down) |

Sheep still must not invent pipeline position in the return; Nicki passes `--step` / `--mode`.

## Errors

- Missing required fields for a status write → `written: false` + `errors[]`; Nicki corrects and retries (not harness failure).
- Document blocked → no file; Nicki relays `open_questions`.
- Harness script failure → `sheep-fallback` unchanged.

## Non-goals

- Nicki authoring document or code bodies herself.
- Dual persistence (operational file + status object).
- Softening consent into a silent auto-advance.
- Rewriting frozen `docs/archive/**` historical stories beyond necessary pointer notes.

## Acceptance

- Document sheep write only at Nicki-supplied paths; agent/skill docs match.
- No operational handoff files required by routing, gates, or skills.
- Status workflow for operational steps is position + `open_questions` only; no readiness/sync/integrate status blobs.
- No consumer-facing `completed_step` on status; workflow runs on `next_step` (and `current_step` as updated today).
- Redundant operational gates removed or reduced to consent + document needs.
- Smokes and Nicki/routing docs aligned; `python3 test.py` green.
