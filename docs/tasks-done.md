# Nicki — completed tasks

Shipped work moved out of [`tasks.md`](tasks.md) to keep the backlog lean. Task archives: [`archive/`](archive/).

---

## P1 — Workflow correct functioning (done)

| # | Task | Notes |
|---|------|-------|
| 1 | `create-worktree.py` | Pull base branch, `git worktree add`, workspace `worktrees/<project>-<slug>`, copy gitignored locals from registry, `post_create`, scaffold `current-task/`, register `global-status.json`. Archive: [`archive/nicki/04/`](archive/nicki/04/). |
| 2 | Root `worktrees/` layout | Shipped with #1. **Unified:** `worktrees/<project>-<slug>` at workspace root (single hyphen). See `create-worktree.py` and `nicki-workspace.example.yaml`. |
| 3 | `post_create` copy list | Shipped with #1. Per-project `copy` and `post_create` in workspace registry; readable by `create-worktree.py`. |
| 4 | Migrate active task | `tetris-clone-frp` active at `worktrees/tetris-clone-frp-ghost-piece-rendering`; `global-status.json` and `status.json` use unified paths. No legacy `projects/tetris-clone-frp/worktrees/`. Archive: [`archive/ghost-piece-rendering/`](archive/ghost-piece-rendering/). |
| 5 | Wire `sheep-start` to new script | `sheep-start.md` invokes `create-worktree.py` per `start-task/SKILL.md`; legacy `start-worktrees.sh` retired from agent path. Archive: [`archive/wire-sheep-start/`](archive/wire-sheep-start/). |
| 6 | **Gherkin + spec mutual understanding** | Archive: [`archive/gherkin-spec-mutual-understanding/`](archive/gherkin-spec-mutual-understanding/). See below. |
| 15 | `nicki.code-workspace` sync | `scripts/generate-code-workspace.sh` wired into `create-worktree.py` (start) and `close-scope` (close). Warn on regen failure; skip on `--dry-run`. Archive: [`archive/code-workspace-sync/`](archive/code-workspace-sync/). |
| | **status.json YAGNI (v2)** | Simplify per-task status to task-status.v2: `task.completed_steps`, `artifacts.story` gates, no verbose history. Archive: [`archive/status-json-yagni/`](archive/status-json-yagni/). |

Projects on disk: `castlemill-landing`, `project-psychic-lemon`, `tetris-clone-frp` (one active worktree). Gitignored env is copied by script — not a layout problem.

### Gherkin + spec mutual understanding (#6)

**Goal:** Nicki and sheep do not advance past `describe` / `spec` until user and agent share the same understanding — not just formatted output.

| Step | Who | Behavior |
|------|-----|----------|
| `describe` | **sheep-describe** + **story-maker** | Ask before draft; do not invent specifics. Draft in relay until user approves. Write `story.md` only when clear and approved. |
| `describe` relay | **Nicki** | Relay blocked `open_questions` or draft `summary`; re-send sheep-describe with user context. Pause when user is silent. |
| `spec` | **sheep-spec** + **spec-maker** | Block without write when vague or forked; `open_questions` for Nicki relay. No spec file until resolved. |
| `spec` relay | **Nicki** | Present `open_questions`; re-send sheep-spec after user answers. No subtasks while spec `open_questions` non-empty. |
| Gate | **Harness** (P2) | `routing.yaml` / `check-gate.py`: block `spec` without `artifacts.story`; block `subtasks` while spec `open_questions` non-empty. |

**Shipped:** `story-maker/SKILL.md`, `sheep-describe.md`, `nicki.md` (Describe + Spec relay), `sheep-spec.md`, `spec-maker/SKILL.md`, `routing.yaml` (describe → `sheep-describe`).

**Deferred to P2:** `check-gate.py` script enforcement; full E2E tetris ghost-piece Nicki run.

### status.json YAGNI (v2)

**Goal:** Per-task `status.json` holds only fields Nicki and sheep read — step pointers, artifact paths, `open_questions` — without verbose history or duplicate gates.

| Area | Shipped |
|------|---------|
| Schema | `task-status.v2` — `task.completed_steps`, `artifacts.*` pointers, lean `meta` |
| Writers | `current-task-update` emits v2 only; `create-worktree.py` scaffolds v2 example |
| Readers | `status-read.md`, `routing.yaml`, `nicki.md`, sheep disk-inputs use `artifacts.story` |
| Archive | `task-archive` sources process from artifact handoffs, not status history |

**Deferred to P2:** `check-gate.py` script enforcement of v2 gates.
