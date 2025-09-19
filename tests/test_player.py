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
        """Test that left thruster only causes positive angle change (right turn)."""
        # Simulate left thruster only
        self.player.left_thrust = 1.0
        self.player.right_thrust = 0.0

        # Update player
        self.player.update(self.dt)

        # Angle should increase (right turn)
        self.assertGreater(self.player.angle, 0)

        # Should have some velocity but less than full thrust
        velocity_magnitude = self.player.velocity.magnitude()
        self.assertGreater(velocity_magnitude, 0)

    def test_left_turn(self):
        """Test that right thruster only causes negative angle change (left turn)."""
        # Simulate right thruster only
        self.player.left_thrust = 0.0
        self.player.right_thrust = 1.0

        # Update player
        self.player.update(self.dt)

        # Angle should decrease (left turn)
        self.assertLess(self.player.angle, 0)

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


if __name__ == "__main__":
    unittest.main()
