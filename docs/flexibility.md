# Nicki flexibility

Date: 2026-07-31. Gate history: [`harness-gate-bugs.md`](harness-gate-bugs.md).
Next steps / leftover backlog: [`flexibility_next_steps.md`](flexibility_next_steps.md).
Pending: none for sequenced flexibility — see [`flexibility_next_steps.md`](flexibility_next_steps.md) for hygiene backlog.

## Goal

Nicki is no longer a strict linear march. Two capabilities shipped:

1. **Run a step out of band.** Sync mid-`execute`, without acceptance, without moving workflow position.
2. **Jump ahead with informal input.** Set pipeline position to a target sheep; chat (and any path the user mentions) is enough — jump does not copy or materialize predecessor files. See [`2026-07-30-informal-jump-and-drop-execution-design.md`](superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md).

## Constraints

Standing. Do not trade these for convenience.

| Constraint | Means |
|---|---|
| Scripts stay authoritative | `check-gate.py`, `update-status.py`, `bootstrap-context.py` keep the veto. No decision moves back into prose. |
| `status.json` stays source of truth for pipeline state | Position is `current_step` + `next_step` + artifact pointers. Ad-hoc runs log to `side_effects` without moving position; jump moves position deliberately. |
| Gate denials never waive | Consent, readiness blocks, missing inputs, and every other gate deny are final. No `--override`. No `deny_sequence` / sequence class. See [`2026-07-31-drop-sequence-and-override-design.md`](superpowers/specs/2026-07-31-drop-sequence-and-override-design.md). |
| Modes own write shape, not waivers | `--mode adhoc` / `--mode jump` change how `update-status.py` moves position. They are not flags to bypass the gate. |

## Write modes

Both `check-gate.py` and `update-status.py` take `--mode normal|adhoc|jump` (default `normal`). The gate echoes the resolved mode in stdout; Nicki forwards the same mode to `sheep-status`.

| Mode | Gate | Write | Position after write |
|---|---|---|---|
| **normal** | Safety + consent (+ policy bookends) | Sets `current_step` from `--step`; derives `next_step` from routing via `next_step_for()` | Advances along the pipeline |
| **adhoc** | Same denials as normal; step must be `adhoc_allowed` | Records artifact pointer; appends `task.side_effects[]`; leaves `current_step` and `next_step` untouched | Unchanged |
| **jump** | Same denials as normal; cannot target `start`, `close`, or `done` | Sets `next_step` to the target; leaves `current_step` untouched; no summary `artifact` required; appends `side_effects` with `artifact: null` | Points at target sheep — Nicki gates and runs it next |

**Ad-hoc policy:** every step sets `adhoc_allowed` in `routing.json` except `start`, `close`, and `done`.

**Sheep return contract:** sheep return `artifact`, `completed_status`, `open_questions`, `summary` only — not `next_step` or `completed_step`. Execute **omits** `artifact` (no `executions/*.json`). Nicki forwards the return plus the `--step` and `--mode` she dispatched.

## Position model

`task.completed_steps` is **removed**. Position is `current_step`, `next_step`, and artifact pointers only. Legacy files still carrying `completed_steps` have it stripped on the next write.

**Bootstrap stdout** (`bootstrap-context.py`): `active_task`, `status_path`, `current_step`, `next_step`, `readiness`, `sheep` — no `completed_steps`.

## Capability A — out-of-band steps

### Behavior

An ad-hoc invocation is gated for safety, runs the sheep, and leaves `current_step` and `next_step` byte-identical.

| Layer | Behavior |
|---|---|
| Gate | `check-gate.py --mode adhoc --step <requested>`; step must be `adhoc_allowed`; denials never waived |
| Sheep | Position-free return; no workflow knowledge in sheep files |
| Write | `update-status.py --mode adhoc`: artifact pointer recorded, one `task.side_effects` entry appended, position untouched |

### Side-effect trail

