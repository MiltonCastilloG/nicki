Feature: Ghost piece rendering

  As a player
  I want to see where the active piece will land
  So that I can place pieces accurately

  Background:
    Given ghost computation and rendering live entirely in board.js from fallingBlocks and lockedMap on redraw without game.js changes
    And the playfield draws layers in order: background/grid, locked blocks, ghost, active falling piece
    And ghost rendering uses the active piece color at reduced opacity via drawGhostCell at approximately 0.28 alpha
    And when fallingBlocks is empty no ghost cells are rendered

  Scenario: Ghost shows hard-drop rest position
    Given an active falling piece above the stack
    When the board is drawn
    Then ghostBlocks is the piece position after repeated downward steps until one more step would collide with locked cells or bounds
    And that position matches where hard drop (Arrow Up) would rest the piece

  Scenario: Ghost at rest overlaps active piece
    Given an active falling piece that cannot move down
    When the board is drawn
    Then ghostBlocks occupies the same cells as the active falling piece

  Scenario: Ghost updates with piece and board changes
    Given an active falling piece
    When the piece moves, rotates, or soft-drops
    Or when lockedMap visualization changes
    Then ghostBlocks is recomputed before draw

  Scenario: No ghost without active piece
    Given fallingBlocks is empty
    When the board is drawn
    Then no ghost cells are rendered
