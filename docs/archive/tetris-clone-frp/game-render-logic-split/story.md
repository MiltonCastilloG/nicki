# game-render-logic-split — Organize game JS into logic and render folders

Behavior-preserving refactor: split `game.js` and `board.js` into `game-logic/` and `game-render/` under `public/assets/js/`.

---

## Design decisions (approved)

| ADR | Decision |
| --- | -------- |
| ADR-1 | **`game-logic/`** — `game.js` (Redux stores, streams, input, game loop) and `tetromino.js` (piece movement/spawn) |
| ADR-2 | **`game-render/`** — `board.js` (canvas playfield, layout sizing, hold/upcoming previews, `playfieldRenderState`, ghost draw, line-clear flash) |
| ADR-3 | **Shared at `js/` root** — `collision.js` and `utils.js` remain importable by both layers without circular dependencies |
| ADR-4 | **Bootstrap unchanged** — `initGame.js`, `menu.js`, and `api.js` stay at `js/` root; `config/` and `lib/` remain shared |
| ADR-5 | **No adapter layer** — `game.js` keeps direct subscribe→render calls to `board.js` exports (move-only refactor) |

---

## Feature: Game JS reorganized into game-logic and game-render

As a game maintainer  
I want game.js and board.js split into dedicated folders by concern  
So that logic and rendering are easier to navigate without changing gameplay

```gherkin
Background:
  Given the entry point remains menu.js loaded from index.html
  And all gameplay behavior is unchanged (behavior-preserving refactor)
```

### Scenario: Module layout under public/assets/js

```gherkin
Given game.js contains Redux stores, stream input, and game-loop orchestration
And board.js contains canvas drawing, layout sizing, and preview panels
When the reorganization is complete
Then game.js lives under game-logic/
And board.js lives under game-render/
And tetromino.js lives under game-logic/
And collision.js and utils.js remain at the js/ root as shared modules
And config/ and lib/ remain shared
And initGame.js, menu.js, and api.js remain at the js/ root as bootstrap and peripheral modules
```

### Scenario: Import graph and lint stay valid

```gherkin
When all relative import paths are updated
Then pnpm lint passes with no new errors
And the browser loads the game without module resolution errors
```

### Scenario: Fresh game plays identically

```gherkin
Given I start a new game from the menu
When I move, rotate, soft-drop, hard-drop, hold, pause, and clear lines
Then piece movement, scoring, hold lock, delay clock ticks, and line-clear flash behave as before
And the playfield, hold, upcoming queue, and score panels render correctly
```

### Scenario: Load saved game still works

```gherkin
Given a saved game hash exists on the server
When I load it from the menu
Then board state, locked map, and active piece restore correctly
And gameplay continues without errors
```

### Scenario: Upload and responsive layout unchanged

```gherkin
Given a game is in progress
When I upload the game state or resize the viewport
Then upload still returns a hash alert
And playfield sizing, DPR scaling, and mobile rail layout behave as before
```
