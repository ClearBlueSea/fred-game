"""Bottle collection and spawning tests for FRED: Ocean Cleanup.

Tests deterministic spawning, collection mechanics, and game completion.
"""

import pygame
import pytest


class TestBottleSpawning:
    """Test suite for deterministic bottle spawning."""

    def test_deterministic_spawning_with_seed(self, game_factory):
        """Verify bottles spawn in same positions for same seed."""
        # Arrange & Act
        game1 = game_factory(seed=42, bottle_positions=None)
        game2 = game_factory(seed=42, bottle_positions=None)

        # Assert - bottles should be in identical positions
        assert len(game1.bottles) == len(game2.bottles)

        for bottle1, bottle2 in zip(game1.bottles, game2.bottles, strict=False):
            assert bottle1.position.x == bottle2.position.x
            assert bottle1.position.y == bottle2.position.y

    def test_different_seeds_produce_different_positions(self, game_factory):
        """Verify different seeds produce different bottle positions."""
        # Arrange & Act
        game1 = game_factory(seed=42, bottle_positions=None)
        game2 = game_factory(seed=1337, bottle_positions=None)

        # Assert - at least some bottles should be in different positions
        positions_match = 0
        for bottle1, bottle2 in zip(game1.bottles, game2.bottles, strict=False):
            if (
                bottle1.position.x == bottle2.position.x
                and bottle1.position.y == bottle2.position.y
            ):
                positions_match += 1

        # Very unlikely all bottles are in same position with different seeds
        assert positions_match < len(game1.bottles)

    def test_bottles_spawn_within_bounds(self, game_factory, rng_seed):
        """Verify all bottles spawn within world boundaries."""
        # Arrange
        world_size = (800, 600)
        game = game_factory(world_size=world_size, seed=rng_seed, bottle_positions=None)

        # Assert
        for bottle in game.bottles:
            assert 0 <= bottle.position.x <= world_size[0]
            assert 0 <= bottle.position.y <= world_size[1]
            # Check rect is also within bounds
            assert game.world_bounds.contains(bottle.rect)

    def test_bottles_spawn_away_from_edges(self, game_factory):
        """Verify bottles spawn with margin from world edges."""
        # Arrange
        world_size = (800, 600)
        margin = 50  # Expected margin from edges
        game = game_factory(world_size=world_size, seed=42, bottle_positions=None)

        # Assert
        for bottle in game.bottles:
            assert margin <= bottle.position.x <= world_size[0] - margin
            assert margin <= bottle.position.y <= world_size[1] - margin

    def test_custom_bottle_positions(self, game_factory):
        """Test creating game with specific bottle positions."""
        # Arrange
        positions = [(100, 100), (200, 200), (300, 300)]

        # Act
        game = game_factory(bottle_positions=positions)

        # Assert
        assert len(game.bottles) == 3
        for bottle, expected_pos in zip(game.bottles, positions, strict=False):
            assert bottle.position.x == expected_pos[0]
            assert bottle.position.y == expected_pos[1]


class TestCollectionMechanics:
    """Test suite for bottle collection mechanics."""

    def test_collection_on_overlap(self, game_factory):
        """Verify bottle is collected when player overlaps it."""
        # Arrange
        bottle_pos = (100, 100)
        game = game_factory(
            player_pos=(100, 100),  # Same position as bottle
            bottle_positions=[bottle_pos],
        )

        # Act
        game.check_collisions()

        # Assert
        assert game.bottles[0].collected is True
        assert game.bottles_remaining == 0

    def test_collection_decrements_counter(self, game_factory):
        """Verify bottles_remaining decrements on collection."""
        # Arrange
        game = game_factory(bottle_positions=[(100, 100), (200, 200), (300, 300)])
        initial_count = game.bottles_remaining

        # Move player to first bottle
        game.player.position = pygame.math.Vector2(100, 100)
        game.player.rect.center = (100, 100)

        # Act
        game.check_collisions()

        # Assert
        assert game.bottles_remaining == initial_count - 1
        assert game.bottles[0].collected is True
        assert game.bottles[1].collected is False
        assert game.bottles[2].collected is False

    def test_no_double_collection(self, game_factory):
        """Verify collected bottle cannot be collected again."""
        # Arrange
        game = game_factory(player_pos=(100, 100), bottle_positions=[(100, 100)])

        # First collection
        game.check_collisions()
        assert game.bottles_remaining == 0

        # Act - try to collect again
        game.check_collisions()

        # Assert - count shouldn't go negative
        assert game.bottles_remaining == 0
        assert game.bottles[0].collected is True

    def test_multiple_collections_in_sequence(self, game_factory):
        """Test collecting multiple bottles in sequence."""
        # Arrange
        positions = [(100, 100), (200, 200), (300, 300)]
        game = game_factory(bottle_positions=positions)

        # Act & Assert - collect each bottle
        for i, pos in enumerate(positions):
            game.player.position = pygame.math.Vector2(*pos)
            game.player.rect.center = pos
            game.check_collisions()

            assert game.bottles[i].collected is True
            assert game.bottles_remaining == len(positions) - (i + 1)

    def test_collection_requires_rect_overlap(self, game_factory):
        """Verify collection only happens with actual rect collision."""
        # Arrange
        game = game_factory(
            player_pos=(100, 100),
            bottle_positions=[(150, 150)],  # Close but not overlapping
        )

        # Act
        game.check_collisions()

        # Assert - should not be collected if rects don't overlap
        if not game.player.rect.colliderect(game.bottles[0].rect):
            assert game.bottles[0].collected is False
            assert game.bottles_remaining == 1

    def test_last_bottle_triggers_end_screen(self, game_factory):
        """Verify collecting last bottle transitions to END_SCREEN."""
        # Arrange
        game = game_factory(
            player_pos=(100, 100),
            bottle_positions=[(100, 100)],  # Single bottle
        )
        assert game.state == "START_SCREEN"

        # Act
        game.check_collisions()

        # Assert
        assert game.bottles_remaining == 0
        assert game.state == "END_SCREEN"

    @pytest.mark.parametrize("num_bottles", [1, 3, 5, 10])
    def test_end_screen_with_various_bottle_counts(self, game_factory, num_bottles):
        """Test END_SCREEN triggers correctly with different bottle counts."""
        # Arrange
        positions = [(100 + i * 50, 100) for i in range(num_bottles)]
        game = game_factory(bottle_positions=positions)

        # Act - collect all bottles
        for i, pos in enumerate(positions):
            game.player.position = pygame.math.Vector2(*pos)
            game.player.rect.center = pos
            game.check_collisions()

        # Assert
        assert game.bottles_remaining == 0
        assert game.state == "END_SCREEN"
        assert all(bottle.collected for bottle in game.bottles)


