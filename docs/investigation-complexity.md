# Complexity impact — trimming (P3 only)

Companion to [`investigation.md`](investigation.md) and [`tasks.md`](tasks.md).

**Backlog:** all three goals always apply. Priority order (functioning → harness → trimming) resolves **conflicts** only. See [`tasks.md`](tasks.md).

This doc is the **trimming** deletion map — use when functioning and harness are already met.

---

## When to use this doc

After `check-gate.py` and validators are proven on a real task. Then delete duplicated prose the harness already enforces.

---

## Trimming payoff

| Signal | Measures |
|--------|----------|
| **LLM job removed** | Fewer files to read, fewer rules to interpret |
| **Lines cut** | Smaller `nicki.md` + `status-read.md` load (Nicki ≈ 486 lines today) |

Estimated cut after full trim: **~80–120 lines** from `nicki.md`, **~15** from `status-read.md`.

---

## `nicki.md` deletion map

| Delete | Lines | LLM job removed |
|--------|------:|-----------------|
| Numbered workflow | L41–51 | Remember step sequence |
| Context load-for-gates | L91–92 | Decide what files to open for routing |
| Session bootstrap gates | L105–106 | Re-derive sync blocks from readiness |
| Readiness table | L107–115 | Map readiness → route |
| Spec / partial review gates | L117–119 | Interpret gate prose |
| Sheep map | L121–135 | Map step → `subagent_type` |

**Add (~5 lines):** show card → user yes → `check-gate.py` → spawn `sheep` from output or show `reason`.

**Hard rule:** keep any prose for rules the script does not enforce yet.

---

## Duplication source

Same logic in four places today:

- `routing.yaml` — authoritative
- `nicki.md` — copy for the model
- `status-read.md` — copy for readers
- `NICKI.md` — human doc

P3 collapses the Nicki-facing copies after P2 script reads `routing.yaml`.

---

## What leaves the LLM (after P2 + P3)

| LLM work today | After harness + trim |
|----------------|----------------------|
| Read + interpret `routing.yaml` gates | Run `check-gate.py`; read `reason` |
| Readiness table (L107–113) | Script reads validation YAML |
| Sheep map table (L121–133) | Script returns `sheep` |
| Workflow list (L41–51) | `status.json` `next_step` + script |
| Load spec/validation for routing | Script loads when needed |

**Nicki still does:** transition card, chat confirm, Gherkin `describe`, Task spawn, relay YAML.

---

## Defer (not trimming)

Disk consent, CLI, `AgentDefinition` TS — no prompt reduction; not tier 1 or 2.

**Actionable backlog:** [`tasks.md`](tasks.md).
