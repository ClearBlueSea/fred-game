"""Application entry point for FRED: Ocean Cleanup game."""

from .game import Game


def main():
    """Main function to run the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