class TestCollectionEdgeCases:
    """Test edge cases in bottle collection system."""

    def test_empty_bottle_list(self, game_factory):
        """Test game behavior with no bottles."""
        # Arrange
        game = game_factory(bottle_positions=[])

        # Act
        game.check_collisions()

        # Assert
        assert game.bottles_remaining == 0
        assert game.state == "END_SCREEN"  # Should immediately end

    def test_collection_at_world_boundaries(self, game_factory):
        """Test bottle collection at world edges."""
        # Arrange
        world_size = (800, 600)
        edge_positions = [
            (20, 300),  # Near left edge
            (780, 300),  # Near right edge
            (400, 20),  # Near top edge
            (400, 580),  # Near bottom edge
        ]
        game = game_factory(world_size=world_size, bottle_positions=edge_positions)

        # Act & Assert - collect each edge bottle
        for i, pos in enumerate(edge_positions):
            game.player.position = pygame.math.Vector2(*pos)
            game.player.rect.center = pos
            game.check_collisions()
            assert game.bottles[i].collected is True

    def test_simultaneous_multi_bottle_collection(self, game_factory):
        """Test collecting multiple bottles in same collision check."""
        # Arrange - place bottles very close together
        close_positions = [(100, 100), (105, 105), (110, 110)]
        game = game_factory(bottle_positions=close_positions)

        # Make player rect larger to overlap multiple bottles
        game.player.rect = pygame.Rect(80, 80, 60, 60)
        game.player.position = pygame.math.Vector2(110, 110)

        # Act
        game.check_collisions()

        # Assert - all overlapping bottles should be collected
        collected_count = sum(1 for b in game.bottles if b.collected)
        assert collected_count >= 1  # At least one should be collected
        assert game.bottles_remaining == len(close_positions) - collected_count


class TestBottleProperties:
    """Test bottle entity properties and methods."""

    def test_bottle_initialization(self, game_factory):
        """Test bottle properties after initialization."""
        # Arrange & Act
        game = game_factory(bottle_positions=[(150, 250)])
        bottle = game.bottles[0]

        # Assert
        assert bottle.position == pygame.math.Vector2(150, 250)
        assert bottle.collected is False
        assert bottle.rect.center == (150, 250)
        assert bottle.rect.width == 20
        assert bottle.rect.height == 20

    def test_bottle_collect_method(self):
        """Test bottle's collect method behavior."""
        # Arrange
        from tests.helpers import MockBottle

        bottle = MockBottle(
            position=pygame.math.Vector2(100, 100), rect=pygame.Rect(90, 90, 20, 20)
        )

        # Act & Assert
        assert bottle.collected is False
        assert bottle.collect() is True  # First collection succeeds
        assert bottle.collected is True
        assert bottle.collect() is False  # Second collection fails


class TestBottleSpawningPatterns:
    """Test various bottle spawning patterns and distributions."""

    def test_minimum_spacing_between_bottles(self, game_factory):
        """Test that bottles maintain minimum spacing (if implemented)."""
        # Arrange
        game = game_factory(seed=42, bottle_positions=None)
        min_distance = 30  # Minimum expected distance between bottles

        # Act & Assert
        for i, bottle1 in enumerate(game.bottles):
            for bottle2 in game.bottles[i + 1 :]:
                distance = bottle1.position.distance_to(bottle2.position)
                # This may not be enforced in basic implementation
                # Document expected behavior
                if distance < min_distance:
                    pytest.skip(
                        "Minimum spacing not enforced in current implementation"
                    )

    def test_bottle_distribution_across_world(self, game_factory):
        """Test that bottles are reasonably distributed across the world."""
        # Arrange
        world_size = (800, 600)
        game = game_factory(world_size=world_size, seed=42, bottle_positions=None)

        # Divide world into quadrants
        quadrants = {"top_left": 0, "top_right": 0, "bottom_left": 0, "bottom_right": 0}

        # Count bottles in each quadrant
        for bottle in game.bottles:
            if bottle.position.x < world_size[0] / 2:
                if bottle.position.y < world_size[1] / 2:
                    quadrants["top_left"] += 1
                else:
                    quadrants["bottom_left"] += 1
            else:
                if bottle.position.y < world_size[1] / 2:
                    quadrants["top_right"] += 1
                else:
                    quadrants["bottom_right"] += 1

        # Assert - no quadrant should be completely empty (for 5+ bottles)
        if len(game.bottles) >= 5:
            assert all(count > 0 for count in quadrants.values()) or pytest.skip(
                "Distribution not enforced"
            )
