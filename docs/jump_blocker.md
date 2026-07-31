# Jump blocker — prerequisite format mismatch

Date: 2026-07-29. Related: [`flexibility.md`](flexibility.md) Capability B.
**Status: resolved** by [`superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md`](superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md) (implemented in harness / `.cursor`).

## Real-use case (historical)

User has a design doc from `brainstorm` (markdown under `docs/superpowers/specs/…`) and wants to **jump to `subtasks`**.

Previously:

1. Jump required the **predecessor** artifact to already match routing’s expected suffix.
2. Predecessor of `subtasks` is `spec` → expected `current-task/specs/<slug>.json`.
3. Brainstorm output is `.md`.
4. Harness **rejected** the jump (`jump artifact must be .json …`) — no markdown→JSON conversion.

So the user could not “bring my brainstorm and skip to checklist” without first producing a schema-shaped JSON spec.

## Resolution

Informal jump is **position-only**: set `next_step` to the target; leave `current_step` untouched; no summary artifact, no copy into `current-task/`, no suffix match on jump.

Chat (and any path the user mentions) is enough. Nicki jumps, gates the target, and spawns the sheep with that chat. Sheep **accept whatever** Nicki passes; on-disk predecessor files are optional context when present. The harness does **not** convert markdown→JSON.

## Why YAGNI left the old path (historical)

| Approach | Cost | Status |
|---|---|---|
| Convert md→JSON in harness | Changes how “spec” is defined; shape/open_questions rules; tests | Still non-goal — harness does not convert |
| Accept `.md` as `artifacts.spec` | Broke then-gates / `load_artifact` | Superseded — jump no longer materializes |
| Require correct suffix + copy into `current-task/` | Small; archive-safe when format matches | Shipped 2026-07-29; **removed** by informal jump |

## Acceptance (met)

- Jump to `subtasks` (or `spec` / `execute` / `review`) with only chat succeeds end-to-end (gate allows, sheep runs).
- Jump write never fails for “wrong suffix” or “artifact not found.”
- `current_step` before and after a jump write is identical; `next_step` equals the target.
