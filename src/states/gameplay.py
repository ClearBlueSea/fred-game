"""Gameplay state implementation."""

import random

import pygame

from ..entities.bottle import Bottle
from ..entities.player import Player
from ..settings import (
    GREEN,
    PLAYER_START_POS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)
from .base import BaseState


class GameplayState(BaseState):
    """Gameplay state with player control and bottle collection."""

    def __init__(self):
        """Initialize the gameplay state."""
        super().__init__()
        self.font = None
        self.score_font = None
        self.all_sprites = None
        self.bottles = None
        self.player = None
        self.score = 0
        self.bottle_spawn_timer = 0
        self.bottle_spawn_interval = 2.0  # seconds between bottle spawns

    def startup(self, persistent_data=None, previous_state=None):
        """Initialize the gameplay when it becomes active."""
        super().startup(persistent_data, previous_state)

        # Ensure pygame and font subsystem are initialized (safe in headless tests)
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        # Initialize fonts
        self.font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 48)

        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bottles = pygame.sprite.Group()

        # Create player entity
        self.player = Player(PLAYER_START_POS, self.all_sprites)

        # Reset game state
        self.score = 0
        self.bottle_spawn_timer = 0

        # Spawn initial bottles
        for _ in range(5):
            self.spawn_bottle()

    def handle_event(self, event):
        """Handle events for the gameplay.

        Args:
            event: pygame event object
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESCAPE key
                self.done = True
                self.next_state_name = "MENU"

    def spawn_bottle(self):
        """Spawn a new bottle at a random position."""
        # Random position with margin from edges
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)

        # Create bottle and add to groups
        Bottle((x, y), [self.all_sprites, self.bottles])

    def update(self, dt):
        """Update gameplay logic.

        Args:
            dt: Delta time in seconds
        """
        # Update all sprites
        self.all_sprites.update(dt)

        # Check for collisions between player and bottles
        collected = pygame.sprite.spritecollide(self.player, self.bottles, True)
        self.score += len(collected)

        # Spawn new bottles periodically
        self.bottle_spawn_timer += dt
        if self.bottle_spawn_timer >= self.bottle_spawn_interval:
            self.spawn_bottle()
            self.bottle_spawn_timer = 0

    def draw(self, surface):
        """Draw the gameplay screen.

        Args:
            surface: pygame surface to draw on
        """
        # Fill screen with ocean blue-green color
        surface.fill(GREEN)

        # Draw all sprites
        self.all_sprites.draw(surface)

        # Draw UI elements
        self.draw_ui(surface)

    def draw_ui(self, surface):
        """Draw UI elements like score and instructions."""
        # Draw score
        score_text = self.score_font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))

        # Draw controls hint
        controls = ["A - Left Thruster", "D - Right Thruster", "ESC - Menu"]
        y_offset = SCREEN_HEIGHT - 100
        for control in controls:
            text = self.font.render(control, True, WHITE)
            surface.blit(text, (10, y_offset))
            y_offset += 30
