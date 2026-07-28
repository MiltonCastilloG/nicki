# Nicki — tasks

Actionable backlog. Completed work: [`tasks-done.md`](tasks-done.md). Analysis: [`investigation.md`](investigation.md), [`investigation-complexity.md`](investigation-complexity.md). Harness ADR: [`superpowers/specs/2026-07-17-harness-read-write-types-design.md`](superpowers/specs/2026-07-17-harness-read-write-types-design.md).

## Three goals (always)

Every change must respect **all three**. They are standing requirements, not pick-one options.

| Goal | Always means |
|------|----------------|
| **Correct functioning** | Pipeline runs end-to-end; worktrees, paths, handoffs work |
| **Harness and guardrails** | Read/write scripts + gates stay in place; smoke tests prove them; scripts enforce what prose used to |
| **Trimming** | Prompt and docs stay lean; cut duplication when safe |

**When goals conflict**, higher tier wins:

1. Correct functioning  
2. Harness and guardrails  
3. Trimming  

Example: never trim `nicki.md` rules the harness does not enforce yet (trimming vs guardrails → keep prose). Never skip gate script to ship a smaller prompt (guardrails vs trimming → keep harness).

When goals **align**, do all three — e.g. prove gate fixtures and trim duplicate prose in the same area once the script is proven.

---

## P2 — Harness and guardrails

| # | Task | Notes |
|---|------|-------|
| ~~10~~ | ~~Smoke fixtures~~ — **done 2026-07-28** | Matrix shipped: `tests/smoke/gates_matrix.py`, 45 cases through `check-gate.py` — all 13 gates allow+deny, v2 happy paths, blocked `open_questions`, readiness routing, unparseable artifacts, legacy `task.story_artifact` + `history` fail fixture, missing `status.json`, unknown step. Plus `gate_paths.py` (artifact path scope) and `routing_next_step.py` (routing owns position). See [`harness-gate-bugs.md`](harness-gate-bugs.md) follow-up 2. Optional leftover: scaffold-only asserts in `create-worktree.py`. |

**Validating status/schema changes (#10, not Nicki E2E):** Do **not** use a full Nicki pipeline run to verify schema or gate field names — too slow and easy to test the wrong branch (worktrees scaffold from `main`). Use **#10 fixtures** run against `check-gate.py` instead.

Harness shape (shipped): **read** (`bootstrap-context.py`) · **gate** (`check-gate.py`) · **write** (`update-status.py`). No per-step return validator — see design doc.

---

## P3 — Trimming

See deletion map in [`investigation-complexity.md`](investigation-complexity.md). #12 / #14 shipped — [`tasks-done.md`](tasks-done.md).

| # | Task | Notes |
|---|------|-------|
| 13 | Trim `status-read.md` | Drop remaining gate/readiness prose if any; field pointers + JSON example only. Gates/Readiness sections already removed in harness trim pass — confirm lean and close. |

**Hard rule:** if trim would remove a rule the script does not enforce yet, keep the prose.

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
