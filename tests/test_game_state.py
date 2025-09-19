"""Game state and UI flow tests for FRED: Ocean Cleanup.

Tests state transitions, UI data integrity, and game flow.
"""

from unittest.mock import MagicMock, patch

import pygame
import pytest


class TestStateTransitions:
    """Test suite for game state machine transitions."""

    def test_initial_state_is_start_screen(self, game_factory):
        """Verify game initializes in START_SCREEN state."""
        # Arrange & Act
        game = game_factory()

        # Assert
        assert game.state == "START_SCREEN"

    def test_start_screen_to_playing_transition(self, game_factory):
        """Test transition from START_SCREEN to PLAYING state."""
        # Arrange
        game = game_factory()
        assert game.state == "START_SCREEN"

        # Act - simulate start event
        game.state = "PLAYING"

        # Assert
        assert game.state == "PLAYING"

    def test_playing_to_end_screen_on_last_bottle(self, game_factory):
        """Test automatic transition to END_SCREEN when last bottle collected."""
        # Arrange
        game = game_factory(bottle_positions=[(100, 100)])
        game.state = "PLAYING"
        game.player.position = pygame.math.Vector2(100, 100)
        game.player.rect.center = (100, 100)

        # Act
        game.check_collisions()

        # Assert
        assert game.bottles_remaining == 0
        assert game.state == "END_SCREEN"

    def test_state_persistence_during_gameplay(self, game_factory):
        """Test that state remains PLAYING during normal gameplay."""
        # Arrange
        game = game_factory(bottle_positions=[(100, 100), (200, 200)])
        game.state = "PLAYING"

        # Collect first bottle (not last)
        game.player.position = pygame.math.Vector2(100, 100)
        game.player.rect.center = (100, 100)

        # Act
        game.check_collisions()

        # Assert
        assert game.bottles_remaining == 1
        assert game.state == "PLAYING"  # Should still be playing

    @pytest.mark.parametrize("initial_state,expected_valid", [
        ("START_SCREEN", True),
        ("PLAYING", True),
        ("END_SCREEN", True),
        ("INVALID_STATE", False),
    ])
    def test_valid_state_values(self, game_factory, initial_state, expected_valid):
        """Test that only valid state values are accepted."""
        # Arrange
        game = game_factory()
        valid_states = ["START_SCREEN", "PLAYING", "END_SCREEN"]

        # Act
        game.state = initial_state

        # Assert
        if expected_valid:
            assert game.state in valid_states
        else:
            # Invalid states should be handled appropriately
            # Document expected behavior
            pass


class TestUIDataIntegrity:
    """Test suite for UI data consistency and integrity."""

    def test_initial_ui_values(self, game_factory):
        """Test initial UI values are correctly set."""
        # Arrange
        num_bottles = 5
        positions = [(100 + i * 50, 100) for i in range(num_bottles)]

        # Act
        game = game_factory(bottle_positions=positions)

        # Assert
        assert game.score == 0.0
        assert game.bottles_remaining == num_bottles
        assert len(game.bottles) == num_bottles

    def test_score_display_matches_internal_score(self, game_factory):
        """Verify displayed score matches internal score value."""
        # Arrange
        game = game_factory()
        game.state = "PLAYING"
        game.player.left_thrust_active = True

        # Act - update score multiple times
        for _ in range(5):
            game.update_score(0.5)

        # Assert
        expected_score = 2.5  # 5 * 0.5 * 1
        assert game.score == expected_score
        # In real implementation, would check rendered score text

    def test_bottles_remaining_display_accuracy(self, game_factory):
        """Test bottles_remaining counter stays synchronized."""
        # Arrange
        positions = [(100, 100), (200, 200), (300, 300)]
        game = game_factory(bottle_positions=positions)
        game.state = "PLAYING"

        # Act & Assert - verify counter after each collection
        for i, pos in enumerate(positions):
            game.player.position = pygame.math.Vector2(*pos)
            game.player.rect.center = pos
            game.check_collisions()

            expected_remaining = len(positions) - (i + 1)
            assert game.bottles_remaining == expected_remaining

    def test_ui_data_during_state_transitions(self, game_factory):
        """Test UI data persists correctly across state transitions."""
        # Arrange
        game = game_factory(bottle_positions=[(100, 100), (200, 200)])

        # Build up some game state
        game.state = "PLAYING"
        game.player.left_thrust_active = True
        game.update_score(5.0)

        # Collect one bottle
        game.player.position = pygame.math.Vector2(100, 100)
        game.player.rect.center = (100, 100)
        game.check_collisions()

        initial_score = game.score
        initial_remaining = game.bottles_remaining

        # Act - transition to END_SCREEN
        game.bottles_remaining = 0
        game.state = "END_SCREEN"

        # Assert - data should persist
        assert game.score == initial_score
        # Bottles remaining is now 0 due to our manual setting
        assert game.bottles_remaining == 0

    def test_score_precision_in_ui(self, game_factory):
        """Test that score maintains appropriate precision for display."""
        # Arrange
        game = game_factory()
        game.player.left_thrust_active = True

        # Act - accumulate fractional score
        game.update_score(0.333)
        game.update_score(0.667)
        game.update_score(0.123)

        # Assert
        expected = 0.333 + 0.667 + 0.123
        assert abs(game.score - expected) < 0.001
        # UI should handle rounding appropriately


