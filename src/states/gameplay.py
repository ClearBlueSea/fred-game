"""Gameplay state implementation."""

import pygame

from ..settings import GREEN, WHITE
from .base import BaseState


class GameplayState(BaseState):
    """Gameplay state that displays green background with instructions."""

    def __init__(self):
        """Initialize the gameplay state."""
        super().__init__()
        self.font = None
        self.text_surface = None

    def startup(self, persistent_data=None, previous_state=None):
        """Initialize the gameplay when it becomes active."""
        super().startup(persistent_data, previous_state)

        # Ensure pygame and font subsystem are initialized (safe in headless tests)
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        # Initialize font and create text surface
        self.font = pygame.font.Font(None, 48)
        self.text_surface = self.font.render("Gameplay (Press ESC)", True, WHITE)

    def handle_event(self, event):
        """Handle events for the gameplay.

        Args:
            event: pygame event object
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESCAPE key
                self.done = True
                self.next_state_name = "MENU"

    def update(self, dt):
        """Update gameplay logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    def draw(self, surface):
        """Draw the gameplay screen.

        Args:
            surface: pygame surface to draw on
        """
        # Fill screen with green color
        surface.fill(GREEN)

        # Center the text on screen
        if self.text_surface:
            text_rect = self.text_surface.get_rect()
            text_rect.center = surface.get_rect().center
            surface.blit(self.text_surface, text_rect)
