"""Base state class for the game state machine."""


class BaseState:
    """Base class for all game states."""

    def __init__(self):
        """Initialize the base state."""
        self.done = False
        self.next_state_name = None
        self.quit = False
        self.persistent_data = {}

    def startup(self, persistent_data=None, previous_state=None):
        """Called when the state becomes active.

        Args:
            persistent_data: Data passed from previous state
            previous_state: Name of the previous state
        """
        pass

    def cleanup(self):
        """Called when the state becomes inactive.

        Returns:
            Data to pass to the next state
        """
        return None

    def handle_event(self, event):
        """Handle pygame events.

        Args:
            event: pygame event object
        """
        pass

    def update(self, dt):
        """Update the state logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    def draw(self, surface):
        """Draw the state to the screen.

        Args:
            surface: pygame surface to draw on
        """
        pass
