# Nicki flexibility

Date: 2026-07-29. Gate history: [`harness-gate-bugs.md`](harness-gate-bugs.md).
Next steps / leftover backlog: [`flexibility_next_steps.md`](flexibility_next_steps.md).

## Goal

Nicki is no longer a strict linear march. Two capabilities shipped:

1. **Run a step out of band.** Sync mid-`execute`, without acceptance, without moving workflow position.
2. **Accept a source of truth from outside the workflow.** Register an external artifact and jump to the sheep that consumes it (e.g. a spec produced by the `brainstorm` skill).

## Constraints

Standing. Do not trade these for convenience.

| Constraint | Means |
|---|---|
| Scripts stay authoritative | `check-gate.py`, `update-status.py`, `bootstrap-context.py` keep the veto. No decision moves back into prose. |
| `status.json` stays source of truth for pipeline state | Position is `current_step` + `next_step` + artifact pointers. Ad-hoc runs log to `side_effects` without moving position; jump moves position deliberately. |
| Safety gates never waive | Push to main, merge, worktree delete stay hard-confirmed. `--override`, `--mode adhoc`, and `--mode jump` waive **sequence** denials only. |
| Flexibility is not `--override` | Use `--mode adhoc` or `--mode jump` with their own reason strings. Reusing the blunt flag hides the next bug — see `harness-gate-bugs.md`, "Why these recur". |

## Write modes

Both `check-gate.py` and `update-status.py` take `--mode normal|adhoc|jump` (default `normal`). The gate echoes the resolved mode in stdout; Nicki forwards the same mode to `sheep-status`.

| Mode | Gate | Write | Position after write |
|---|---|---|---|
| **normal** | Standard sequence + safety checks | Sets `current_step` from `--step`; derives `next_step` from routing via `next_step_for()` | Advances along the pipeline |
| **adhoc** | Waives sequence when `adhoc_allowed`; consent and safety still apply | Records artifact pointer; appends `task.side_effects[]`; leaves `current_step` and `next_step` untouched | Unchanged |
| **jump** | Waives sequence; cannot target `start`, `close`, or `done` | Copies summary `artifact` into `current-task/` at the predecessor slot (archiveable), registers that worktree-relative pointer, sets `current_step` to the predecessor and `next_step` to the target; appends `side_effects` | Points at target sheep — Nicki gates and runs it next |

**Ad-hoc policy:** every step sets `adhoc_allowed` in `routing.json` except `start`, `close`, and `done`. `irreversible` may combine with `adhoc_allowed` (consent and safety inputs still never waive).

**Sheep return contract:** sheep return `artifact`, `completed_status`, `open_questions`, `summary` only — not `next_step` or `completed_step`. Nicki forwards the return plus the `--step` and `--mode` she dispatched.

## Position model

`task.completed_steps` is **removed**. Position is `current_step`, `next_step`, and artifact pointers only. Legacy files still carrying `completed_steps` have it stripped on the next write.

**Bootstrap stdout** (`bootstrap-context.py`): `active_task`, `status_path`, `current_step`, `next_step`, `readiness`, `sheep` — no `completed_steps`.

## Capability A — out-of-band steps

### Behavior

An ad-hoc invocation is gated for safety, runs the sheep, and leaves `current_step` and `next_step` byte-identical.

| Layer | Behavior |
|---|---|
| Gate | `check-gate.py --mode adhoc --step <requested>`; sequence denials waived when `adhoc_allowed`; safety and consent never waived |
| Sheep | Position-free return; no workflow knowledge in sheep files |
| Write | `update-status.py --mode adhoc`: artifact pointer recorded, one `task.side_effects` entry appended, position untouched |

### Side-effect trail

`task.side_effects[]` is append-only — one entry per ad-hoc or jump write, with `step`, `mode`, UTC `at`, and `artifact` (may be null). Documented in `status-format.md`.

Archive `process` is handoff rows plus one row per side-effect entry (including null artifacts) — see `archive-format.md`.

### Acceptance checks

- Ad-hoc sync during `execute`: gate allows, sheep runs, `current_step`/`next_step` byte-identical before and after.
- Artifact pointer for the ad-hoc sync is recorded; side effect appears in the log and in the archive report (`process` row).
- Ad-hoc `start` / `close` / `done`: **denied** — not `adhoc_allowed`.
- Ad-hoc on other steps (including `integrate`): **allowed** when safety inputs and consent hold; sequence-only denials are waived.
- Fixture per case, through `check-gate.py`, in `test.py`.
- Archive format contract asserts `side_effects` → `process` (including null artifact rows).

## Capability B — external source of truth

### Behavior

Jump ahead registers an external path as the prerequisite artifact for a target sheep, moves position to that target, and lets Nicki gate and run the sheep.

Typical flow (Nicki):

1. User provides a path already in the **format that slot uses** (e.g. JSON spec for jump → `subtasks`). No harness conversion from brainstorm markdown.
2. Write with `--mode jump --step <target>` and summary `artifact` set to that path. The write **copies** into `current-task/` at the predecessor `expected_artifact` when the file is outside (suffix must match); registers the worktree-relative pointer; sets position; logs `side_effects`.
3. Gate the **target** with `--step <target>` (`normal` is enough after the jump write; `--mode jump` also waives sequence if needed).
4. Spawn that step's sheep. After it returns, `sheep-status` with `--mode normal --step <target>` as usual.

`start`, `close`, and `done` are not jump targets.

### Resolved items

