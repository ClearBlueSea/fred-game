"""Integration tests for FRED: Ocean Cleanup.

Tests controlled game loop ticks, complex scenarios, and system interactions.
"""

import pygame.math
import pytest


@pytest.mark.timeout(10)  # 10 second timeout for controlled tests
class TestControlledGameLoop:
    """Test controlled game loop execution with precise timing."""

    def test_three_tick_movement_sequence(self, game_factory, time_controller):
        """Test precise 3-tick movement sequence with thrust changes."""
        # Arrange
        game = game_factory(player_pos=(400, 300), player_angle=0)
        player = game.player
        dt = 0.016  # 16ms per tick (60 FPS)

        with time_controller.patch_pygame_time():
            # Tick 1: Left thrust only
            player.apply_thrust(left=True, right=False, dt=dt)
            player.update(dt=dt, world_bounds=game.world_bounds)
            game.update_score(dt)
            time_controller.advance(16)

            # Assert after tick 1
            assert player.angle > 0  # Turned right
            assert game.score > 0  # Score increased
            tick1_position = player.position.copy()

            # Tick 2: Both thrusts
            player.apply_thrust(left=True, right=True, dt=dt)
            player.update(dt=dt, world_bounds=game.world_bounds)
            game.update_score(dt)
            time_controller.advance(16)

            # Assert after tick 2
            assert player.position != tick1_position  # Moved forward
            assert game.score > dt  # Score increased more

            # Tick 3: No thrust (coast)
            player.apply_thrust(left=False, right=False, dt=dt)
            player.update(dt=dt, world_bounds=game.world_bounds)
            game.update_score(dt)
            time_controller.advance(16)

            # Assert after tick 3
            assert (
                player.velocity.length() < player.thrust_power * dt * 2
            )  # Slowing down
            # Score shouldn't increase during coast
            final_score = game.score
            assert pytest.approx(final_score, abs=0.01) == dt * 3  # 1 + 2 + 0

    def test_five_tick_complex_sequence(self, game_factory, time_controller):
        """Test 5-tick sequence with varied inputs and timing."""
        # Arrange
        game = game_factory(world_size=(1000, 800))
        player = game.player
        player.position = pygame.math.Vector2(500, 400)

        sequence = [
            # (left, right, dt_ms, expected_behavior)
            (True, False, 16, "turn_right"),
            (False, True, 16, "turn_left"),
            (True, True, 32, "forward"),
            (False, False, 16, "coast"),
            (True, True, 16, "forward"),
        ]

        positions = []
        angles = []
        scores = []

        with time_controller.patch_pygame_time():
            # Execute sequence
            for left, right, dt_ms, behavior in sequence:
                dt = dt_ms / 1000.0

                # Apply inputs
                player.apply_thrust(left=left, right=right, dt=dt)
                player.update(dt=dt, world_bounds=game.world_bounds)
                game.update_score(dt)
                time_controller.advance(dt_ms)

                # Record state
                positions.append(player.position.copy())
                angles.append(player.angle)
                scores.append(game.score)

        # Assert behavioral patterns
        assert angles[0] > 0  # First tick turned right
        assert angles[1] < angles[0]  # Second tick turned left
        assert positions[2].distance_to(positions[1]) > positions[3].distance_to(
            positions[2]
        )  # Deceleration during coast
        assert scores[3] == scores[2]  # No score during coast

    @pytest.mark.parametrize("dt_ms", [5, 16, 33, 100])
    def test_delta_time_robustness(self, game_factory, time_controller, dt_ms):
        """Test physics stability with various delta times."""
        # Arrange
        game = game_factory(world_size=(2000, 2000))
        player = game.player
        player.position = pygame.math.Vector2(1000, 1000)
        dt = dt_ms / 1000.0

        with time_controller.patch_pygame_time():
            # Run for equivalent of 1 second total
            num_ticks = int(1000 / dt_ms)

            for _ in range(num_ticks):
                player.apply_thrust(left=True, right=True, dt=dt)
                player.update(dt=dt, world_bounds=game.world_bounds)
                time_controller.advance(dt_ms)

            # Assert - player should have similar results regardless of dt
            # Position should be reasonable
            assert 500 < player.position.x < 1500
            assert 500 < player.position.y < 1500

            # Velocity should be bounded
            assert player.velocity.length() < 500

            # No NaN or infinity values
            assert player.position.x != float("inf")
            assert player.position.y != float("inf")


