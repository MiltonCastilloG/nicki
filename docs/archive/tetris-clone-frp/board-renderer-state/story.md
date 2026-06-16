Feature: Richer board renderer state

  As a game maintainer
  I want board.js to maintain a structured render state object
  So that canvas drawing can consume locked, falling, ghost, and flash data without changing game.js wiring

  Scenario: Render state holds all visual layers
    Given the board renderer is initialized
    When render state is updated from game logic
    Then the state includes lockedMap for settled cells
    And the state includes fallingBlocks and fallingColor for the active piece
    And the state includes ghostBlocks for the hard-drop preview position
    And the state includes flashRows and flashUntilMs for line-clear flash timing
    And the state includes cached board metrics (cellW, cellH, DPR-scaled sizes)

  Scenario: game.js integration stays stable
    Given game.js calls the existing board.js exported functions
    When the richer render state refactor is applied
    Then all exported function names and signatures used by game.js remain unchanged
    And game behavior is unchanged (render-only refactor)
