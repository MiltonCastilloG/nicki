---
worktree: nicki-wire-sheep-start
generated_by: subtask-maker
spec: current-task/specs/wire-sheep-start.yaml
context: current-task/status.json
title: Wire sheep-start to create-worktree.py
constraints:
  - no-commit
  - no-new-deps
---

# Subtasks

- [x] Confirm start-task skill already defines classification and one create-worktree.py run per work item from workspace root — sheep-start defers without duplicating those rules.
- [x] Replace the worktree creation step in sheep-start agent instructions so each item invokes create-worktree.py from workspace root with project, slug, type, and original — not start-worktrees.sh.
- [x] Remove the separate post-creation global-status registration block from sheep-start so registration stays only on the create-worktree.py success path.
- [x] Update sheep-start handoff example and reporting steps to map fields from create-worktree.py JSON stdout for downstream sheep-status consumption.
- [x] Replace legacy managed-project path and PROJECT= environment guidance with unified worktrees/<project>-<slug> layout per start-task skill.
- [x] Add failure guidance so duplicate or recoverable errors surface script output without overwrite and direct operators to WORKFLOW.md recovery.
- [x] Confirm no start-worktrees.sh or parallel shell registration references remain on the sheep-start agent path.
- [x] Verify sheep-start agent path documents create-worktree.py per start-task skill and omits start-worktrees.sh.
- [x] Exercise create-worktree.py for a nicki self-task and confirm worktree at worktrees/<project>-<slug>, scaffolded status, and global-status entry without legacy shell invocation.
- [x] Exercise create-worktree.py for a managed project and confirm worktree at worktrees/<project>-<slug> with global-status updated for that project.
- [x] Verify successful runs yield structured handoff fields from script JSON stdout matching sheep-status expectations.
- [x] Verify duplicate worktree attempts fail without overwrite and sheep-start guidance surfaces the error plus WORKFLOW.md recovery.