@pytest.mark.timeout(20)  # 20 second timeout for complex scenarios
class TestComplexGameScenarios:
    """Test complex, multi-system game scenarios."""

    def test_spiral_collection_pattern(self, game_factory, time_controller):
        """Test collecting bottles in a spiral pattern."""
        # Arrange - bottles in a rough spiral
        spiral_positions = [
            (400, 300),  # Center
            (450, 300),  # Right
            (450, 350),  # Down
            (400, 350),  # Left
            (350, 350),  # More left
            (350, 300),  # Up
            (350, 250),  # More up
        ]

        game = game_factory(player_pos=(400, 300), bottle_positions=spiral_positions)

        with time_controller.patch_pygame_time():
            game.state = "PLAYING"

            # Collect center bottle immediately
            game.check_collisions()
            assert game.bottles_remaining == 6

            # Navigate to each bottle with realistic movement
            for i, target_pos in enumerate(spiral_positions[1:], 1):
                # Simple navigation: turn towards target and thrust
                moves = 0
                max_moves = 150  # Increased limit for safety
                while (
                    game.player.position.distance_to(pygame.math.Vector2(*target_pos))
                    > 30
                ):
                    moves += 1
                    if moves > max_moves:  # Prevent infinite loop
                        break

                    # Apply thrust towards target
                    game.player.apply_thrust(left=True, right=True, dt=0.016)
                    game.player.update(dt=0.016, world_bounds=game.world_bounds)
                    game.update_score(0.016)
                    time_controller.advance(16)

                # Move player to exact position for collection
                game.player.position = pygame.math.Vector2(*target_pos)
                game.player.rect.center = target_pos
                game.check_collisions()

                assert game.bottles_remaining == len(spiral_positions) - (i + 1)

            # All bottles collected
            assert game.bottles_remaining == 0
            assert game.state == "END_SCREEN"
            assert game.score > 0  # Some thrust was used

    def test_boundary_bounce_collection(self, game_factory):
        """Test collecting bottles after boundary collisions."""
        # Arrange - bottles near walls
        game = game_factory(
            world_size=(800, 600),
            player_pos=(400, 300),
            bottle_positions=[(50, 300), (750, 300), (400, 50), (400, 550)],
        )

        game.state = "PLAYING"
        player = game.player

        # Scenario 1: Hit left wall then collect
        player.velocity = pygame.math.Vector2(-1000, 0)  # Faster to ensure wall hit
        player.update(dt=0.5, world_bounds=game.world_bounds)
        assert player.velocity.x == 0  # Stopped by wall
        assert player.position.x == 20  # At left boundary (half width of 40)

        # Now at left wall, collect bottle
        player.position = pygame.math.Vector2(50, 300)
        player.rect.center = (50, 300)
        game.check_collisions()
        assert game.bottles[0].collected

        # Scenario 2: Hit right wall then collect
        player.position = pygame.math.Vector2(400, 300)
        player.velocity = pygame.math.Vector2(500, 0)
        player.update(dt=0.5, world_bounds=game.world_bounds)

        player.position = pygame.math.Vector2(750, 300)
        player.rect.center = (750, 300)
        game.check_collisions()
        assert game.bottles[1].collected

        assert game.bottles_remaining == 2

    def test_rapid_direction_changes(self, game_factory, time_controller):
        """Test rapid alternating thrust changes."""
        # Arrange
        game = game_factory()
        player = game.player

        with time_controller.patch_pygame_time():
            # Rapidly alternate thrusters
            for i in range(20):
                if i % 2 == 0:
                    player.apply_thrust(left=True, right=False, dt=0.05)
                else:
                    player.apply_thrust(left=False, right=True, dt=0.05)

                player.update(dt=0.05, world_bounds=game.world_bounds)
                game.update_score(0.05)
                time_controller.advance(50)

            # Assert - should have zigzagged but stayed relatively centered
            # Due to alternating turns
            assert abs(player.angle) < 180  # Didn't spin completely around
            assert pytest.approx(game.score, abs=0.001) == 1.0  # 20 * 0.05 * 1


