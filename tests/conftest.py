"""Core pytest fixtures for FRED: Ocean Cleanup test suite.

This module provides essential fixtures for headless testing, time control,
and game state management to ensure deterministic and automated testing.
"""

import os
import random
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

# Critical: Set headless mode BEFORE importing pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa: E402

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session", autouse=True)
def env_headless():
    """Ensure SDL runs in headless mode for all tests.
    
    This fixture is automatically used for all tests and sets the
    SDL_VIDEODRIVER to 'dummy' before any pygame imports.
    """
    # Already set above, but we verify it here
    assert os.environ.get("SDL_VIDEODRIVER") == "dummy"
    assert os.environ.get("SDL_AUDIODRIVER") == "dummy"
    yield


@pytest.fixture(scope="session")
def pygame_init():
    """Initialize pygame once for the entire test session.
    
    This fixture properly initializes pygame at the start of the test
    session and ensures proper cleanup with pygame.quit() at the end.
    """
    pygame.init()
    pygame.mixer.quit()  # Disable mixer in tests to avoid audio issues
    yield pygame
    pygame.quit()


@pytest.fixture(params=[42, 1337, 2024])
def rng_seed(request):
    """Parametrized fixture providing multiple RNG seeds for testing.
    
    This fixture seeds the random module with different values to ensure
    test robustness across different random states.
    
    Args:
        request: pytest request object containing the seed parameter
        
    Returns:
        int: The seed value used for this test run
    """
    seed = request.param
    random.seed(seed)
    return seed


@dataclass
class TimeController:
    """Mock time controller for deterministic time-based testing.
    
    Provides methods to control and advance mock time for testing
    time-dependent game logic.
    """

    _current_time_ms: float = 0.0

    def now(self) -> float:
        """Get current mock time in milliseconds.
        
        Returns:
            float: Current time in milliseconds
        """
        return self._current_time_ms

    def advance(self, milliseconds: float) -> None:
        """Advance the mock clock by specified milliseconds.
        
        Args:
            milliseconds: Amount to advance the clock
        """
        self._current_time_ms += milliseconds

    def reset(self) -> None:
        """Reset the clock to zero."""
        self._current_time_ms = 0.0

    @contextmanager
    def patch_pygame_time(self):
        """Context manager to patch pygame.time functions.
        
        Yields:
            TimeController: This controller instance
        """
        with patch("pygame.time.get_ticks", side_effect=lambda: int(self.now())):
            with patch("pygame.time.Clock") as mock_clock:
                # Make tick return delta time in ms
                mock_clock.return_value.tick.side_effect = lambda fps=0: 16.67
                yield self


@pytest.fixture
def time_controller():
    """Create a time controller for mocking time in tests.
    
    Returns:
        TimeController: Controller for manipulating mock time
    """
    return TimeController()


@dataclass
class MockPlayer:
    """Mock player entity for testing.
    
    Represents FRED with position, velocity, angle, and thrust control.
    """

    position: pygame.math.Vector2
    velocity: pygame.math.Vector2
    angle: float  # degrees
    rect: pygame.Rect
    left_thrust_active: bool = False
    right_thrust_active: bool = False
    thrust_power: float = 100.0  # pixels/second^2
    drag_coefficient: float = 0.95
    turn_rate: float = 180.0  # degrees/second with single thrust

    def apply_thrust(self, left: bool, right: bool, dt: float) -> None:
        """Apply differential thrust physics.
        
        Args:
            left: Whether left propeller is active
            right: Whether right propeller is active
            dt: Delta time in seconds
        """
        self.left_thrust_active = left
        self.right_thrust_active = right

        if left and right:
            # Both thrusters: move forward
            acceleration = pygame.math.Vector2(0, -self.thrust_power).rotate(self.angle)
            self.velocity += acceleration * dt
        elif left:
            # Left thruster only: turn right
            self.angle += self.turn_rate * dt
            # Small forward component
            acceleration = pygame.math.Vector2(0, -self.thrust_power * 0.3).rotate(self.angle)
            self.velocity += acceleration * dt
        elif right:
            # Right thruster only: turn left
            self.angle -= self.turn_rate * dt
            # Small forward component
            acceleration = pygame.math.Vector2(0, -self.thrust_power * 0.3).rotate(self.angle)
            self.velocity += acceleration * dt

    def update(self, dt: float, world_bounds: pygame.Rect) -> None:
        """Update player position with physics.
        
        Args:
            dt: Delta time in seconds
            world_bounds: Rectangle defining world boundaries
        """
        # Apply drag
        self.velocity *= (self.drag_coefficient ** dt)

        # Update position
        self.position += self.velocity * dt

        # Boundary collision
        if self.position.x < world_bounds.left + self.rect.width // 2:
            self.position.x = world_bounds.left + self.rect.width // 2
            self.velocity.x = 0
        elif self.position.x > world_bounds.right - self.rect.width // 2:
            self.position.x = world_bounds.right - self.rect.width // 2
            self.velocity.x = 0

        if self.position.y < world_bounds.top + self.rect.height // 2:
            self.position.y = world_bounds.top + self.rect.height // 2
            self.velocity.y = 0
        elif self.position.y > world_bounds.bottom - self.rect.height // 2:
            self.position.y = world_bounds.bottom - self.rect.height // 2
            self.velocity.y = 0

        # Update rect position
        self.rect.center = (int(self.position.x), int(self.position.y))


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


