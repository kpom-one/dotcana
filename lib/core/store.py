"""
Abstract interface for state storage.

Defines contract for loading/saving game states.
Implementations: FileStore (DOT files), MemoryStore (dict-based).
"""
from abc import ABC, abstractmethod
from pathlib import Path


class StateStore(ABC):
    """Abstract base class for state storage backends."""

    @abstractmethod
    def load_state(self, path: Path | str, state_class):
        """
        Load game state from storage.

        Args:
            path: Identifier for the state (file path or key)
            state_class: Class to instantiate (e.g., LorcanaState)

        Returns:
            Loaded state instance

        Raises:
            KeyError or FileNotFoundError: If state doesn't exist
        """
        pass

    @abstractmethod
    def save_state(self, state, path: Path | str, format_actions_fn=None):
        """
        Save game state to storage.

        Args:
            state: State object with graph, deck1_ids, deck2_ids attributes
            path: Identifier for where to save (file path or key)
            format_actions_fn: Optional function to format actions for navigation
        """
        pass

    @abstractmethod
    def state_exists(self, path: Path | str) -> bool:
        """
        Check if state exists in storage.

        Args:
            path: Identifier for the state

        Returns:
            True if state exists, False otherwise
        """
        pass
