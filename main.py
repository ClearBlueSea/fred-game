"""Main game application for FRED: Ocean Cleanup."""

import pygame
import sys

from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_START_POS
from src.entities.player import Player
from src.entities.bottle import Bottle


def main():
    """Main game loop."""
    # Initialize Pygame
    pygame.init()

    # Create game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("FRED: Ocean Cleanup - Phase 2 Prototype")

    # Create clock for frame rate limiting
    clock = pygame.time.Clock()

    # Create sprite groups
    all_sprites = pygame.sprite.Group()

    # Create player
    player = Player(PLAYER_START_POS, all_sprites)

    # Create test bottle
    test_bottle = Bottle((400, 200), all_sprites)

    # Game loop
    running = True
    while running:
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update all sprites
        all_sprites.update(dt)

        # Render
        # Light blue background (representing water)
        screen.fill((173, 216, 230))  # Light blue color

        # Draw all sprites
        all_sprites.draw(screen)

        # Update display
        pygame.display.flip()

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
