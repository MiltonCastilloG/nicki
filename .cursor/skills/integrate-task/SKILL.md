---
name: integrate-task
description: "Merge feature into target branch and push target branch."
---

# Integrate Task

Merge a synced feature branch into the target branch (default `main`), then push target. Conflicts → [conflict-resolution](../conflict-resolution/SKILL.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Task worktree path | Yes | Feature worktree (context) |
| Target branch worktree | Yes | Where merge runs |
| Target branch | No | Default `main` |
| Feature branch | Yes | From prompt / git |

Ask if paths or feature branch are missing. Do **not** require a sync handoff file.

## Procedure

1. Resolve task and target worktrees. Merge/push only in target worktree. No integrate handoff JSON.
2. Inspect target: clean tree on target branch, remote OK.
3. `git merge --no-ff <feature-branch>` (or record already up to date in `summary`). Resolve conflicts with the user.
4. `git push origin <target_branch>`. No force push. Do not push the feature branch here.

## Safety

- Only when explicitly invoked.
- Never resolve conflicts without user input; never force push; never destructive git without approval.
