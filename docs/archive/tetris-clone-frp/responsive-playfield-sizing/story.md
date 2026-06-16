Feature: Responsive playfield sizing (desktop and mobile)

  As a player on any device
  I want the Tetris playfield to scale to my screen and orientation
  So that the game fits comfortably, stays sharp, and does not fight touch scrolling

  Background:
    Given the abstract grid is 10 columns by 20 rows
    And game logic uses abstract grid coordinates only

  Scenario: Playfield scales from container and viewport limits
    Given the playfield sits inside a layout container
    When the browser viewport or container size changes
    Then display scale is computed from container bounds and viewport limits
    And visualViewport dimensions are used when available
    And canvas CSS size and DPR backing buffer are updated together
    And cell pixel metrics are recomputed on resize

  Scenario: Mobile portrait on a narrow phone
    Given the device is in portrait with a narrow viewport
    When the playfield is laid out
    Then cell size meets a minimum readable size on small screens
    And safe-area-inset padding is respected for notched devices
    And the canvas uses touch-action none so play does not steal page scroll
    And side panels stack below the playfield when space is tight

  Scenario: Orientation change and visualViewport resize
    Given the game is running on a mobile browser
    When the device rotates between portrait and landscape
    Or when the visualViewport resizes (e.g. mobile browser chrome)
    Then scale and cell metrics are recomputed after a debounced resize
    And the abstract grid remains 10x20

  Scenario: Crisp rendering at high DPR
    Given a display with devicePixelRatio greater than 1
    When the canvas is resized
    Then backing store dimensions equal CSS size times DPR (rounded)
    And block and grid visuals remain sharp without blur

  Scenario: No layout reads in hot movement paths
    Given a piece is falling or moving on the board
    When the game tick runs movement and rendering
    Then cached cell metrics from render state are used
    And getBoundingClientRect and other layout reads are not called per tick
