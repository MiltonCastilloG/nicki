# P1-5 — Wire sheep-start to create-worktree.py

## Task

- **Slug:** wire-sheep-start
- **Branch:** chore/wire-sheep-start
- **Type:** chore

## Story

create-worktree.py · start-task skill · retire start-worktrees.sh agent path · JSON handoff · global-status via create-worktree

## Outcome

Merged into `main` at `9409089` and pushed to `origin/main`. Final handoff: `current-task/integrates/wire-sheep-start.yaml`.

## Process

Describe captured four Gherkin scenarios for sheep-start worktree creation. Spec defined seven requirements aligning agent instructions with create-worktree.py. Execute rewired sheep-start.md — defers classification to start-task skill, invokes create-worktree.py per item, maps JSON stdout for sheep-status, removes start-worktrees.sh and parallel register-global-status.sh from the agent path. Review approved at ready_for_acceptance with E2E via nicki-review-wire-self. User accepted and authorized sync through close. Sync committed and pushed chore/wire-sheep-start. Integrate merged to main with current-task conflicts resolved per user (incoming feature branch).

## Decisions

Integrate conflicts on current-task files resolved by keeping feature-branch content; archive supersedes. Legacy shell retired from agent path only.

## Suggestions

- Clean up review E2E worktree nicki-review-wire-self (nicki:7) separately after close.
- Remove nested verification worktrees inside the task worktree before integrate.
- Verify subtask file on disk before marking subtasks complete in status.