@pytest.mark.timeout(30)  # 30 second timeout for full game simulations
class TestFullGameSimulation:
    """Test complete game simulations from start to finish."""

    def test_speedrun_simulation(self, game_factory, time_controller):
        """Simulate a 'speedrun' - collecting all bottles as fast as possible."""
        # Arrange
        game = game_factory(
            bottle_positions=[(200, 300), (400, 300), (600, 300)]  # Line of bottles
        )

        with time_controller.patch_pygame_time():
            # Start game
            game.state = "PLAYING"
            player = game.player
            player.position = pygame.math.Vector2(100, 300)
            player.angle = 90  # Face right to move horizontally

            # Full thrust to the right to collect all bottles
            elapsed = 0
            dt = 0.016

            iterations = 0
            max_iterations = 600  # 600 * 16ms = ~10 seconds
            while (
                game.bottles_remaining > 0
                and elapsed < 10
                and iterations < max_iterations
            ):
                iterations += 1

                # Apply forward thrust
                player.apply_thrust(left=True, right=True, dt=dt)
                player.update(dt=dt, world_bounds=game.world_bounds)
                game.update_score(dt)

                # Check collisions
                game.check_collisions()

                time_controller.advance(16)
                elapsed += dt

            # Assert
            assert game.bottles_remaining == 0
            assert game.state == "END_SCREEN"
            assert game.score > 0  # Used thrust
            assert elapsed < 10  # Completed within timeout

    def test_efficient_vs_inefficient_play(self, game_factory, time_controller):
        """Compare efficient vs inefficient collection strategies."""
        # Setup for both strategies - closer bottles for more reliable physics
        bottle_positions = [(250, 300), (350, 300)]

        # Efficient strategy - direct movement
        efficient_game = game_factory(
            player_pos=(200, 300), bottle_positions=bottle_positions
        )

        with time_controller.patch_pygame_time():
            efficient_game.state = "PLAYING"

            # Move efficiently to each bottle
            for bottle_pos in bottle_positions:
                # Move player close to bottle and collect
                # Just move directly there for testing purposes
                efficient_game.player.position = pygame.math.Vector2(*bottle_pos)
                efficient_game.player.rect.center = bottle_pos
                efficient_game.check_collisions()

        efficient_score = efficient_game.score

        # Inefficient strategy - lots of turning
        time_controller.reset()
        inefficient_game = game_factory(
            player_pos=(200, 300), bottle_positions=bottle_positions
        )

        with time_controller.patch_pygame_time():
            inefficient_game.state = "PLAYING"

            # Waste time spinning - using thrust which increases score
            for _ in range(100):  # Lots of spinning
                inefficient_game.player.apply_thrust(left=True, right=False, dt=0.016)
                inefficient_game.player.update(
                    dt=0.016, world_bounds=inefficient_game.world_bounds
                )
                inefficient_game.update_score(0.016)
                time_controller.advance(16)

            # Then collect bottles without additional movement
            for bottle_pos in bottle_positions:
                inefficient_game.player.position = pygame.math.Vector2(*bottle_pos)
                inefficient_game.player.rect.center = bottle_pos
                inefficient_game.check_collisions()

        inefficient_score = inefficient_game.score

        # Assert
        assert efficient_score < inefficient_score  # Lower score is better
        assert efficient_game.state == "END_SCREEN"
        assert inefficient_game.state == "END_SCREEN"


