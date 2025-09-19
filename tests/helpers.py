"""Helper classes for FRED: Ocean Cleanup test suite.

This module provides reusable mock classes and utilities for testing.
"""

from dataclasses import dataclass

import pygame


@dataclass
class MockBottle:
    """Mock bottle entity for testing collection mechanics."""

    position: pygame.math.Vector2
    rect: pygame.Rect
    collected: bool = False

    def collect(self) -> bool:
        """Mark bottle as collected.

        Returns:
            bool: True if bottle was not already collected
        """
        if not self.collected:
            self.collected = True
            return True
        return False
