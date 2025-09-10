"""Main game class with Finite State Machine."""

import sys

import pygame

from .settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from .states.gameplay import GameplayState
from .states.menu import MainMenuState


class Game:
    """Main game class that manages the game loop and state machine."""

    def __init__(self):
        """Initialize the game."""
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()

        # Create screen and clock using settings constants
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("FRED: Ocean Cleanup")
        self.clock = pygame.time.Clock()

        # Create states dictionary
        self.states = {"MENU": MainMenuState(), "GAMEPLAY": GameplayState()}

        # Set initial state
        self.current_state_name = "MENU"
        self.current_state = self.states[self.current_state_name]
        self.current_state.startup()

        # Game loop control
        self.running = True

    def run(self):
        """Main game loop with delta time calculation."""
        while self.running:
            # Calculate delta time in seconds
            dt = self.clock.tick(FPS) / 1000.0

            # Sequential calls to handle_events, update, and draw
            self.handle_events()
            self.update(dt)
            self.draw()

            # Update display
            pygame.display.flip()

        # Cleanup
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Handle pygame events and pass them to current state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.current_state.handle_event(event)

        # Check if current state wants to quit
        if self.current_state.quit:
            self.running = False

        # Check for state transitions
        if self.current_state.done:
            self.flip_state()

    def update(self, dt):
        """Update current state logic.

        Args:
            dt: Delta time in seconds
        """
        self.current_state.update(dt)

    def draw(self):
        """Draw current state to the screen."""
        self.current_state.draw(self.screen)

    def flip_state(self):
        """Handle state transitions."""
        if self.current_state.next_state_name in self.states:
            # Get persistent data from current state
            persistent_data = self.current_state.cleanup()
            previous_state_name = self.current_state_name

            # Switch to new state
            self.current_state_name = self.current_state.next_state_name
            self.current_state = self.states[self.current_state_name]

            # Initialize new state
            self.current_state.startup(persistent_data, previous_state_name)
        else:
            # Invalid state transition, quit game
            self.running = False
