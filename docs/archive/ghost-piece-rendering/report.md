# Ghost piece rendering

## Task

- **Slug:** ghost-piece-rendering
- **Branch:** feature/ghost-piece-rendering
- **Type:** feature

## Story

ghost hard-drop position · downward simulation · draw order · 0.28 alpha · hold D · Space pause

## Outcome

Merged into `master` at `82b7cb1` and pushed to `origin/master`. Final handoff: `current-task/integrates/ghost-piece-rendering.yaml`.

## Process

Describe captured four Gherkin scenarios with board.js-only ghost computation. Spec bounded scope to the board renderer. Execute populated `ghostBlocks` via downward simulation on each redraw. First sync shipped ghost rendering. User then requested incremental keybinding work on the same branch — hold remapped to D, Space toggles pause, docs updated. Second sync and integrate merged everything to master.

## Decisions

Ghost rest equals hard-drop rest, computed in board.js. Keybinding follow-up reused the worktree per user override.

## Suggestions

- Split out-of-scope follow-ups into separate tasks before a second sync.
- Record scope expansion in spec when incremental work crosses file boundaries.
