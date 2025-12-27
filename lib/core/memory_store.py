"""
In-memory state storage.

Fast dict-based storage for game states. No filesystem I/O.
Useful for performance-critical operations like game tree search.
"""
from pathlib import Path
from copy import deepcopy
from lib.core.store import StateStore
from lib.core.navigation import write_path_file, write_actions_file


class MemoryStore(StateStore):
    """
    In-memory state storage using dictionaries.

    Stores states in memory without writing to disk.
    Much faster than FileStore for batch operations.
    """

    def __init__(self):
        """Initialize empty in-memory storage."""
        # Storage: path -> (graph, deck1_ids, deck2_ids)
        self._states = {}
        # Optional: path -> formatted_actions (for navigation)
        self._actions = {}

    def load_state(self, path: Path | str, state_class):
        """
        Load game state from memory.

        Args:
            path: Key for the state
            state_class: Class to instantiate (e.g., LorcanaState)

        Returns:
            Loaded state instance with deep-copied graph

        Raises:
            KeyError: If state doesn't exist
        """
        path = str(path)  # Normalize to string key

        if path not in self._states:
            raise KeyError(f"State not found: {path}")

        graph, deck1_ids, deck2_ids = self._states[path]

        # Deep copy graph to prevent mutation of stored state
        # Deck lists are copied in state constructor
        return state_class(deepcopy(graph), list(deck1_ids), list(deck2_ids))

    def save_state(self, state, path: Path | str, format_actions_fn=None):
        """
        Save game state to memory.

        Args:
            state: State object with graph, deck1_ids, deck2_ids attributes
            path: Key for where to save
            format_actions_fn: Optional function to format actions for navigation
        """
        path = str(path)  # Normalize to string key

        # Store deep copy to prevent external mutations
        self._states[path] = (
            deepcopy(state.graph),
            list(state.deck1_ids),
            list(state.deck2_ids)
        )

        # Store formatted actions if provided
        if format_actions_fn:
            self._actions[path] = format_actions_fn(state.graph)

    def state_exists(self, path: Path | str) -> bool:
        """
        Check if state exists in memory.

        Args:
            path: Key for the state

        Returns:
            True if state exists, False otherwise
        """
        return str(path) in self._states

    def get_actions(self, path: Path | str) -> list[dict]:
        """
        Get formatted actions for a state (if available).

        Args:
            path: Key for the state

        Returns:
            List of action dicts with 'id' and 'description' keys
        """
        return self._actions.get(str(path), [])

    def clear(self):
        """Clear all stored states from memory."""
        self._states.clear()
        self._actions.clear()
