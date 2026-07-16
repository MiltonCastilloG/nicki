# Nicki — tasks

Actionable backlog. Completed work: [`tasks-done.md`](tasks-done.md). Analysis: [`investigation.md`](investigation.md), [`investigation-complexity.md`](investigation-complexity.md).

## Three goals (always)

Every change must respect **all three**. They are standing requirements, not pick-one options.

| Goal | Always means |
|------|----------------|
| **Correct functioning** | Pipeline runs end-to-end; worktrees, paths, handoffs work |
| **Harness and guardrails** | Gates, validators, smoke tests stay in place; scripts enforce what prose used to |
| **Trimming** | Prompt and docs stay lean; cut duplication when safe |

**When goals conflict**, higher tier wins:

1. Correct functioning  
2. Harness and guardrails  
3. Trimming  

Example: never trim `nicki.md` rules the harness does not enforce yet (trimming vs guardrails → keep prose). Never skip gate script to ship a smaller prompt (guardrails vs trimming → keep harness).

When goals **align**, do all three — e.g. add `check-gate.py` and trim duplicate prose in the same area once the script is proven.

---

## P1 — Workflow correct functioning

| # | Task | Notes |
|---|------|-------|
| 16 | **Context handling** | Prose disk-first bootstrap shipped (nicki.md + nicki-default.mdc). **Remaining:** scripted reads — see **#18**. |
| 18 | **Bootstrap script investigation** | **Next after nicki-gate-wiring.** Map how Nicki reads `global-status.json`, `status.json`, `routing.yaml`, validation/spec; design a `check-gate.py`-style sibling so orchestration context comes from script stdout. Follow-up spec: `current-task/next-steps/nicki-bootstrap-script.yaml` (nicki-gate-wiring archive). |

**Deferred suggestions (non-blocking):**

- `NICKI.md` — short section on session bootstrap vs disk bootstrap chain
- Backlog extract — handle `docs/tasks.md` rows without `` `slug` `` in column 3
- `hook-contract` — add or delete `examples/resolve-task-status.sh` reference
- Cloud agents — `sessionStart` may not fire; document desktop-first or alternate cold-start path if needed

Worktree path rule: always `worktrees/<project>-<slug>` — e.g. `worktrees/nicki-create-worktree-py`, `worktrees/tetris-clone-frp-hero-section`. Never double hyphen.

Scripts: `.cursor/skills/start-task/scripts/create-worktree.py`, `register-global-status.py`, `WORKFLOW.md` (manual recovery).

---

## P2 — Harness and guardrails

| # | Task | Notes |
|---|------|-------|
| 7 | `check-gate.py` | `.cursor/skills/nicki/scripts/check-gate.py` — `status.json` + `routing.yaml` (+ validation/spec when needed). Stdout: `allowed`, `sheep`, `reason`, `user_confirm`. All steps; git tail first. |
| 8 | Nicki **calls** gate script | Add to `nicki.md`: before spawn, run script; on fail show `reason`, do not spawn. **Keep** existing gate prose until script is proven — add, don't delete yet. **In progress:** `nicki-gate-wiring` worktree. |
| 9 | Return YAML validator | `sheep-status` path — validate `sheep_return_contract` before write. |
| 10 | Smoke fixtures | Fixture `status.json` (+ spec/validation when needed) exercised **through `check-gate.py`** — pass and fail cases. **No separate `smoke-status-v2` script** — v2 shape checks and step gates live here once #7 ships. Optional: extend `create-worktree.py` / `smoke-status-boundary.sh` for scaffold-only asserts. |
| 11 | Permissions | Allow `python …/check-gate.py` and `create-worktree.py` in `.cursor/permissions.json`. |

### `check-gate.py` (#7)

Script owns **whether** Nicki may spawn the next sheep — reads `routing.yaml`, `status.json`, validation/spec when a gate needs them. Nicki shows the transition card, user confirms, then runs the script; on `allowed: false`, show `reason` and stop.

That replaces routing prose duplicated in `nicki.md` and `status-read.md` (Gates + Readiness table). After the script is proven on a real task (P3 **#13**): delete those sections from `status-read.md` — **do not** replace with a diagram. File keeps field pointers and the JSON example only; routing stays in `routing.yaml` + the script.

**Validating status/schema changes (#10, not Nicki E2E):** After task-status.v2, do **not** use a full Nicki pipeline run to verify schema or gate field names — too slow and easy to test the wrong branch (worktrees scaffold from `main`). Use **#10 fixtures** run against `check-gate.py` instead: minimal v2 happy path, blocked `open_questions`, readiness routing, and at least one legacy-shape fail fixture (e.g. `task.story_artifact`, verbose `history`). Until #7 exists, ad-hoc local checks are fine; do not add a permanent parallel smoke script.

---

## P3 — Trimming

Only after P1–P2 run clean on a real task. See deletion map in [`investigation-complexity.md`](investigation-complexity.md).

| # | Task | Notes |
|---|------|-------|
| 12 | Trim `nicki.md` | Remove L41–51, L91–92, L105–106, L107–119, L121–135 once script is authoritative. Replace with short "run `check-gate.py`" block. |
| 13 | Trim `status-read.md` | Drop L17–30; field pointers only. |
| 14 | Shorten `NICKI.md` | Maintainer doc — duplicated transition/readiness prose. |

**Hard rule:** if trim would remove a rule the script does not enforce yet, keep the prose.

---

## Host runtime

| # | Task | Notes |
|---|------|-------|
| **20** | **Approach B: neutral-dir extract** | Move committed agents/skills/rules out of `.cursor/` into a neutral canonical tree; flip `RUNTIME_ROOT`; add Cursor-side `link_dir` install. Design: [`docs/superpowers/specs/2026-07-15-host-runtime-single-source-design.md`](superpowers/specs/2026-07-15-host-runtime-single-source-design.md). Not Approach A (Claude→`.cursor/` symlinks). |

## Defer

| Item | Why |
|------|-----|
| Disk `consented` history | Dropped in task-status.v2 — git confirm on sync/integrate only |
| `bin/nicki` CLI | PLAN.md sketch — later |
| Typed `AgentDefinition` TS | Parallel layer |
| Full orchestrator rewrite | Chat Nicki stays |

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
| [`tasks-done.md`](tasks-done.md) | Shipped P1 tasks and archives |
| [`investigation.md`](investigation.md) | Article vs Nicki; direction |
| [`investigation-complexity.md`](investigation-complexity.md) | Trimming deletion map (P3 only) |
| [`PLAN.md`](PLAN.md) | Workspace layout |
| [`complexity.md`](complexity.md) | Agent line counts |
