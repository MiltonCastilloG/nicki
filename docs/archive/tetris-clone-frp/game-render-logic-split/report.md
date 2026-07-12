# Task archive — game-render-logic-split

## Task

Slug `game-render-logic-split`. Game render and logic folder split. Branch `refactor/game-render-logic-split`.

## Story

game-logic/ · game-render/ · shared/ collision utils · bootstrap at js root · no adapter · behavior-preserving refactor

## Outcome

Pending integrate into `master`. Feature branch pushed (`b1a584f`). Final handoff at `current-task/syncs/game-render-logic-split.yaml`.

## Process

**Describe** captured Gherkin for splitting game.js and board.js into game-logic/ and game-render/ with shared root modules.

**Spec** defined a move-only, behavior-preserving refactor — no adapter layer between logic and render.

**Subtasks** listed thirteen steps from folder creation through lint, browser load, gameplay parity, save/load, and upload checks.

**Execute** shipped the folder split in earlier passes; final audit documented 26 modules, acyclic imports, and pnpm lint exit 0 with no further moves warranted.

**Review** approved at `ready_for_acceptance`; verify_only scope satisfied; menu.js and shared/ placement flagged as user-approved ADR deviations.

**Sync** committed the split (`b1a584f`), merged `origin/master`, pushed `origin/refactor/game-render-logic-split`.

## Decisions

menu.js stays in game-render/ (presentation-adjacent, user-approved). collision.js and utils.js live under shared/ at js root (user-approved).

## Suggestions

Update ADR-4 to match approved menu.js placement — deferred scope finding recurred at review. Late execute passes should stay verify-only when layout is already shipped — six execute/review cycles preceded sync.