@dataclass
class GameWorld:
    """Container for game world state during testing."""

    player: MockPlayer
    bottles: list[MockBottle]
    world_bounds: pygame.Rect
    score: float = 0.0
    bottles_remaining: int = 0
    state: str = "START_SCREEN"

    def update_score(self, dt: float) -> None:
        """Update score based on active thrusters.
        
        Args:
            dt: Delta time in seconds
        """
        if self.player.left_thrust_active:
            self.score += dt
        if self.player.right_thrust_active:
            self.score += dt

    def check_collisions(self) -> None:
        """Check and handle bottle collections."""
        for bottle in self.bottles:
            if not bottle.collected and self.player.rect.colliderect(bottle.rect):
                if bottle.collect():
                    self.bottles_remaining -= 1
                    if self.bottles_remaining == 0:
                        self.state = "END_SCREEN"


@pytest.fixture
def game_factory(pygame_init):
    """Factory fixture for creating test game worlds.
    
    Args:
        pygame_init: Ensures pygame is initialized
        
    Returns:
        callable: Factory function for creating game worlds
    """
    def _create_game(
        world_size: tuple[int, int] = (800, 600),
        player_pos: tuple[float, float] | None = None,
        player_angle: float = 0.0,
        bottle_positions: list[tuple[float, float]] | None = None,
        seed: int | None = None
    ) -> GameWorld:
        """Create a game world for testing.
        
        Args:
            world_size: Width and height of the world
            player_pos: Initial player position (defaults to center)
            player_angle: Initial player angle in degrees
            bottle_positions: List of bottle positions (defaults to random)
            seed: Random seed for bottle placement
            
        Returns:
            GameWorld: Configured game world for testing
        """
        if seed is not None:
            random.seed(seed)

        world_bounds = pygame.Rect(0, 0, *world_size)

        # Create player
        if player_pos is None:
            player_pos = (world_size[0] // 2, world_size[1] // 2)

        player = MockPlayer(
            position=pygame.math.Vector2(*player_pos),
            velocity=pygame.math.Vector2(0, 0),
            angle=player_angle,
            rect=pygame.Rect(0, 0, 40, 60)  # Catamaran size
        )
        player.rect.center = player_pos

        # Create bottles
        bottles = []
        if bottle_positions is None:
            # Generate random positions
            bottle_positions = []
            for _ in range(5):
                x = random.randint(50, world_size[0] - 50)
                y = random.randint(50, world_size[1] - 50)
                bottle_positions.append((x, y))

        for pos in bottle_positions:
            bottle = MockBottle(
                position=pygame.math.Vector2(*pos),
                rect=pygame.Rect(pos[0] - 10, pos[1] - 10, 20, 20)
            )
            bottles.append(bottle)

        return GameWorld(
            player=player,
            bottles=bottles,
            world_bounds=world_bounds,
            score=0.0,
            bottles_remaining=len(bottles),
            state="START_SCREEN"
        )

    return _create_game


@pytest.fixture
def mock_game_class():
    """Fixture providing a mock Game class for testing state transitions.
    
    Returns:
        MagicMock: Mock game class with state management
    """
    mock_game = MagicMock()
    mock_game.states = {
        "MENU": MagicMock(),
        "GAMEPLAY": MagicMock()
    }
    mock_game.current_state_name = "MENU"
    mock_game.current_state = mock_game.states["MENU"]
    mock_game.running = True
    mock_game.screen = MagicMock()
    mock_game.clock = MagicMock()

    return mock_game


# Testing utilities
def assert_vector_equal(v1: pygame.math.Vector2, v2: pygame.math.Vector2, tolerance: float = 0.01):
    """Assert two vectors are approximately equal.
    
    Args:
        v1: First vector
        v2: Second vector
        tolerance: Maximum allowed difference
    """
    assert abs(v1.x - v2.x) < tolerance, f"X mismatch: {v1.x} != {v2.x}"
    assert abs(v1.y - v2.y) < tolerance, f"Y mismatch: {v1.y} != {v2.y}"


def assert_angle_equal(a1: float, a2: float, tolerance: float = 0.1):
    """Assert two angles are approximately equal.
    
    Args:
        a1: First angle in degrees
        a2: Second angle in degrees
        tolerance: Maximum allowed difference in degrees
    """
    # Normalize angles to 0-360 range
    a1 = a1 % 360
    a2 = a2 % 360
    diff = abs(a1 - a2)
    # Handle wrap-around
    if diff > 180:
        diff = 360 - diff
    assert diff < tolerance, f"Angle mismatch: {a1} != {a2} (diff: {diff})"
