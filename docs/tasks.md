# Nicki — tasks

Actionable backlog. Analysis: [`investigation.md`](investigation.md), [`investigation-complexity.md`](investigation-complexity.md).

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
| 1 | `create-worktree.py` | Pull base branch, `git worktree add`, workspace `worktrees/<slug>` (or `<project>--<slug>`), copy gitignored locals (`.env`, `.env.*`), `post_create` from registry, register `global-status.json`. |
| 2 | Root `worktrees/` layout | Workspace-level `worktrees/` vs `projects/*/worktrees/`. Update paths in formats, `sheep-start`, `start-task`, `close-scope`. |
| 3 | `post_create` copy list | Per-project files to copy after checkout. Document in workspace registry. |
| 4 | Migrate active task | Recreate or move `tetris-clone-frp` worktree; fix `global-status.json`. |
| 5 | Wire `sheep-start` to new script | Replace/extend `start-worktrees.sh` call path; keep register flow. |
| 6 | **Gherkin + spec mutual understanding** | See below — blocks bad downstream work. |

### Gherkin + spec mutual understanding (#6)

**Goal:** Nicki and sheep do not advance past `describe` / `spec` until user and agent share the same understanding — not just formatted output.

| Step | Who | Behavior |
|------|-----|----------|
| `describe` | **Nicki** | Draft Gherkin; **ask** on ambiguity (scope, actors, acceptance). Revise until user **explicitly approves** story meaning. No `story.md` on first draft alone. |
| `spec` | **sheep-spec** | Read approved story; **ask** (via `open_questions` + blocked return) when requirements fork or stay vague. No spec file until resolved or user confirms trade-offs. |
| Gate | **Harness** | `routing.yaml` / `check-gate.py`: block `spec` without `story_artifact`; block `subtasks` while spec `open_questions` non-empty. |

**Touch:** `nicki.md` (Describe), `sheep-spec.md`, `spec-maker/SKILL.md`, optional `story-format.md` / spec gate smoke.

**Today:** one-shot approval on describe; spec-maker asks internally but sheep may write spec with lingering `open_questions` — tighten loop so Nicki relays questions to user until clear.

Projects on disk: `castlemill-landing`, `tetris-clone-frp` (one active worktree). Gitignored env is copied by script — not a layout problem.

---

## P2 — Harness and guardrails

| # | Task | Notes |
|---|------|-------|
| 7 | `check-gate.py` | `.cursor/skills/nicki/scripts/check-gate.py` — `status.json` + `routing.yaml` (+ validation/spec when needed). Stdout: `allowed`, `sheep`, `reason`, `user_confirm`. All steps; git tail first. |
| 8 | Nicki **calls** gate script | Add to `nicki.md`: before spawn, run script; on fail show `reason`, do not spawn. **Keep** existing gate prose until script is proven — add, don't delete yet. |
| 9 | Return YAML validator | `sheep-status` path — validate `sheep_return_contract` before write. |
| 10 | Smoke fixtures | Gate pass/fail on fixture `status.json`. Worktree script smoke if applicable. |
| 11 | Permissions | Allow `python …/check-gate.py` and `create-worktree.py` in `.cursor/permissions.json`. |

### `check-gate.py` (#7)

Script owns **whether** Nicki may spawn the next sheep — reads `routing.yaml`, `status.json`, validation/spec when a gate needs them. Nicki shows the transition card, user confirms, then runs the script; on `allowed: false`, show `reason` and stop.

That replaces routing prose duplicated in `nicki.md` and `status-read.md` (Gates + Readiness table). After the script is proven on a real task (P3 **#13**): delete those sections from `status-read.md` — **do not** replace with a diagram. File keeps field pointers and the JSON example only; routing stays in `routing.yaml` + the script.

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

## Defer

| Item | Why |
|------|-----|
| Disk `consented` history | Not needed for functioning or guardrails |
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

May merge with **#1–2** above. Update PLAN when root `worktrees/` ships.

---

## References

| Doc | Role |
|-----|------|
| [`investigation.md`](investigation.md) | Article vs Nicki; direction |
| [`investigation-complexity.md`](investigation-complexity.md) | Trimming deletion map (P3 only) |
| [`PLAN.md`](PLAN.md) | Workspace layout |
| [`complexity.md`](complexity.md) | Agent line counts |
