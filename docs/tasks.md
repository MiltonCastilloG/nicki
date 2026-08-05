# Nicki — tasks

Actionable backlog. Completed work: [`tasks-done.md`](tasks-done.md). Analysis: [`investigation.md`](investigation.md), [`investigation-complexity.md`](investigation-complexity.md). Harness ADR: [`superpowers/specs/2026-07-17-harness-read-write-types-design.md`](superpowers/specs/2026-07-17-harness-read-write-types-design.md).

## Three goals (always)

Every change must respect **all three**. They are standing requirements, not pick-one options.

| Goal | Always means |
|------|----------------|
| **Correct functioning** | Pipeline runs end-to-end; worktrees, paths, handoffs work |
| **Harness and guardrails** | Read/write scripts + smoke tests stay in place; scripts enforce position; chat consent for execute/sync |
| **Trimming** | Prompt and docs stay lean; cut duplication when safe |

**When goals conflict**, higher tier wins:

1. Correct functioning  
2. Harness and guardrails  
3. Trimming  

Example: never trim `nicki.md` consent rules that scripts do not enforce (trimming vs guardrails → keep prose).

When goals **align**, do all three — e.g. prove smoke fixtures and trim duplicate prose in the same area once the script is proven.

---

## P2 — Harness and guardrails

| # | Task | Notes |
|---|------|-------|
| ~~10~~ | ~~Smoke fixtures~~ — **done** | Live suite: `python3 test.py` (bootstrap, status write, routing_next_step, jump, harness_failure, …). Gate matrix retired with check-gate 2026-08-05 — see [`archive/retire-check-gate/`](archive/retire-check-gate/). |

**Validating status/schema changes:** Prefer smoke fixtures via `python3 test.py` — not a full Nicki pipeline E2E (worktrees scaffold from `main` and drift easily).

Harness shape (shipped): **read** (`bootstrap-context.py`) · **write** (`update-status.py`). Consent is Nicki chat (execute + sync). No per-step return validator — see [retire-check-gate design](superpowers/specs/2026-08-05-retire-check-gate-design.md).

---

## P3 — Trimming

See deletion map in [`investigation-complexity.md`](investigation-complexity.md). #12 / #14 shipped — [`tasks-done.md`](tasks-done.md).

| # | Task | Notes |
|---|------|-------|
| 13 | Trim `status-read.md` | Drop remaining gate/readiness prose if any; field pointers + JSON example only. |

**Hard rule:** if trim would remove a consent rule Nicki still needs in chat, keep the prose.

---

## Host runtime

| # | Task | Notes |
|---|------|-------|
| **20** | **Approach B: neutral-dir extract** | Move committed agents/skills/rules out of `.cursor/` into `nicki-workflow/`; flip `RUNTIME_ROOT`; add Cursor-side `link_dir` install. Checklist: [`host-runtime-backlog-and-approach-b.md`](host-runtime-backlog-and-approach-b.md). Design: [`superpowers/specs/2026-07-15-host-runtime-single-source-design.md`](superpowers/specs/2026-07-15-host-runtime-single-source-design.md). |

---

## Defer

| Item | Why |
|------|-----|
| **#9** `validate-sheep-return.py` | Superseded: per-step return validator deleted; required-field checks live in `update-status.py` write path only. See [harness read/write design](superpowers/specs/2026-07-17-harness-read-write-types-design.md). |
| Disk `consented` history | Dropped in task-status.v2 — git confirm on sync/integrate only |
| `bin/nicki` CLI | PLAN.md sketch — later |
| Typed `AgentDefinition` TS | Parallel layer |
| Full orchestrator rewrite | Chat Nicki stays |

**Deferred suggestions (non-blocking):**

- Backlog extract — handle `docs/tasks.md` rows without `` `slug` `` in column 3
- `hook-contract` — add or delete `examples/resolve-task-status.sh` reference
- Cloud agents — `sessionStart` may not fire; document desktop-first or alternate cold-start path if needed

---

## PLAN.md — multi-project workspace (later)

| # | Task |
|---|------|
| P1 | Finalize `nicki-workspace.yaml` schema |
| P2 | Minimal CLI — `workspace init`, `project clone`, `runtime install`, `doctor` |
| P3 | Dogfood across managed projects |
| **17** | **AWS deployment exploration** | All managed projects will deploy on AWS; **how** is TBD. One candidate to explore (not chosen): [Bedrock AgentCore MCP](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/mcp-getting-started.html) / AgentCore Runtime — whether it fits Nicki workflow, app hosting, or something else. Document findings and options; no fixed playbook yet. Tetris **#12** may dogfood once an approach looks worth trying. |

May merge with completed P1 worktree tasks — see [`tasks-done.md`](tasks-done.md). Update PLAN when root `worktrees/` ships.

---

## References

| Doc | Role |
|-----|------|
| [`tasks-done.md`](tasks-done.md) | Shipped tasks and archives |
| [`host-runtime-backlog-and-approach-b.md`](host-runtime-backlog-and-approach-b.md) | Approach B checklist (#20) |
| [`superpowers/specs/2026-07-17-harness-read-write-types-design.md`](superpowers/specs/2026-07-17-harness-read-write-types-design.md) | Read vs write harness ADR |
| [`investigation.md`](investigation.md) | Article vs Nicki; direction |
| [`investigation-complexity.md`](investigation-complexity.md) | Trimming deletion map (P3 only) |
| [`PLAN.md`](PLAN.md) | Workspace layout |
| [`complexity.md`](complexity.md) | Agent line counts |