`task.side_effects[]` is append-only — one entry per ad-hoc or jump write, with `step`, `mode`, UTC `at`, and `artifact` (may be null). Documented in `status-format.md`.

Archive `process` is handoff rows plus one row per side-effect entry (including null artifacts) — see `archive-format.md`.

### Acceptance checks

- Ad-hoc sync during `execute`: gate allows, sheep runs, `current_step`/`next_step` byte-identical before and after.
- Artifact pointer for the ad-hoc sync is recorded; side effect appears in the log and in the archive report (`process` row).
- Ad-hoc `start` / `close` / `done`: **denied** — not `adhoc_allowed`.
- Ad-hoc on other steps (including `integrate`): **allowed** when safety inputs and consent hold.
- Acceptance before first sync is Nicki’s chat confirm only — the sync gate does not require `current_step == acceptance` (pending drop-sequence design).
- Fixture per case, through `check-gate.py`, in `test.py`.
- Archive format contract asserts `side_effects` → `process` (including null artifact rows).

## Capability B — informal jump (position-only)

### Behavior

Jump ahead sets `next_step` to a target sheep and leaves `current_step` untouched. No predecessor artifact on the jump write — chat is enough; a document path in chat is optional context for the sheep, not a harness payload.

Typical flow (Nicki):

1. User asks to skip ahead (chat / optional path / diff context). If unclear which target, ask once.
2. Write with `--mode jump --step <target>` — position only; no summary `artifact`; no copy into `current-task/`; no suffix match. Logs `side_effects` with `artifact: null`.
3. Gate the **target** with `--step <target>` (denials never waived; mode is for write forwarding).
4. Spawn that step's sheep with chat as primary input. On-disk `current-task/` files are optional when present. After return, `sheep-status` with `--mode normal --step <target>` as usual (execute omits `artifact`).

No “ensure X exists” / convert prelude before jump. Sync remains **adhoc**, not jump. `start`, `close`, and `done` are not jump targets.

### Resolved items

| Item | Status |
|---|---|
| **B1 — path scope** | Done (corrected 2026-07-31). All artifact pointers including `archive` resolve against the worktree (project repo). Earlier workspace-root archive scope was a Nicki-only mistake. |
| **B2 — jump without claiming a step** | Done (superseded shape). `--mode jump` is position-only: `next_step` = target, `current_step` untouched; no materialize. |
| **B3 — brainstorm / informal input** | Done via informal jump. Chat (or a design `.md` path in chat) jumps to `subtasks` / `spec` / etc.; harness does not convert. Sheep accept whatever Nicki passes. Was blocked under materialize — see [`jump_blocker.md`](jump_blocker.md) (resolved). |
| **B4 — materialize into worktree for archive** | Done 2026-07-29; **removed** 2026-07-30 by informal jump. Jump no longer copies or suffix-matches. Artifacts under `current-task/` still come from normal sheep writes when produced. |
| **B5 — status vocabulary** | Done. Skip-ahead is `--mode jump`; `completed_status` stays `complete`/`blocked` only. |
| **B6 — drop execution artifact** | Done. Execute omits `artifact`; review never requires or loads `executions/*.json`. |

### Acceptance checks

- Jump to `subtasks` (or `spec` / `execute` / `review`) with only chat: `next_step` is the target, `current_step` byte-identical, no file copied into `current-task/`, side effect logged with `artifact: null`.
- Jump to `start` / `close` / `done`: **denied**.
- Jump write succeeds with no summary `artifact` (no “artifact not found” / wrong-suffix failure).
- Fixture per case in `test.py`.

## Sequencing

Sequenced flexibility through informal jump and drop-sequence / override is done.

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
| 10 | B4: materialize prior artifact into `current-task/` on jump | **Done** 2026-07-29; **removed** 2026-07-30 (informal jump) |
| 11 | Informal jump + drop execution artifact | **Done** 2026-07-30 |
| 12 | Drop `deny_sequence` + `--override` | **Done** 2026-07-31 |