| Item | Status |
|---|---|
| **B1 — path scope** | Done. `artifact_path()` resolves per-key scope via `gate_utils.ROOT_SCOPED_ARTIFACTS`. |
| **B2 — register pointer without claiming a step** | Done. `--mode jump` materializes and registers the prerequisite under `current-task/`. |
| **B3 — brainstorm output does not fit the spec slot** | Wontfix. Jump copies whatever path the user provides into `current-task/`; no special `.md` loader. |
| **B4 — materialize into worktree for archive** | Done 2026-07-29 (YAGNI). Jump copies into `current-task/` only when the suffix already matches the predecessor slot. Wrong format → input error; Nicki asks or runs the normal producer sheep. No markdown↔JSON conversion in the harness. **Real-use blocker** (brainstorm `.md` → jump `subtasks`): see [`jump_blocker.md`](jump_blocker.md). |
| **B5 — status vocabulary** | Done. Skip-ahead is `--mode jump`; `completed_status` stays `complete`/`blocked` only. |

### Acceptance checks

- Jump to `subtasks` with an external spec path: file appears under `current-task/`, `artifacts.spec` points there, `next_step` is `subtasks`, side effect logged.
- Jump to `review` with an execution handoff path: prerequisite under `current-task/`, target sheep runs after gate.
- Jump to `start` / `close` / `done`: **denied**.
- Missing jump artifact path: write fails with a clear error.
- Fixture per case in `test.py`.

## Sequencing

All sequenced flexibility work is done.

| Order | Work | Status |
|---|---|---|
| 1 | Scope model for artifact paths | **Done** 2026-07-28 |
| 2 | Read `routing.json`: `default_next_step`, `artifact_key` | **Done** 2026-07-28 / 2026-07-29 |
| 3 | Gate fixtures in `test.py` | **Done** 2026-07-28 |
| 4 | Status vocabulary: enum, no-advance mode, side-effect log | **Done** 2026-07-29 |
| 5 | Consent from routing + safety vs sequence gates in `check-gate.py` | **Done** 2026-07-29 |
| 6 | Strip workflow knowledge from every `sheep-*.md` | **Done** 2026-07-29 |
| 7 | Write path: `--step`/`--mode`; `next_step_for()` on normal; wire `artifact_key` | **Done** 2026-07-29 |
| 8 | Ad-hoc sync end to end; archive reads `side_effects` | **Done** 2026-07-29 |
| 9 | Jump ahead (`--mode jump`) | **Done** 2026-07-29 |
| 10 | B4: materialize prior artifact into `current-task/` on jump | **Done** 2026-07-29 |

## Decisions

### 1. Who owns `next_step` — **routing**

Decided 2026-07-28.

- Sheep return handoff only: artifact, `completed_status`, blockers — **not** `next_step` or `completed_step`.
- On normal completion, `update-status.py` sets `task.next_step` from `routing.json` via `next_step_for()` for the completed step (`--step`).
- Git-tail nuance (first sync → `archive`, second sync → `integrate` when `artifacts.archive` is set) lives in the script/routing, not sheep prose.
- Ad-hoc: write mode does **not** apply `default_next_step`; position fields stay byte-identical.
- Jump: write mode copies the summary `artifact` into `current-task/` at the predecessor slot when outside the worktree (**suffix must match** the predecessor `expected_artifact`); wrong suffix is an input error — no harness md→json conversion. Sets `current_step` to predecessor and `next_step` to target; Nicki then gates and runs the target sheep. Brainstorm `.md` → jump `subtasks`: [`jump_blocker.md`](jump_blocker.md).

### 2. How flexibility is spelled — **`--mode` enum**

Decided 2026-07-28.

- `check-gate.py` takes `--mode normal|adhoc|jump` (default `normal`) and **echoes the resolved mode in stdout**.
- Nicki forwards the mode to `sheep-status`; `update-status.py` applies routing's `default_next_step` only when mode is `normal`.
- One axis: ad-hoc and jump share the same flag. Do not add `--adhoc`/`--jump` booleans alongside `--override`.
- Step names stay as they are; no duplicate steps in `routing.json`.

### 3. Consent lives in routing, required every time

Decided 2026-07-28.

- Per-step `user_confirm_required: true|false`; `check-gate.py` enforces generically.
- **Amended on implementation (2026-07-29):** `gate_review` keeps its conditional check (artifact-dependent confirm). `gate_start` was deleted outright.
- Ad-hoc included — no session grants. "Sync now" from the user is itself the confirm.

### 4. Sheep hold no workflow knowledge

Decided 2026-07-28.

Sheep do one job inside a scope root. Sequence gating, position, and transitions live in Nicki and the scripts only.

**Sheep return:** `artifact`, `completed_status`, `open_questions`, `summary`. Position-free.

**Write path:** `update-status.py` takes `--step` and `--mode` from Nicki. Normal derives position from routing; adhoc leaves position untouched; jump copies the prerequisite into `current-task/` when the file suffix matches the predecessor slot (wrong suffix → input error; no md→json convert — see [`jump_blocker.md`](jump_blocker.md) for brainstorm markdown) and points at the target.

### 5. `completed_status` stays two-valued; mode carries the rest

Decided 2026-07-29.

`completed_status` reports **what the sheep did** — `complete` or `blocked`. `--mode` reports **what the write should do to position** — `normal`, `adhoc`, `jump`. They are orthogonal: an ad-hoc sync is `complete` (it did its job) *and* must not advance; a jump registers a prerequisite artifact *and* moves position so the target sheep runs next.
