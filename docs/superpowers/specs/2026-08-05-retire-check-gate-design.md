# Design: Retire check-gate (chat consent only)

Date: 2026-08-05  
Status: **implemented**  
Slug: `retire-check-gate`  
Related: [`2026-07-31-drop-sequence-and-override-design.md`](2026-07-31-drop-sequence-and-override-design.md), [`2026-08-01-artifact-ownership-and-position-design.md`](2026-08-01-artifact-ownership-and-position-design.md)

## Problem

`check-gate.py` no longer enforces meaningful progress. Remaining checks are thin document/consent bookends that duplicate Nicki chat. Hard product stops the user cares about — **before execute** and **before sync** — are user confirmation, not artifact re-derivation. Consent was split across prose and `user_confirm_required`, so there was no single source of truth.

## Goal

- **Delete** the spawn-time gate harness (`check-gate.py`, `gates.py`, gate-only smokes and wiring).
- **One consent SoT:** Nicki chat. Explicit yes only before `execute` and before `sync`.
- **Harness** is read + write only: `bootstrap-context.py` → spawn → `update-status.py`.
- Rename/thin former `gate_utils` to bootstrap-only helpers; move writer routing helpers under `current-task-update`.
- Archive this task with `docs/archive/retire-check-gate/report.md` recording the removal commit id (no full Nicki pipeline).

## Decision summary

| Topic | Decision |
|---|---|
| Spawn veto script | **Remove** — Nicki never calls `check-gate.py` |
| Consent | Nicki chat only; hard confirms: **execute**, **sync** |
| Other steps | No explicit approval required to spawn |
| Adhoc / jump | Still `--mode` on `update-status` only; never invoke a gate |
| `adhoc_allowed` / `user_confirm_*` / per-step `gate` strings / `gate_policy` | **Remove** from `routing.json` |
| Open questions | Sheep + status; no script re-check before spawn |
| `gate_utils.py` | Rename (e.g. `bootstrap_utils.py`); keep only bootstrap needs |
| Writer helpers (`next_step_for`, `MODES`, routing load) | Live under `current-task-update` |
| Jump bookends (`start`/`close`/`done`) | Remain in `update-status.py` |
| Archive | Manual `report.md` with commit id after implementation commit |

## Architecture

```text
status.json
  → bootstrap-context.py  (position + sheep)
  → Nicki card; ask yes only if next is execute or sync
  → spawn sheep from routing/bootstrap
  → sheep-status → update-status.py
```

## Delete set

- `.cursor/skills/nicki/scripts/check-gate.py`
- `.cursor/skills/nicki/scripts/gates.py`
- `tests/smoke/gates_matrix.py`, `tests/smoke/gate_paths.py` (and `test.py` registrations)
- Permissions / harness_failure / Nicki agent references to check-gate
- Routing: `gate`, `user_confirm`, `user_confirm_required`, `adhoc_allowed`, `gate_policy`, `status_update.skip_user_confirm`

## Keep / move

| Piece | Action |
|---|---|
| `workspace_root`, `resolve_worktree`, `load_status`, `load_routing` | `bootstrap_utils.py` (bootstrap + `validate-harness-stdout`) |
| `next_step_for`, `MODES` | `current-task-update` helper (e.g. `routing_write.py` beside `update-status.py`) |
| Artifact/deny/allow helpers | Delete with gates |

## Nicki prose

- Shell allowlist: `bootstrap-context.py` only.
- Position = bootstrap `next_step`; sheep name from bootstrap/routing.
- Transitions: show card; **ask yes only for execute and sync**; then spawn (no gate).
- Adhoc/jump: forward `--mode` to sheep-status; jump not for `start`/`close`/`done` (writer enforces).

## Tests

- Drop gate matrix/path smokes.
- `routing_next_step`: keep resolver cases against the moved `next_step_for`; drop gate-echo cases.
- `harness_failure`: drive contract validation via remaining harness scripts (bootstrap / update-status), not check-gate.
- `errors_append`: use a non-gate script route example.
- `python3 test.py` green.

## Docs

- Update `.cursor/agents/nicki.md` (authoritative agent).
- Light touch on live harness mentions in `docs/NICKI.md` / `docs/flexibility.md` where they claim gate veto — enough that the live story matches.
- Do not rewrite frozen `docs/archive/**` historical stories.

## Non-goals

- Changing adhoc/jump **write** semantics.
- Reintroducing readiness or sequence denials.
- Renaming `gate_utils` consumers outside the nicki/current-task-update scripts beyond this split.
- Running the full Nicki archive sheep for this task.

## Acceptance

- No `check-gate.py` / `gates.py` in the tree.
- Nicki does not invoke a gate; consent is execute + sync chat only.
- Bootstrap utils module has no deny/allow/artifact gate API.
- Writer still derives `next_step` from routing (including archive branch).
- `docs/archive/retire-check-gate/report.md` cites the implementation commit.
- `python3 test.py` passes.