## Decisions

### 1. Who owns `next_step` — **routing**

Decided 2026-07-28.

- Sheep return handoff only: artifact, `completed_status`, blockers — **not** `next_step` or `completed_step`.
- On normal completion, `update-status.py` sets `task.next_step` from `routing.json` via `next_step_for()` for the completed step (`--step`).
- Git-tail nuance (first sync → `archive`, second sync → `integrate` when `artifacts.archive` is set) lives in the script/routing, not sheep prose.
- Ad-hoc: write mode does **not** apply `default_next_step`; position fields stay byte-identical.
- Jump: write mode sets `next_step` to the target and leaves `current_step` untouched; no summary `artifact`, no copy into `current-task/`, no suffix match. Nicki then gates and runs the target sheep with chat as primary input. Former materialize blocker: [`jump_blocker.md`](jump_blocker.md) (resolved).

### 2. How flexibility is spelled — **`--mode` enum**

Decided 2026-07-28.

- `check-gate.py` takes `--mode normal|adhoc|jump` (default `normal`) and **echoes the resolved mode in stdout**.
- Nicki forwards the mode to `sheep-status`; `update-status.py` applies routing's `default_next_step` only when mode is `normal`.
- One axis: ad-hoc and jump share the same `--mode` flag. Do not add `--adhoc`/`--jump` booleans.
- **Amended 2026-07-31:** drop `--override` and the sequence-waiver class entirely — modes are write semantics only. Design: [`2026-07-31-drop-sequence-and-override-design.md`](superpowers/specs/2026-07-31-drop-sequence-and-override-design.md).
- Step names stay as they are; no duplicate steps in `routing.json`.

### 3. Consent lives in routing, required every time

Decided 2026-07-28.

- Per-step `user_confirm_required: true|false`; `check-gate.py` enforces generically.
- **Amended on implementation (2026-07-29):** `gate_review` keeps its conditional check (artifact-dependent confirm). `gate_start` was deleted outright.
- **Amended 2026-07-30:** `start` omits `user_confirm_required` — the user's start request is the confirm (hard-gating it double-asked with the transition card).
- Ad-hoc included — no session grants. "Sync now" from the user is itself the confirm.
- **Amended 2026-07-31:** acceptance before first sync is chat ask/confirm only — not a sync gate condition.

### 4. Sheep hold no workflow knowledge

Decided 2026-07-28.

Sheep do one job inside a scope root. Sequence gating, position, and transitions live in Nicki and the scripts only.

**Sheep return:** `artifact`, `completed_status`, `open_questions`, `summary`. Position-free.

**Write path:** `update-status.py` takes `--step` and `--mode` from Nicki. Normal derives position from routing; adhoc leaves position untouched; jump sets `next_step` to the target only (`current_step` unchanged; no materialize).

### 5. `completed_status` stays two-valued; mode carries the rest

Decided 2026-07-29.

`completed_status` reports **what the sheep did** — `complete` or `blocked`. `--mode` reports **what the write should do to position** — `normal`, `adhoc`, `jump`. They are orthogonal: an ad-hoc sync is `complete` (it did its job) *and* must not advance; a jump sets `next_step` to the target *and* leaves `current_step` untouched so Nicki can gate and run that sheep next.

### 6. No sequence class; no `--override`

Done 2026-07-31. Spec: [`2026-07-31-drop-sequence-and-override-design.md`](superpowers/specs/2026-07-31-drop-sequence-and-override-design.md).

- Removed `deny_sequence` / `SEQUENCE` and the only two call sites (sync acceptance ordering; done-before-close).
- Removed `--override`. Gate denials are never waived.
- Adhoc and jump remain for write position behavior and policy bookends (`adhoc_allowed`, jump non-targets).
- Why override died: it duplicated sequence waiver without write semantics, and historically kept broken gates alive.
