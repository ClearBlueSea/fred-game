"""Main menu state implementation."""

import pygame

from ..settings import BLUE, WHITE
from .base import BaseState


class MainMenuState(BaseState):
    """Main menu state that displays blue background with instructions."""

    def __init__(self):
        """Initialize the main menu state."""
        super().__init__()
        self.font = None
        self.text_surface = None

    def startup(self, persistent_data=None, previous_state=None):
        """Initialize the menu when it becomes active."""
        super().startup(persistent_data, previous_state)

        # Ensure pygame and font subsystem are initialized (safe in headless tests)
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        # Initialize font and create text surface
        self.font = pygame.font.Font(None, 48)
        self.text_surface = self.font.render("Main Menu (Press ENTER)", True, WHITE)

    def handle_event(self, event):
        """Handle events for the main menu.

        Args:
            event: pygame event object
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # ENTER key
                self.done = True
                self.next_state_name = "GAMEPLAY"

    def update(self, dt):
        """Update menu logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    def draw(self, surface):
        """Draw the main menu.

        Args:
            surface: pygame surface to draw on
        """
        # Fill screen with blue color
        surface.fill(BLUE)

        # Center the text on screen
        if self.text_surface:
            text_rect = self.text_surface.get_rect()
            text_rect.center = surface.get_rect().center
            surface.blit(self.text_surface, text_rect)
