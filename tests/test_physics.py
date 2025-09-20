"""Physics and movement tests for FRED: Ocean Cleanup.

Tests differential thrust mechanics, momentum, drag, and boundary collisions.
"""

import pygame.math
import pytest

from .conftest import assert_angle_equal, assert_vector_equal


class TestDifferentialThrust:
    """Test suite for differential thrust control system."""

    def test_left_thrust_only_turns_right(self, game_factory, time_controller):
        """Verify that left thrust only causes a right turn."""
        # Arrange
        game = game_factory(player_angle=0.0)
        player = game.player
        dt = 0.5  # 500ms

        # Act
        player.apply_thrust(left=True, right=False, dt=dt)

        # Assert
        # Angle should increase (turn right)
        expected_angle = player.turn_rate * dt  # 180 * 0.5 = 90 degrees
        assert_angle_equal(player.angle, expected_angle, tolerance=0.1)

        # Should have some forward velocity from turning thrust
        assert player.velocity.length() > 0
        assert (
            player.velocity.length() < player.thrust_power * dt
        )  # Less than full thrust

    def test_right_thrust_only_turns_left(self, game_factory, time_controller):
        """Verify that right thrust only causes a left turn."""
        # Arrange
        game = game_factory(player_angle=0.0)
        player = game.player
        dt = 0.5  # 500ms

        # Act
        player.apply_thrust(left=False, right=True, dt=dt)

        # Assert
        # Angle should decrease (turn left)
        expected_angle = -player.turn_rate * dt  # -180 * 0.5 = -90 degrees
        assert_angle_equal(player.angle, expected_angle, tolerance=0.1)

        # Should have some forward velocity
        assert player.velocity.length() > 0
        assert player.velocity.length() < player.thrust_power * dt

    def test_both_thrusts_move_forward(self, game_factory):
        """Verify that both thrusts result in forward motion with minimal rotation."""
        # Arrange
        game = game_factory(player_angle=45.0)  # Test at non-zero angle
        player = game.player
        initial_angle = player.angle
        dt = 0.5  # 500ms

        # Act
        player.apply_thrust(left=True, right=True, dt=dt)

        # Assert
        # Angle should remain unchanged
        assert_angle_equal(player.angle, initial_angle, tolerance=0.01)

        # Velocity should be in the direction of the angle
        expected_velocity = pygame.math.Vector2(0, -player.thrust_power * dt).rotate(
            initial_angle
        )
        assert_vector_equal(player.velocity, expected_velocity, tolerance=1.0)

    @pytest.mark.parametrize("angle", [0, 45, 90, 180, 270])
    def test_thrust_direction_matches_angle(self, game_factory, angle):
        """Verify thrust acceleration is applied in the correct direction."""
        # Arrange
        game = game_factory(player_angle=angle)
        player = game.player
        dt = 0.1

        # Act
        player.apply_thrust(left=True, right=True, dt=dt)

        # Assert
        # Velocity should be in the direction of player angle
        expected_direction = pygame.math.Vector2(0, -1).rotate(angle)
        actual_direction = (
            player.velocity.normalize()
            if player.velocity.length() > 0
            else pygame.math.Vector2(0, 0)
        )

        if player.velocity.length() > 0:
            dot_product = expected_direction.dot(actual_direction)
            assert dot_product > 0.99, f"Direction mismatch at angle {angle}"


class TestMomentumAndDrag:
    """Test suite for momentum conservation and drag physics."""

    def test_velocity_decreases_after_thrust_stops(self, game_factory):
        """Verify that velocity monotonically decreases when thrust stops."""
        # Arrange
        game = game_factory()
        player = game.player

        # Apply thrust to build up velocity
        player.apply_thrust(left=True, right=True, dt=0.5)
        initial_velocity = player.velocity.length()

        # Act - simulate multiple frames without thrust
        velocities = [initial_velocity]
        for _ in range(10):
            player.update(dt=0.1, world_bounds=game.world_bounds)
            velocities.append(player.velocity.length())

        # Assert - velocity should monotonically decrease
        for i in range(1, len(velocities)):
            assert velocities[i] < velocities[i - 1], (
                f"Velocity did not decrease at step {i}"
            )

        # Should approach zero but not quite reach it due to drag formula
        assert velocities[-1] < initial_velocity * 0.5
        assert velocities[-1] > 0  # Should not completely stop due to exponential decay

    def test_drag_coefficient_effect(self, game_factory):
        """Test that drag coefficient properly affects deceleration."""
        # Arrange
        game = game_factory()
        player = game.player

        # Set initial velocity
        player.velocity = pygame.math.Vector2(100, 0)

        # Act - update with drag
        dt = 1.0  # 1 second
        player.update(dt=dt, world_bounds=game.world_bounds)

        # Assert
        expected_velocity = 100 * (player.drag_coefficient**dt)
        assert pytest.approx(player.velocity.x, abs=0.1) == expected_velocity

    def test_momentum_conservation_during_turn(self, game_factory):
        """Verify that existing momentum is preserved during turns."""
        # Arrange
        game = game_factory()
        player = game.player

        # Give player forward momentum
        player.velocity = pygame.math.Vector2(50, 0)
        initial_speed = player.velocity.length()

        # Act - turn while coasting
        player.apply_thrust(left=True, right=False, dt=0.1)

        # Assert - speed should increase slightly due to turning thrust
        # but original momentum should be preserved
        assert player.velocity.length() > initial_speed * 0.9
        assert player.angle > 0  # Should have turned right


