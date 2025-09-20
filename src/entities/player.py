"""Player entity (FRED) for Ocean Cleanup game."""

import pygame
from pygame.math import Vector2

from ..settings import (
    ANGULAR_DRAG,
    LINEAR_DRAG_COEFFICIENT,
    MASS,
    MAX_THRUST,
    MAX_TORQUE,
)


class Player(pygame.sprite.Sprite):
    """FRED vehicle entity with differential thrust physics."""

    def __init__(self, pos, groups):
        """Initialize the player sprite.

        Args:
            pos: Position tuple (x, y) for the player
            groups: Sprite groups to add this player to
        """
        super().__init__(groups)

        # Create placeholder visual - 100x50 blue rectangle
        self.original_image = pygame.Surface((100, 50))
        self.original_image.fill((0, 0, 255))  # Blue color
        self.image = self.original_image.copy()

        # Set up rect and position
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # Physics variables (MUST be Vector2)
        self.position = Vector2(pos)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        # Rotational variables
        self.angle = 0.0  # float
        self.angular_velocity = 0.0  # float

        # Input variables
        self.left_thrust = 0.0  # float
        self.right_thrust = 0.0  # float

        # Store physics constants
        self.max_thrust = MAX_THRUST
        self.max_torque = MAX_TORQUE
        self.linear_drag_coefficient = LINEAR_DRAG_COEFFICIENT
        self.angular_drag = ANGULAR_DRAG
        self.mass = MASS

    def get_input(self):
        """Handle input for thrust control."""
        keys = pygame.key.get_pressed()

        # Set thrust values based on key states
        self.left_thrust = 1.0 if keys[pygame.K_a] else 0.0
        self.right_thrust = 1.0 if keys[pygame.K_d] else 0.0

    def update(self, dt):
        """Update player physics and position.

        Args:
            dt: Delta time in seconds
        """
        # 1. Get input (only if not manually controlled)
        if not hasattr(self, "_manual_control"):
            self.get_input()

        # 2. Calculate total thrust and torque
        total_thrust = (self.left_thrust + self.right_thrust) * self.max_thrust
        # Naval convention: left thrust causes right turn (positive angle)
        # right thrust causes left turn (negative angle)
        torque = (self.left_thrust - self.right_thrust) * self.max_torque

        # 3. Direction Vector (calculate BEFORE updating angle)
        self.direction = Vector2(1, 0).rotate(-self.angle)

        # 4. Angular Physics
        # Apply angular drag
        self.angular_velocity *= 1 - self.angular_drag * dt
        # Add torque effect
        self.angular_velocity += torque * dt / self.mass
        # Update angle
        self.angle += self.angular_velocity * dt
        # Wrap angle to prevent unbounded growth
        self.angle %= 360

        # 5. Linear Physics (Euler Integration)
        # Calculate thrust force
        thrust_force = self.direction * total_thrust
        # Calculate drag force
        drag_force = (
            -self.velocity * self.velocity.magnitude() * self.linear_drag_coefficient
        )
        # Calculate total force
        total_force = thrust_force + drag_force
        # Update acceleration
        self.acceleration = total_force / self.mass
        # Update velocity
        self.velocity += self.acceleration * dt
        # Update position
        self.position += self.velocity * dt

        # 6. Visual Update
        # Rotate original image by angle to create new image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        # Update rect center to match position
        self.rect = self.image.get_rect()
        self.rect.center = self.position
