# Nicki flexibility

Date: 2026-08-05 (gate retired). Earlier gate history: [`harness-gate-bugs.md`](harness-gate-bugs.md) (historical).
Next steps / leftover backlog: [`flexibility_next_steps.md`](flexibility_next_steps.md).
Spawn gate retired: [`2026-08-05-retire-check-gate-design.md`](superpowers/specs/2026-08-05-retire-check-gate-design.md).
Ad-hoc is direct sheep invocation: [`2026-08-05-adhoc-direct-sheep-invocation-design.md`](superpowers/specs/2026-08-05-adhoc-direct-sheep-invocation-design.md).

## Goal

Nicki is no longer a strict linear march. Two capabilities shipped:

1. **Run a sheep out of band.** Any sheep, any time, with no task — the agent spawns it directly and Nicki is not involved.
2. **Jump ahead with informal input.** Set pipeline position to a target sheep; chat (and any path the user mentions) is enough — jump does not copy or materialize predecessor files. See [`2026-07-30-informal-jump-and-drop-execution-design.md`](superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md).

## Constraints

Standing. Do not trade these for convenience.

| Constraint | Means |
|---|---|
| Scripts stay authoritative for position | `update-status.py` and `bootstrap-context.py` own write/read of pipeline position. Consent is Nicki chat (execute + sync only). |
| `status.json` stays source of truth for pipeline state | Position is `current_step` + `next_step` + artifact pointers. Jump moves position deliberately; ad-hoc runs write nothing. |
| Modes own write shape | `--mode jump` changes how `update-status.py` moves position. No spawn-gate script. |
| Ad-hoc never touches pipeline state | No bootstrap, no `sheep-status`, no `side_effects` — a directly-invoked sheep only returns JSON. |

## Write modes

`update-status.py` takes `--mode normal|jump` (default `normal`). Nicki forwards the mode to `sheep-status`. Both modes need a task; `--mode adhoc` no longer exists.

| Mode | Write | Position after write |
|---|---|---|
| **normal** | Sets `current_step` from `--step`; derives `next_step` from routing via `next_step_for()` | Advances along the pipeline |
| **jump** | Sets `next_step` to the target; leaves `current_step` untouched; no summary `artifact` required; appends `side_effects` with `artifact: null`; cannot target `start`, `close`, or `done` | Points at target sheep — Nicki runs it next |

**Sheep return contract:** sheep return `artifact`, `completed_status`, `open_questions`, `summary` only — not `next_step` or `completed_step`. Execute **omits** `artifact` (no `executions/*.json`). Nicki forwards the return plus the `--step` and `--mode` she dispatched.

## Position model

`task.completed_steps` is **removed**. Position is `current_step`, `next_step`, and artifact pointers only. Legacy files still carrying `completed_steps` have it stripped on the next write.

**Bootstrap stdout** (`bootstrap-context.py`): `active_task`, `status_path`, `current_step`, `next_step`, `sheep` — no `completed_steps`, no `readiness`.

## Capability A — ad-hoc: invoke a sheep directly

### Behavior

Ad-hoc is not a Nicki mode. The agent Task-spawns one sheep with instructions, relays its return JSON in chat, and stops. No task, worktree, `status.json`, bootstrap, or `sheep-status`. Rule: `.cursor/rules/nicki-default.mdc`.