class TestBoundaryCollisions:
    """Test suite for world boundary collision detection and response."""

    def test_left_wall_collision(self, game_factory):
        """Test collision with left boundary stops horizontal movement."""
        # Arrange
        game = game_factory(world_size=(800, 600))
        player = game.player
        player.position = pygame.math.Vector2(30, 300)  # Near left wall
        player.velocity = pygame.math.Vector2(-100, 50)  # Moving left and down

        # Act
        player.update(dt=0.1, world_bounds=game.world_bounds)

        # Assert
        assert player.position.x == player.rect.width // 2  # Clamped to boundary
        assert player.velocity.x == 0  # Horizontal velocity stopped
        assert player.velocity.y > 0  # Vertical velocity preserved

    def test_right_wall_collision(self, game_factory):
        """Test collision with right boundary stops horizontal movement."""
        # Arrange
        game = game_factory(world_size=(800, 600))
        player = game.player
        player.position = pygame.math.Vector2(770, 300)  # Near right wall
        player.velocity = pygame.math.Vector2(100, -50)  # Moving right and up

        # Act
        player.update(dt=0.1, world_bounds=game.world_bounds)

        # Assert
        assert player.position.x == 800 - player.rect.width // 2  # Clamped to boundary
        assert player.velocity.x == 0  # Horizontal velocity stopped
        assert player.velocity.y < 0  # Vertical velocity preserved

    def test_top_wall_collision(self, game_factory):
        """Test collision with top boundary stops vertical movement."""
        # Arrange
        game = game_factory(world_size=(800, 600))
        player = game.player
        player.position = pygame.math.Vector2(400, 30)  # Near top wall
        player.velocity = pygame.math.Vector2(50, -100)  # Moving up and right

        # Act
        player.update(dt=0.1, world_bounds=game.world_bounds)

        # Assert
        assert player.position.y == player.rect.height // 2  # Clamped to boundary
        assert player.velocity.y == 0  # Vertical velocity stopped
        assert player.velocity.x > 0  # Horizontal velocity preserved

    def test_bottom_wall_collision(self, game_factory):
        """Test collision with bottom boundary stops vertical movement."""
        # Arrange
        game = game_factory(world_size=(800, 600))
        player = game.player
        player.position = pygame.math.Vector2(400, 570)  # Near bottom wall
        player.velocity = pygame.math.Vector2(-50, 100)  # Moving down and left

        # Act
        player.update(dt=0.1, world_bounds=game.world_bounds)

        # Assert
        assert player.position.y == 600 - player.rect.height // 2  # Clamped to boundary
        assert player.velocity.y == 0  # Vertical velocity stopped
        assert player.velocity.x < 0  # Horizontal velocity preserved

    def test_corner_collision(self, game_factory):
        """Test collision with corner stops movement in both axes."""
        # Arrange
        game = game_factory(world_size=(800, 600))
        player = game.player
        player.position = pygame.math.Vector2(30, 30)  # Near top-left corner
        player.velocity = pygame.math.Vector2(-100, -100)  # Moving to corner

        # Act
        player.update(dt=0.1, world_bounds=game.world_bounds)

        # Assert
        assert player.position.x == player.rect.width // 2  # Clamped horizontally
        assert player.position.y == player.rect.height // 2  # Clamped vertically
        assert player.velocity.x == 0  # Horizontal velocity stopped
        assert player.velocity.y == 0  # Vertical velocity stopped

    @pytest.mark.parametrize(
        "start_pos,velocity,expected_clamped",
        [
            ((50, 300), (-200, 0), (True, False)),  # Left wall
            ((750, 300), (200, 0), (True, False)),  # Right wall
            ((400, 50), (0, -200), (False, True)),  # Top wall
            ((400, 550), (0, 200), (False, True)),  # Bottom wall
        ],
    )
    def test_boundary_clamping(
        self, game_factory, start_pos, velocity, expected_clamped
    ):
        """Parametrized test for boundary clamping behavior."""
        # Arrange
        game = game_factory(world_size=(800, 600))
        player = game.player
        player.position = pygame.math.Vector2(*start_pos)
        player.velocity = pygame.math.Vector2(*velocity)

        # Act
        player.update(dt=0.5, world_bounds=game.world_bounds)

        # Assert
        if expected_clamped[0]:  # X-axis clamped
            assert player.velocity.x == 0
        if expected_clamped[1]:  # Y-axis clamped
            assert player.velocity.y == 0


class TestPhysicsStability:
    """Test physics stability with various time deltas."""

    @pytest.mark.parametrize("dt", [0.005, 0.016, 0.033, 0.1])
    def test_physics_stable_with_different_deltas(self, game_factory, dt):
        """Ensure physics calculations remain stable with various time deltas."""
        # Arrange
        game = game_factory(world_size=(1000, 1000))
        player = game.player
        player.position = pygame.math.Vector2(500, 500)

        # Act - apply thrust and update multiple times
        for _ in range(int(1.0 / dt)):  # Simulate 1 second
            player.apply_thrust(left=True, right=True, dt=dt)
            player.update(dt=dt, world_bounds=game.world_bounds)

        # Assert - player should remain in bounds and have reasonable values
        assert 0 <= player.position.x <= 1000
        assert 0 <= player.position.y <= 1000
        assert player.velocity.length() < 1000  # Reasonable max speed
        assert not pygame.math.Vector2(
            player.position.x, player.position.y
        ).length() == float("inf")

    def test_no_tunneling_at_high_speed(self, game_factory):
        """Verify no tunneling through boundaries at high speeds."""
        # Arrange
        game = game_factory(world_size=(800, 600))
        player = game.player
        player.position = pygame.math.Vector2(400, 300)
        player.velocity = pygame.math.Vector2(5000, 0)  # Very high speed

        # Act
        player.update(dt=0.1, world_bounds=game.world_bounds)

        # Assert - should be clamped to boundary, not pass through
        assert player.position.x <= 800 - player.rect.width // 2
        assert player.velocity.x == 0  # Should have stopped
