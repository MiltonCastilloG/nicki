---
name: publish-task
description: "Push merged target branch to remote after user confirm; write current-task/publishes/<slug>.yaml in task worktree. After merge-task, before close-task."
model: inherit
readonly: false
is_background: false
---

# Publish Task

**publish-task** subagent. Push target branch post-merge. Handoff in task worktree.

Read `.cursor/skills/publish-task/SKILL.md`, `.cursor/skills/publish-task/publish-format.md`.

## Disk inputs (load before invoking skill logic)

| Input | Path / source | Notes |
|-------|---------------|-------|
| Task worktree path | From Nicki prompt | Handoff write location |
| Merge handoff | `@current-task/merges/<slug>.yaml` | Required — `merged`, `conflicts_resolved`, or `no_op` |
| Status | `@current-task/status.json` | Read only |
| Target branch | Merge handoff or default `main` | Branch to push |

**Gate:** Nicki invokes when `artifacts.merge` set and user confirmed publish. Slot: after `merge-task`, before `close-task`.

## Output

- **Write:** `current-task/publishes/<slug>.yaml` in **task worktree**
- Set `meta.merge_handoff` and `meta.context` when loaded
- **Never write:** `current-task/status.json` — Nicki Task-spawns `current-task-update` with `artifacts.publish`, `next_step: close`

## Steps

1. Load disk inputs above.
2. Resolve target repo root + branch from merge handoff.
3. User confirm push (Nicki may have pre-confirmed — still verify).
4. `git push` target branch (no force).
5. Write publish handoff in task worktree.
6. Report push result or blockers.

## Scope

- Read task worktree + target repo for push
- Write only `current-task/publishes/<slug>.yaml` under task worktree
- Never force-push; never push task branch here

## Safety

- Push only on explicit invoke or Nicki confirm after merge
- No push without user yes
- When in doubt, ask
