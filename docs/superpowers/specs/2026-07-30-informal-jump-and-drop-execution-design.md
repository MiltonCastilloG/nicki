# Design: Informal jump + drop execution artifact

Date: 2026-07-30  
Status: approved for implementation — **implemented** in harness / `.cursor`  
Related: [`docs/jump_blocker.md`](../../jump_blocker.md), [`docs/flexibility.md`](../../flexibility.md), [`docs/flexibility_next_steps.md`](../../flexibility_next_steps.md)

## Problem

1. Jump assumed the user brings a **schema-shaped predecessor file**. Real input is chat paste, a design path, or a diff — almost never `specs/*.json` or `executions/*.json`.
2. Brainstorm / design `.md` could not jump to `subtasks` because the harness required a matching suffix and materialize into the predecessor slot ([`jump_blocker.md`](../../jump_blocker.md)).
3. Review’s gate required an execution JSON handoff, but review already decides from the **git diff** plus whatever exists under `current-task/`. The execution file is redundant proof.

## Goal

- Jump is **position-only**: set `next_step` to the target; leave `current_step` untouched; no predecessor artifact on the jump write.
- Chat is enough to jump. Chat may mention a document path; that does not matter to the harness.
- Sheep learn to **accept whatever** Nicki passes (chat / path / optional on-disk files). They do not own jump prerequisites.
- **Nicki + scripts** create and register artifacts. Jump does not copy or materialize files.
- **Execute never produces** an execution artifact (omit `artifact` from the return — not null).
- **Review never receives** execution JSON. Review the diff + available `current-task/` files only.

## Constraints (unchanged)

| Constraint | Means |
|---|---|
| Scripts stay authoritative | `check-gate.py`, `update-status.py`, `bootstrap-context.py` keep the veto |
| Safety / consent never waived | Jump waives **sequence** only |
| Flexibility is not `--override` | Use `--mode jump` / `--mode adhoc` |

## Decision summary

| Topic | Decision |
|---|---|
| Shipping shape | One design: informal jump + drop execution together |
| Jump write | `next_step` = target; `current_step` untouched; no summary `artifact` required |
| Jump materialize | **Remove** (no copy into `current-task/`, no suffix match on jump) |
| Ensure / convert prelude | **None** — do not run producer sheep “to ensure” files before jump |
| Sheep changes | Input flexibility only (“accept whatever”); ask / `open_questions` as today |
| Execute artifact | Stop writing `executions/*.json`; omit `artifact` on return; drop routing `artifact_key` / `expected_artifact` for execute |
| Review inputs | Never load execution JSON; gate does not require it |
| Early/mid gates | Drop hard “predecessor file must exist” for spec / subtasks / execute; review drops execution |
| Sync | Remains **adhoc**, not jump |
| Non-targets | `start`, `close`, `done` still cannot be jump targets |

## Jump behavior (harness)

`update-status.py --mode jump --step <target>`:

1. Deny if target is `start`, `close`, or `done`, or if `--step` is missing.
2. Set `task.next_step` to `<target>`.
3. Do **not** modify `task.current_step`.
4. Do **not** require or read summary `artifact` for materialize.
5. Append `task.side_effects[]` with `step` = target, `mode` = `jump`, `at` = UTC, and `artifact: null` (jump carries no file; keep the key for a stable log shape).
6. Remove `_materialize_jump_artifact`, `_dest_rel_for_jump`, `_predecessor_for` usage from the jump path, and suffix-enforcement used only by jump.

`check-gate.py --mode jump` still waives sequence denials only.

After jump, Nicki gates with `--step <target>` and spawns that sheep, forwarding the user chat (and any path the user mentioned) in the prompt.

## Nicki flows

No “ensure X exists” before jump. Pattern:

1. User asks to skip ahead (with chat / optional path / diff context).
2. If unclear which target, ask once.
3. `--mode jump --step <target>` (position only).
4. Gate target; on allow, spawn target sheep with chat as primary input.
5. Sheep may use on-disk `current-task/` files **if present**; absence is fine.
6. On sheep return, `sheep-status` with `--mode normal --step <target>` as usual (except execute omits `artifact`).