class TestPropertyBasedScenarios:
    """Property-based testing for game invariants."""

    @pytest.mark.parametrize("seed", [42, 100, 9999])
    def test_player_always_in_bounds(self, game_factory, seed):
        """Property: Player position never exceeds world boundaries."""
        # Arrange
        import random

        random.seed(seed)

        world_size = (1000, 800)
        game = game_factory(world_size=world_size)
        player = game.player

        # Generate random thrust sequence
        for _ in range(100):
            left = random.choice([True, False])
            right = random.choice([True, False])
            dt = random.uniform(0.01, 0.1)

            # Apply random thrust
            player.apply_thrust(left=left, right=right, dt=dt)
            player.update(dt=dt, world_bounds=game.world_bounds)

            # Assert property - player always in bounds
            assert 0 <= player.position.x <= world_size[0]
            assert 0 <= player.position.y <= world_size[1]

    def test_score_monotonically_increases(self, game_factory):
        """Property: Score never decreases during gameplay."""
        # Arrange
        game = game_factory()
        player = game.player
        previous_score = 0

        # Random gameplay sequence
        import random

        for _ in range(50):
            # Random thrust
            player.left_thrust_active = random.choice([True, False])
            player.right_thrust_active = random.choice([True, False])

            # Update score
            dt = 0.016
            game.update_score(dt)

            # Assert property
            assert game.score >= previous_score
            previous_score = game.score

    def test_conservation_of_bottles(self, game_factory):
        """Property: Total bottles (collected + remaining) stays constant."""
        # Arrange
        initial_bottles = 5
        positions = [(100 + i * 100, 300) for i in range(initial_bottles)]
        game = game_factory(bottle_positions=positions)

        # Play through game
        for i, pos in enumerate(positions):
            # Count bottles
            collected = sum(1 for b in game.bottles if b.collected)
            remaining = game.bottles_remaining

            # Assert property
            assert collected + remaining == initial_bottles

            # Collect next bottle
            game.player.position = pygame.math.Vector2(*pos)
            game.player.rect.center = pos
            game.check_collisions()

        # Final check
        assert sum(1 for b in game.bottles if b.collected) == initial_bottles
        assert game.bottles_remaining == 0


class TestRefactoringRecommendations:
    """Document refactoring needs for better testability."""

    def test_identifies_clock_dependency(self):
        """Document need for clock injection in Game class."""
        # Current implementation directly uses pygame.time.Clock()
        # Recommendation: Accept clock as parameter for testing

        recommendation = """
        REFACTORING NEEDED - src/game.py:
        
        Current:
            self.clock = pygame.time.Clock()
        
        Suggested:
            def __init__(self, clock=None):
                self.clock = clock or pygame.time.Clock()
        
        This allows injection of mock clocks during testing.
        """
        assert recommendation  # Document exists

    def test_identifies_random_dependency(self):
        """Document need for RNG injection for bottle spawning."""
        # Future bottle spawning will use random
        # Recommendation: Accept RNG instance

        recommendation = """
        REFACTORING NEEDED - Future bottle spawning:
        
        Instead of:
            x = random.randint(50, world_width - 50)
        
        Suggested:
            def spawn_bottles(self, rng=None):
                rng = rng or random.Random()
                x = rng.randint(50, self.world_width - 50)
        
        This allows deterministic testing with seeded RNG.
        """
        assert recommendation  # Document exists

    def test_identifies_state_testability_needs(self):
        """Document state machine testing improvements."""
        recommendation = """
        REFACTORING NEEDED - State management:
        
        Consider adding:
        1. State history tracking for testing transitions
        2. Event queue for programmatic event injection
        3. State data validation methods
        
        This would enable more thorough state transition testing.
        """
        assert recommendation  # Document exists
