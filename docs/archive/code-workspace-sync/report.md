# nicki.code-workspace sync

## Task

- **Slug:** code-workspace-sync
- **Branch:** chore/code-workspace-sync
- **Type:** chore

## Story

start regen · close regen · warn-only failure · dry-run skip · Shared + worktree folders

## Outcome

Merged into `main` at `e84fef0` and pushed to `origin/main`. Final handoff: `current-task/integrates/code-workspace-sync.yaml`.

## Process

Describe captured four Gherkin scenarios for workspace sync on start and close. Spec defined five requirements with YAGNI-friendly script simplification allowed during wiring. Execute wired `regenerate_code_workspace` into create-worktree.py and documented post-teardown regen in close-scope. First review blocked on close and regen-failure E2E; fix round completed all subtasks. User then requested script simplification — 32-line heredoc collapsed to a 5-line one-liner with unchanged output. R3 approved. Sync committed and resolved add/add conflicts on the script and workspace file. Integrate merged to main.

## Decisions

Regen script simplified during wiring; Shared plus one-folder-per-worktree semantics preserved. Sync conflicts resolved by keeping the feature one-liner and regenerating nicki.code-workspace.

## Suggestions

- Run close and regen-failure E2E before first review when spec lists them as acceptance criteria.
- Expect add/add conflicts on workspace script and file when parallel tasks touch the same tooling.
- Scope post-review polish as an explicit sub-round with user approval before acceptance.
