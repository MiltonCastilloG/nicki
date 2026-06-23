---
worktree: nicki-code-workspace-sync
generated_by: subtask-maker
spec: current-task/specs/code-workspace-sync.yaml
context: current-task/status.json
title: nicki.code-workspace sync
constraints:
  - no-commit
  - no-new-deps
---

# Subtasks

- [x] Keep the regeneration script as the single entry point and simplify it only where wiring requires.
- [x] Run workspace regeneration after successful worktree creation when create-worktree.py completes without dry-run.
- [x] Append a warning to the start handoff when regeneration fails without failing worktree creation.
- [x] Omit workspace regeneration when create-worktree.py runs in dry-run mode.
- [x] Run workspace regeneration after close-scope deletes the worktree directory.
- [x] Warn the operator when close-time regeneration fails without undoing teardown.
- [x] Verify non-dry-run start runs regen and the new worktree appears in nicki.code-workspace with Shared preserved.
- [x] Verify close runs regen and drops the removed worktree while keeping other folder entries.
- [x] Verify regeneration failure during start or close warns only and primary operations still succeed.
- [x] Verify dry-run start skips regen and leaves nicki.code-workspace unchanged.
- [x] Verify regenerated output lists Shared plus one folder per git worktree under worktrees/.

## Fix
<!-- ref: current-task/review-validations/r1-validation.yaml -->
- [x] Run close E2E for three test worktrees and confirm nicki.code-workspace updates
- [x] Run start and close regen-failure E2E and confirm warn-only with primary success
