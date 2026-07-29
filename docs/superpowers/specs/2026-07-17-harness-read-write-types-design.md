# Design: harness read vs write script types

**Date:** 2026-07-17  
**Status:** Decided and shipped (Jul 14); docs aligned Jul 17; **partially superseded 2026-07-29**  
**Related:** [`docs/tasks.md`](../../tasks.md) (defer #9; keep #10), session [status drift / two-script types](fe3fc594-f391-4c7f-9bf2-b18aa825e950)

> **Later changes:** `task.completed_steps` removed; write modes are
> `--mode normal|adhoc|jump`; see [`flexibility.md`](../../flexibility.md) and
> [`flexibility_next_steps.md`](../../flexibility_next_steps.md).

## Context

After Psychic Lemon status drift, a temporary `validate-sheep-return.py` sat between sheep return YAML and `update-status.py`. That “validate every step” chain was rejected: separate schema validation at every sheep handoff is unnecessary; orchestration needs **reads**, **gates**, and **writes**.

## Decision

Two harness script types only (plus gate as a specialized read/decision):

| Type | Scripts | Behavior |
|------|---------|----------|
| **Read** | `bootstrap-context.py`, `check-gate.py` | Lenient on optional fields (`.get()`). Fail only when an **obligatory** input is missing and the job cannot run (no registry entry, no `status.json`, no `next_step`). |
| **Write** | `update-status.py` | Do **not** write if required fields are missing. Success: `{"written": true, ...}`. Input error: `{"written": false, "errors": ["missing required field: …"]}` — agent retry, **not** harness failure / `sheep-fallback`. |

### Write required fields

- `worktree` (CLI)
- `next_step`

### Write optional (defaults)

- `completed_step` — when present, updates `task.current_step`, may append `completed_steps`, and may set artifact pointer; when absent, only advances `next_step` but **still always writes `task.current_step`** (preserve existing, or `"start"` on fresh init)
- `artifact` — skip pointer if absent (acceptance / fix / close may have none)
- `completed_status` → `"complete"`
- `open_questions` → `[]`
- `summary` / extra `task.*` — ignored or derived

### Explicitly not done

- **No** `validate-sheep-return.py` — deleted; folded into write required-field checks
- **No** per-step full schema validation of sheep return / artifact YAML against format docs
- Pipeline **review** readiness YAML (`validation/` skill) is unrelated — still runs inside `sheep-review`

## Target flow

```text
User ↔ Nicki (chat UX)
         ↓
    bootstrap-context.py   → position, card, relay hints
    check-gate.py          → allowed / sheep / reason  (after user confirm)
         ↓ spawn sheep
    sheep-*                → feature work → return YAML
         ↓
    update-status.py       → write status.json (or written:false + errors)
```

## Doc / backlog impact

| Item | Action |
|------|--------|
| tasks.md **#9** | **Defer** — superseded by this ADR |
| tasks.md **#10** | **Keep** — gate smoke fixture matrix (testing only) |
| `routing.yaml` / `nicki.md` / `sheep-status.md` | Already rewired (Jul 14) |
| investigation.md, PLAN.md, README | Describe reads/writes, not return validator |

## Out of scope

- Artifact body schema validators (spec/execution YAML vs format docs)
- Full orchestrator rewrite / `bin/nicki` CLI
- Changing review `validation/` readiness skill
