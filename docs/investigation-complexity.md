# Complexity impact — trimming (P3 only)

Companion to [`investigation.md`](investigation.md) and [`tasks.md`](tasks.md).

**Backlog:** all three goals always apply. Priority order (functioning → harness → trimming) resolves **conflicts** only. See [`tasks.md`](tasks.md).

This doc is the **trimming** deletion map — use when functioning and harness are already met.

---

## When to use this doc

After read/write smoke fixtures are green on a real task. Then delete duplicated prose the harness already covers. Spawn gate is retired — consent for execute/sync stays in `nicki.md`. See [retire-check-gate](superpowers/specs/2026-08-05-retire-check-gate-design.md).

---

## Trimming payoff

| Signal | Measures |
|--------|----------|
| **LLM job removed** | Fewer files to read, fewer rules to interpret |
| **Lines cut** | Smaller `nicki.md` + `status-read.md` load |

Much of the original deletion map (readiness table, sheep map, gate prose) already shipped. Remaining trim is residual duplication only.

---

## What leaves the LLM (current)

| LLM work historically | After harness + trim |
|----------------|----------------------|
| Interpret routing gates | Gone — no spawn gate; sheep from bootstrap |
| Readiness table | Gone — Nicki sets `next_step` after review |
| Sheep map table | Bootstrap / `routing.json` returns `sheep` |
| Workflow list | `status.json` `next_step` + bootstrap |

**Nicki still does:** transition card, chat confirm (execute + sync), Task spawn, relay sheep returns to sheep-status.

---

## Hard rule

Keep consent prose for execute/sync — scripts do not enforce it.
