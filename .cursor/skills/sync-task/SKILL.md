---
name: sync-task
description: "Local commit, merge main into feature branch, push feature branch."
---

# Sync Task

Commit locally, merge base into the feature branch, push the feature branch. Conflicts → [conflict-resolution](../conflict-resolution/SKILL.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Task worktree |
| Base branch | No | Default `main` |
| Commit instruction | Optional | Message / include paths |

Ask if worktree path is missing.

## Procedure

1. Resolve worktree; confirm it is a git worktree. Scope root = that path. Read under scope; git commands with `working_directory` = scope root. Never write a sync handoff JSON.
2. Inspect `git status` / `diff` / branch / remote. Stop if on `main`/`master`, secrets, or ambiguous remote.
3. Stage task paths only (never `current-task/`). Second pass: stage `docs/archive/<slug>/` when present. Commit with a short technical message.
4. Merge base into feature. Record outcome only in the sheep return `summary` (`merged` or `not_needed`). Resolve conflicts with the user.
5. `git push -u origin HEAD` (retry HTTPS↔SSH on auth failure). No force push. No `main`/`master`.

## Safety

- Only when explicitly invoked.
- Never force push, amend without explicit ask + git-safety rules, commit secrets, or update git config.