| Intent | Notes |
|---|---|
| → spec / subtasks / execute / review / describe | Jump + chat; sheep accepts whatever |
| → review | Diff / worktree is enough; planning files optional |
| sync | **Adhoc**, not jump |
| archive / integrate / acceptance / fix | Existing safety, consent, readiness — not informal-convert jumps |

## Gate changes

| Gate | Change |
|---|---|
| `gate_spec` | Do not require `artifacts.story` / story file on disk |
| `gate_subtasks` | Do not require spec file; still deny if status or (if present) spec `open_questions` non-empty |
| `gate_execute` | Do not require subtasks file |
| `gate_review` | Do not require execution artifact; drop `review_scope` loaded from execution. Partial confirm only if Nicki/review-input supplies scope and routing still demands confirm |
| sync / archive / integrate / close | Unchanged safety + consent |

Optional files remain useful when present; they are not admission tickets for those steps.

## Execute / review contract

### Execute

- Skill / sheep: do not write `current-task/executions/<slug>.json`.
- Return contract: **omit** `artifact` (better than `null`).
- `routing.json` execute step: `artifact_key: null`, `expected_artifact: null` (or remove key per existing null pattern).
- `update-status.py` normal write for execute: no execution pointer to set when artifact omitted.
- Deprecate or delete `execution-format.md` as a live writer schema; update readers that assumed the file. **Done** — file deleted 2026-07-31.

### Review

- Skill / sheep: never load execution JSON. Inputs = worktree diff + available current-task files (story, spec, subtasks, review guidance) + Nicki prompt.
- Align skill text with gate (already said missing execution is OK; make that the only path).
- Status / archive docs: remove `artifacts.execution` as a current pointer.

### Partial review confirm

Today `gate_review` reads `review_scope.mode` from the execution file. After the drop, partial scope lives only in Nicki’s prompt and/or `review-inputs` if still used. If no execution and no review-input scope, treat review as full; no special confirm.

## Sheep “accept whatever”

Update disk-input tables and skill input sections for describe, spec, subtask, execute, review:

- Primary input may be free text from Nicki’s prompt.
- On-disk predecessor files are optional context when present.
- Ask-first / non-empty `open_questions` behavior unchanged when the sheep cannot proceed.

No sheep invents pipeline position. No sheep performs jump materialize.

## Docs to update

- `.cursor/agents/nicki.md` — Jump section (position-only; chat enough; no harness convert; no ensure prelude).
- `docs/flexibility.md` — Capability B / jump write semantics; strike materialize-as-jump-payload.
- `docs/jump_blocker.md` — mark resolved by this design (Nicki + flexible sheep; harness does not convert).
- `docs/flexibility_next_steps.md` — close or retarget §1 jump format blocker.
- Routing, status-format, status-read, archive-format, review/execute sheep + skills as above.

## Tests

Update `tests/smoke/jump_mode.py` and related gate fixtures:

- Jump sets `next_step`, leaves `current_step` byte-identical; succeeds with no summary artifact; does not copy files into `current-task/`.
- Jump to `close` (and peers) still rejected.
- Remove assertions that `.md` into spec slot is rejected on jump (materialize gone).
- `gate_review` allows with no `artifacts.execution`.
- Execute status write with omitted `artifact` does not create/require `executions/*.json`.
- Optional: `gate_spec` / `gate_subtasks` / `gate_execute` allow when predecessor files are missing.

`python3 test.py` remains the entrypoint.

## Non-goals

- Harness markdown→JSON conversion.
- Finding 5 quoting hygiene; CI for smoke suite; manual dogfood (separate backlog items).
- Turning sync into a jump target.
- Requiring `current_step` to be set or cleared on jump.
- Fabricating execution JSON wrappers around diffs.

## Acceptance

- User can jump to `subtasks` (or `spec` / `execute` / `review`) with only chat; gate allows; sheep runs with that chat.
- Jump write never fails for “wrong suffix” or “artifact not found.”
- `current_step` before and after a jump write is identical; `next_step` equals the target.
- Execute completion does not create `current-task/executions/*.json` and omits `artifact` in the return forwarded to status.
- Review gate and skill never require or read an execution artifact.
- Smokes above pass via `python3 test.py`.
