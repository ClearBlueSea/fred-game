"""Bottle entity for FRED: Ocean Cleanup game."""

import pygame


class Bottle(pygame.sprite.Sprite):
    """Simple collectible bottle sprite class."""
    
    def __init__(self, pos, groups):
        """Initialize the bottle sprite.
        
        Args:
            pos: Position tuple (x, y) for the bottle
            groups: Sprite groups to add this bottle to
        """
        super().__init__(groups)
        
        # Create placeholder visual - 30x50 red rectangle
        self.image = pygame.Surface((30, 50))
        self.image.fill((255, 0, 0))  # Red color
        
        # Set up rect and position
        self.rect = self.image.get_rect()
        self.rect.center = pos
