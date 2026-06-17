# Task archive — create-worktree-py

## Task

Slug `create-worktree-py`. P1 create-worktree.py — worktree creation and registration. Branch `chore/create-worktree-py`.

## Story

create-worktree.py · register-global-status.py · unified worktrees/<project>-<slug> · registry copy/post_create · structured JSON handoff · failure-path WORKFLOW.md

## Outcome

Merged to `main` @ `cee192e` and pushed. Dogfood worktrees removed.

## Process

**Describe/spec** captured unified layout and reduce-agent-workload constraint. **Execute** delivered Python scripts replacing bash worktree flow. **Review** ran three dogfood E2E rounds (nicki, tetris, castlemill) plus failure-path test. **Sync/integrate** completed with SSH push fallback.

## Decisions

Single path formula for all projects. Scripts own mechanical work; agents only need workflow docs when automation fails.

## Suggestions

Wire sheep-start (P1-5). Migrate legacy tetris worktree under projects/ (P1-4).
