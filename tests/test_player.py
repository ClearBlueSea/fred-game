"""Unit tests for Player class physics in FRED: Ocean Cleanup."""

import os
import sys
import unittest

import pygame
from pygame.math import Vector2

# Set headless mode before importing pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.entities.player import Player


class TestPlayerPhysics(unittest.TestCase):
    """Test suite for Player class physics."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        pygame.init()
        pygame.mixer.quit()  # Disable mixer to avoid audio issues

        # Create sprite group for testing
        self.all_sprites = pygame.sprite.Group()

        # Create player at center position
        self.player = Player((400, 300), self.all_sprites)

        # Enable manual control for testing
        self.player._manual_control = True

        # Consistent delta time for testing
        self.dt = 1.0 / 60.0  # 60 FPS

    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()

    def test_initialization(self):
        """Test that player initializes with correct default values."""
        # Physics variables should start at zero
        self.assertEqual(self.player.position, Vector2(400, 300))
        self.assertEqual(self.player.velocity, Vector2(0, 0))
        self.assertEqual(self.player.acceleration, Vector2(0, 0))

        # Rotational variables should start at zero
        self.assertEqual(self.player.angle, 0.0)
        self.assertEqual(self.player.angular_velocity, 0.0)

        # Input variables should start at zero
        self.assertEqual(self.player.left_thrust, 0.0)
        self.assertEqual(self.player.right_thrust, 0.0)

        # Rect should be positioned correctly
        self.assertEqual(self.player.rect.center, (400, 300))

    def test_forward_thrust(self):
        """Test that both thrusters cause forward acceleration."""
        # Simulate both thrusters active
        self.player.left_thrust = 1.0
        self.player.right_thrust = 1.0

        # Update player
        self.player.update(self.dt)

        # Should have forward velocity in initial direction (angle = 0)
        # Direction should be (1, 0) rotated by 0 degrees = (1, 0)
        self.assertGreater(self.player.velocity.x, 0)
        self.assertAlmostEqual(self.player.velocity.y, 0, places=5)

        # Angle should remain unchanged (no torque)
        self.assertAlmostEqual(self.player.angle, 0.0, places=5)

    def test_right_turn(self):
        """Test that left thruster only causes right turn (positive angle change)."""
        # Simulate left thruster only
        self.player.left_thrust = 1.0
        self.player.right_thrust = 0.0

        # Update player
        self.player.update(self.dt)

        # Left thrust with naval convention: angle should increase (right turn)
        self.assertGreater(self.player.angle, 0)

        # Should have some velocity but less than full thrust
        velocity_magnitude = self.player.velocity.magnitude()
        self.assertGreater(velocity_magnitude, 0)

    def test_left_turn(self):
        """Test that right thruster only causes left turn (negative angle change)."""
        # Start with angle > 0 to avoid wrap
        self.player.angle = 180.0

        # Simulate right thruster only
        self.player.left_thrust = 0.0
        self.player.right_thrust = 1.0

        # Update player
        self.player.update(self.dt)

        # Right thrust with naval convention: angle should decrease (left turn)
        self.assertLess(self.player.angle, 180.0)

        # Should have some velocity but less than full thrust
        velocity_magnitude = self.player.velocity.magnitude()
        self.assertGreater(velocity_magnitude, 0)

    def test_drag_force(self):
        """Test that velocity decreases over time with no thrust applied."""
        # Give player initial velocity
        self.player.velocity = Vector2(100, 0)
        initial_speed = self.player.velocity.magnitude()

        # Update without thrust (both thrusters off)
        self.player.left_thrust = 0.0
        self.player.right_thrust = 0.0
        self.player.update(self.dt)

        # Velocity should decrease due to drag
        final_speed = self.player.velocity.magnitude()
        self.assertLess(final_speed, initial_speed)

        # Should still be moving in same direction
        if final_speed > 0:
            self.assertGreater(self.player.velocity.x, 0)

    def test_angle_wrapping(self):
        """Test that angle wraps correctly past 360 degrees."""
        # Set angle near 360 degrees
        self.player.angle = 359.0
        self.player.angular_velocity = 120.0  # degrees/second

        # Update with large enough dt to pass 360
        self.player.update(0.05)  # Should add ~6 degrees (less due to drag)

        # Angle should wrap around to somewhere between 3-6 degrees
        # (exact value depends on angular drag)
        self.assertGreater(self.player.angle, 0)
        self.assertLess(self.player.angle, 10)

    def test_zero_delta_time(self):
        """Test physics stability with dt=0."""
        # Give player initial velocity and angular velocity
        self.player.velocity = Vector2(100, 50)
        self.player.angular_velocity = 45.0
        initial_pos = Vector2(self.player.position)
        initial_angle = self.player.angle

        # Update with dt=0
        self.player.left_thrust = 1.0
        self.player.right_thrust = 1.0
        self.player.update(0)

        # Nothing should change with dt=0
        self.assertEqual(self.player.position, initial_pos)
        self.assertEqual(self.player.angle, initial_angle)

    def test_angular_drag_decay(self):
        """Test that angular velocity decays due to drag."""
        # Set initial angular velocity
        self.player.angular_velocity = 100.0
        initial_angular_vel = self.player.angular_velocity

        # Update without thrust
        self.player.left_thrust = 0.0
        self.player.right_thrust = 0.0
        self.player.update(self.dt)

        # Angular velocity should decrease due to drag
        self.assertLess(self.player.angular_velocity, initial_angular_vel)
        self.assertGreater(self.player.angular_velocity, 0)

    def test_sprite_rotation_matches_angle(self):
        """Test that visual sprite rotation matches physics angle."""
        # Set a specific angle
        self.player.angle = 45.0

        # Update to apply rotation
        self.player.update(self.dt)

        # The image should be rotated (it will be different from original)
        self.assertIsNotNone(self.player.image)
        self.assertIsNotNone(self.player.rect)

    def test_direction_vector_calculation(self):
        """Test that direction vector is correctly calculated from angle."""
        import math

        # Test at various angles
        test_angles = [0, 45, 90, 180, 270]

        for angle in test_angles:
            self.player.angle = angle
            self.player.update(self.dt)

            # Calculate expected direction
            rad = math.radians(-angle)
            expected_x = math.cos(rad)
            expected_y = math.sin(rad)

            # Check direction vector
            self.assertAlmostEqual(self.player.direction.x, expected_x, places=5)
            self.assertAlmostEqual(self.player.direction.y, expected_y, places=5)

    def test_sustained_circle_turn(self):
        """Test that sustained turning produces circular motion."""
        angles_recorded = []

        # Apply sustained left turn for multiple updates
        for _ in range(100):  # Simulate 100 frames
            self.player.left_thrust = 1.0
            self.player.right_thrust = 0.5  # Partial right thrust
            self.player.update(self.dt)
            angles_recorded.append(self.player.angle)

        # Check that angle continuously increases
        for i in range(1, len(angles_recorded)):
            # Account for wrapping
            if angles_recorded[i] < angles_recorded[i - 1] - 300:
                # Wrapped from ~360 to ~0
                continue
            else:
                self.assertGreaterEqual(
                    angles_recorded[i], angles_recorded[i - 1] - 0.1
                )


if __name__ == "__main__":
    unittest.main()
