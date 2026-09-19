# Nicki flexibility

Shipped model (full writeups + ADR trio): [`archive/flexibility/report.md`](../archive/flexibility/report.md).

## What shipped

1. **Ad-hoc** — spawn a sheep directly (no task, no `sheep-status`). Rule: `.cursor/rules/nicki-default.mdc`.
2. **Jump** — `--mode jump` sets `next_step` only; chat is enough; no materialize. Modes are `normal` | `jump`.
3. **Consent** — Nicki chat yes before **execute** and **sync** only. Spawn gate retired — [`archive/retire-check-gate/report.md`](../archive/retire-check-gate/report.md).
4. **Dogfood** — manual ad-hoc + informal jump on a real task.
5. **Smoke CI** — `python3 test.py` via `.github/workflows/smoke.yml`.

Position is `current_step` + `next_step` + artifact pointers. Scripts own read/write (`bootstrap-context.py`, `update-status.py`).

## Optional polish (not open work)

Quoting / format hygiene for hand-authored stories — point at [`story-format.md`](../../.cursor/skills/story-maker/story-format.md). Do not start a quoting rewrite.

Do not rewrite frozen `docs/archive/**` here.