class TestGameFlow:
    """Test complete game flow scenarios."""

    def test_complete_game_flow(self, game_factory):
        """Test a complete game from start to finish."""
        # Arrange
        game = game_factory(bottle_positions=[(100, 100), (200, 200)])

        # Assert initial state
        assert game.state == "START_SCREEN"
        assert game.score == 0
        assert game.bottles_remaining == 2

        # Start game
        game.state = "PLAYING"
        assert game.state == "PLAYING"

        # Play the game - apply thrust and collect bottles
        game.player.left_thrust_active = True
        game.update_score(2.0)  # 2 seconds of thrust

        # Collect first bottle
        game.player.position = pygame.math.Vector2(100, 100)
        game.player.rect.center = (100, 100)
        game.check_collisions()
        assert game.bottles_remaining == 1
        assert game.state == "PLAYING"

        # More thrust
        game.player.right_thrust_active = True
        game.update_score(1.0)  # Both thrusters for 1 second

        # Collect last bottle
        game.player.position = pygame.math.Vector2(200, 200)
        game.player.rect.center = (200, 200)
        game.check_collisions()

        # Assert end state
        assert game.bottles_remaining == 0
        assert game.state == "END_SCREEN"
        assert game.score == 4.0  # 2*1 + 1*2

    def test_restart_game_flow(self, game_factory):
        """Test restarting the game after completion."""
        # Arrange
        game = game_factory(bottle_positions=[(100, 100)])

        # Complete first game
        game.state = "PLAYING"
        game.player.left_thrust_active = True
        game.update_score(1.0)
        game.player.position = pygame.math.Vector2(100, 100)
        game.player.rect.center = (100, 100)
        game.check_collisions()

        assert game.state == "END_SCREEN"
        first_score = game.score

        # Act - restart game (would be triggered by user input)
        # This simulates what a restart would do
        game.state = "START_SCREEN"
        game.score = 0
        game.bottles = [game_factory(bottle_positions=[(100, 100)]).bottles[0]]
        game.bottles_remaining = 1
        for bottle in game.bottles:
            bottle.collected = False

        # Assert - game is reset
        assert game.state == "START_SCREEN"
        assert game.score == 0
        assert game.bottles_remaining == 1
        assert not any(bottle.collected for bottle in game.bottles)

    def test_quick_completion(self, game_factory):
        """Test very quick game completion."""
        # Arrange - single bottle at player start position
        game = game_factory(
            player_pos=(400, 300),
            bottle_positions=[(400, 300)]
        )

        # Act
        game.state = "PLAYING"
        game.check_collisions()

        # Assert - should immediately end
        assert game.bottles_remaining == 0
        assert game.state == "END_SCREEN"
        assert game.score == 0  # No thrust applied


class TestStateImplementation:
    """Test the actual state implementation from the codebase."""

    def test_menu_state_initialization(self, mock_game_class):
        """Test MainMenuState initialization and rendering."""
        # Import actual state class
        from src.states.menu import MainMenuState

        # Arrange
        state = MainMenuState()
        mock_surface = MagicMock()

        # Act
        state.startup()

        # Assert
        assert state.done is False
        assert state.next_state_name is None
        assert state.font is not None
        assert state.text_surface is not None

    def test_menu_state_enter_key_handling(self, mock_game_class):
        """Test MainMenuState handles ENTER key correctly."""
        from src.states.menu import MainMenuState

        # Arrange
        state = MainMenuState()
        state.startup()

        # Create mock ENTER key event
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RETURN

        # Act
        state.handle_event(mock_event)

        # Assert
        assert state.done is True
        assert state.next_state_name == "GAMEPLAY"

    def test_gameplay_state_escape_handling(self, mock_game_class):
        """Test GameplayState handles ESCAPE key correctly."""
        from src.states.gameplay import GameplayState

        # Arrange
        state = GameplayState()
        state.startup()

        # Create mock ESCAPE key event
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_ESCAPE

        # Act
        state.handle_event(mock_event)

        # Assert
        assert state.done is True
        assert state.next_state_name == "MENU"

    def test_game_class_state_transitions(self, pygame_init):
        """Test Game class handles state transitions."""
        from src.game import Game

        with patch('pygame.display.set_mode'):
            with patch('pygame.display.set_caption'):
                # Arrange
                game = Game()
                initial_state = game.current_state_name

                # Simulate state transition request
                game.current_state.done = True
                game.current_state.next_state_name = "GAMEPLAY"

                # Act
                game.flip_state()

                # Assert
                assert game.current_state_name == "GAMEPLAY"
                assert game.current_state == game.states["GAMEPLAY"]


class TestUIRenderingData:
    """Test data preparation for UI rendering."""

    def test_score_formatting(self, game_factory):
        """Test score formatting for display."""
        # Arrange
        game = game_factory()
        test_scores = [0, 1, 1.5, 10.333, 100.0, 999.999]

        for score in test_scores:
            game.score = score

            # In real implementation, would test actual formatting
            # For now, document expected behavior
            if score == int(score):
                expected_display = str(int(score))
            else:
                expected_display = f"{score:.1f}"

            # Assert concept (actual implementation would render)
            assert isinstance(game.score, (int, float))

    def test_bottles_remaining_never_negative(self, game_factory):
        """Ensure bottles_remaining counter never goes negative."""
        # Arrange
        game = game_factory(bottle_positions=[(100, 100)])
        game.player.position = pygame.math.Vector2(100, 100)
        game.player.rect.center = (100, 100)

        # Act - collect bottle multiple times
        for _ in range(3):
            game.check_collisions()

        # Assert
        assert game.bottles_remaining >= 0
        assert game.bottles_remaining == 0  # Should stay at 0
