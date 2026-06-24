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
| 6 | **Gherkin + spec mutual understanding** | Archive: [`archive/gherkin-spec-mutual-understanding/`](archive/gherkin-spec-mutual-understanding/). See below. |
| 15 | `nicki.code-workspace` sync | `scripts/generate-code-workspace.sh` wired into `create-worktree.py` (start) and `close-scope` (close). Warn on regen failure; skip on `--dry-run`. Archive: [`archive/code-workspace-sync/`](archive/code-workspace-sync/). |

Projects on disk: `castlemill-landing`, `project-psychic-lemon`, `tetris-clone-frp` (one active worktree). Gitignored env is copied by script — not a layout problem.

### Gherkin + spec mutual understanding (#6)

**Goal:** Nicki and sheep do not advance past `describe` / `spec` until user and agent share the same understanding — not just formatted output.

| Step | Who | Behavior |
|------|-----|----------|
| `describe` | **sheep-describe** + **story-maker** | Ask before draft; do not invent specifics. Draft in relay until user approves. Write `story.md` only when clear and approved. |
| `describe` relay | **Nicki** | Relay blocked `open_questions` or draft `summary`; re-send sheep-describe with user context. Pause when user is silent. |
| `spec` | **sheep-spec** + **spec-maker** | Block without write when vague or forked; `open_questions` for Nicki relay. No spec file until resolved. |
| `spec` relay | **Nicki** | Present `open_questions`; re-send sheep-spec after user answers. No subtasks while spec `open_questions` non-empty. |
| Gate | **Harness** (P2) | `routing.yaml` / `check-gate.py`: block `spec` without `story_artifact`; block `subtasks` while spec `open_questions` non-empty. |

**Shipped:** `story-maker/SKILL.md`, `sheep-describe.md`, `nicki.md` (Describe + Spec relay), `sheep-spec.md`, `spec-maker/SKILL.md`, `routing.yaml` (describe → `sheep-describe`).

**Deferred to P2:** `check-gate.py` script enforcement; full E2E tetris ghost-piece Nicki run.
