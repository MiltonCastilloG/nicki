# Nicki — tasks

Actionable backlog. Analysis: [`investigation.md`](investigation.md), [`investigation-complexity.md`](investigation-complexity.md).

## P1 — Workflow correct functioning

| # | Task | Notes |
|---|------|-------|
| 1 | `create-worktree.py` | **In progress.** Pull base branch, `git worktree add`, workspace `worktrees/<project>-<slug>`, copy gitignored locals from registry, `post_create`, scaffold `current-task/`, register `global-status.json`. |
| 2 | Root `worktrees/` layout | **Unified:** `worktrees/<project>-<slug>` at workspace root (single hyphen). See `create-worktree.py` and `nicki-workspace.example.yaml`. |
| 3 | `post_create` copy list | Per-project `copy` and `post_create` in workspace registry; readable by `create-worktree.py`. |

Worktree path rule: always `worktrees/<project>-<slug>` — e.g. `worktrees/nicki-create-worktree-py`, `worktrees/tetris-clone-frp-hero-section`. Never double hyphen.

Scripts: `.cursor/skills/start-task/scripts/create-worktree.py`, `register-global-status.py`, `WORKFLOW.md` (manual recovery).
