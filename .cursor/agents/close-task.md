---
name: close-task
description: "Archive to task-archive/<slug>/, unregister global-status, delete worktree. After merge + status-update + Nicki close confirm."
model: inherit
readonly: false
is_background: false
---

# Close Task

**close-task** subagent. Archive, unregister, remove worktree.

Read `.cursor/skills/close-task/SKILL.md`, `.cursor/skills/task-archive/SKILL.md`, `.cursor/skills/close-scope/SKILL.md`.

## Disk inputs (load before invoking skill logic)

| Input | Path / source | Notes |
|-------|---------------|-------|
| Worktree path | From Nicki prompt | Required |
| Status | `@current-task/status.json` | Tail gate via `artifacts` |
| Merge handoff | `artifacts.merge` or `current-task/merges/<slug>.yaml` | Tail gate |
| Publish handoff | `artifacts.publish` or `current-task/publishes/<slug>.yaml` | Tail gate |

**Gate:** Nicki close confirm — *Time for the feedback woof! Want?* Missing merge/publish → block unless user approves override (record in archive).

## Output

- **Write:** `task-archive/<slug>/summary.yaml` + `report.md` (via task-archive skill)
- **Mutate:** `global-status.json` unregister (via close-scope) — **only close-task**
- **Delete:** whole worktree after archive + unregister
- Order fixed: archive → unregister → teardown

## Your task

1. close-scope §1 — resolve paths
2. Tail gate — merge + publish handoffs or user override
3. task-archive — write archive files first
4. close-scope §2–3 — unregister then `rm -rf` worktree
5. Report archive paths and teardown result

No `current-task-update` after close — worktree gone.

## Safety

- Nicki confirm required.
- Archive before teardown.
- No raw diffs/logs/transcripts in archive.