| Layer | Behavior |
|---|---|
| Agent | Picks the sheep; packs instructions plus an output path for document sheep (user's path, else under `docs/adhoc/`); asks yes before git sheep |
| Sheep | Same file as on the pipeline — one skill, path from the prompt, position-free return |
| Write | None. Pipeline state is untouched because nothing writes it |

**Nicki-only sheep:** `sheep-start`, `sheep-close`, `sheep-status` own the registry and per-task status; they are never invoked ad-hoc.

### Side-effect trail

`task.side_effects[]` is append-only — one entry per jump write, with `step`, `mode`, UTC `at`, and `artifact` (may be null). Documented in `status-format.md`. Entries with `"mode": "adhoc"` exist in files written before 2026-08-05.

Archive `process` is handoff rows plus one row per side-effect entry (including null artifacts) — see `archive-format.md`.

### Acceptance checks

- A sheep spawned with instructions alone, in a repo with no registered task, runs and returns.
- `--mode adhoc` is rejected by `update-status.py`; no `adhoc` in `MODES`.
- Document sheep invoked ad-hoc with no path given write under `docs/adhoc/`.
- Jump/write still rejects targeting `start` / `close` / `done` on jump mode.
- Acceptance before first sync is Nicki’s chat confirm (ask before sync).
- Archive format contract asserts `side_effects` → `process` (including null artifact rows).

## Capability B — informal jump (position-only)

### Behavior

Jump ahead sets `next_step` to a target sheep and leaves `current_step` untouched. No predecessor artifact on the jump write — chat is enough; a document path in chat is optional context for the sheep, not a harness payload.

Typical flow (Nicki):

1. User asks to skip ahead (chat / optional path / diff context). If unclear which target, ask once.
2. Write with `--mode jump --step <target>` — position only; no summary `artifact`; no copy into `current-task/`; no suffix match. Logs `side_effects` with `artifact: null`.
3. Spawn that step's sheep with chat as primary input (ask yes first if target is `execute` or `sync`). On-disk `current-task/` files are optional when present. After return, `sheep-status` with `--mode normal --step <target>` as usual (execute omits `artifact`).

No “ensure X exists” / convert prelude before jump. `start`, `close`, and `done` are not jump targets (`update-status` denies). A sync outside the pipeline is a directly-invoked `sheep-sync`, not a jump.

### Resolved items

| Item | Status |
|---|---|
| **B1 — path scope** | Done (corrected 2026-07-31). All artifact pointers including `archive` resolve against the worktree (project repo). |
| **B2 — jump without claiming a step** | Done. `--mode jump` is position-only: `next_step` = target, `current_step` untouched; no materialize. |
| **B3 — brainstorm / informal input** | Done via informal jump. |
| **B4 — materialize into worktree for archive** | Done 2026-07-29; **removed** 2026-07-30 by informal jump. |
| **B5 — status vocabulary** | Done. Skip-ahead is `--mode jump`; `completed_status` stays `complete`/`blocked` only. |
| **B6 — drop execution artifact** | Done. Execute omits `artifact`; review never requires or loads `executions/*.json`. |

### Acceptance checks

- Jump to `subtasks` (or `spec` / `execute` / `review`) with only chat: `next_step` is the target, `current_step` byte-identical, no file copied into `current-task/`, side effect logged with `artifact: null`.
- Jump to `start` / `close` / `done`: **denied** by `update-status`.
- Jump write succeeds with no summary `artifact`.
- Fixture per case in `test.py`.

## Sequencing

Sequenced flexibility through informal jump, drop-sequence / override, and retire-check-gate is done.

| Order | Work | Status |
|---|---|---|
| 1–12 | Ad-hoc write mode, jump, drop sequence/`--override`, etc. | **Done** (see earlier rows in git history / designs) |
| 13 | Retire `check-gate.py`; chat consent execute+sync only | **Done** 2026-08-05 |
| 14 | Ad-hoc becomes direct sheep invocation; `--mode adhoc` removed | **Done** 2026-08-05 |

## Decisions

### 1. Who owns `next_step` — **routing**

- Sheep return handoff only: artifact, `completed_status`, blockers — **not** `next_step` or `completed_step`.
- On normal completion, `update-status.py` sets `task.next_step` from `routing.json` via `next_step_for()` for the completed step (`--step`).
- Git-tail nuance (first sync → `archive`, second sync → `integrate` when `artifacts.archive` is set) lives in the script/routing, not sheep prose.
- Jump: write mode sets `next_step` to the target and leaves `current_step` untouched; Nicki then runs the target sheep.
- Ad-hoc writes nothing, so routing never applies to it.

### 2. How flexibility is spelled — **`--mode` enum**

- Nicki forwards `--mode` to `sheep-status`; `update-status.py` applies routing's `default_next_step` only when mode is `normal`.
- **Amended 2026-07-31:** drop `--override` and the sequence-waiver class.
- **Amended 2026-08-05:** spawn-gate script removed; modes are write-only.
- **Amended 2026-08-05:** `adhoc` removed from the enum — ad-hoc is a directly-invoked sheep, not a write. Modes are `normal` and `jump`.

### 3. Consent — **Nicki chat**

- Explicit yes required only before **execute** and **sync**.
- Ad-hoc git sheep (`sheep-sync`, `sheep-integrate`) need the same explicit yes from the agent that spawns them.
- No `user_confirm_required` / spawn-gate script.

### 4. Sheep hold no workflow knowledge

Sheep do one job inside a scope root. Sequence, position, and transitions live in Nicki and the read/write scripts only.

### 5. `completed_status` stays two-valued; mode carries the rest

`completed_status` reports **what the sheep did** — `complete` or `blocked`. `--mode` reports **what the write should do to position**.

### 6. No sequence class; no `--override`; no spawn gate

Drop-sequence done 2026-07-31. Retire-check-gate done 2026-08-05.
