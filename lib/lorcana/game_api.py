"""
Python API for playing Lorcana games in-memory.

Provides high-level game operations without filesystem I/O.
Uses MemoryStore for fast state management.
"""
import random
from pathlib import Path
from lib.core.store import StateStore
from lib.core.memory_store import MemoryStore
from lib.core.file_store import FileStore
from lib.core.graph import can_edges, get_node_attr
from lib.lorcana.state import LorcanaState
from lib.lorcana.execute import execute_action
from lib.lorcana.compute import compute_all
from lib.core.navigation import format_actions


class GameSession:
    """
    In-memory game session.

    Manages game state and provides clean API for playing.
    No filesystem I/O - all operations in memory.
    """

    def __init__(self, initial_state: LorcanaState, store: StateStore = None):
        """
        Create game session from initial state.

        Args:
            initial_state: Starting game state
            store: Storage backend (defaults to MemoryStore)
        """
        self.store = store or MemoryStore()
        self.root_key = "root"
        self.current_key = self.root_key

        # Save initial state
        self.store.save_state(initial_state, self.root_key, format_actions_fn=format_actions)

    @classmethod
    def from_file(cls, path: Path | str, store: StateStore = None):
        """
        Create session from existing file-based state.

        Args:
            path: Path to state directory
            store: Storage backend (defaults to MemoryStore)

        Returns:
            GameSession instance
        """
        file_store = FileStore()
        state = file_store.load_state(path, LorcanaState)
        return cls(state, store=store)

    def get_state(self) -> LorcanaState:
        """Get current game state."""
        return self.store.load_state(self.current_key, LorcanaState)

    def get_actions(self) -> list[dict]:
        """
        Get available actions from current state.

        Returns:
            List of action dicts with 'id' and 'description' keys
        """
        state = self.get_state()
        return format_actions(state.graph)

    def apply_action(self, action_id: str) -> bool:
        """
        Apply action by ID, advancing to new state.

        Args:
            action_id: Action ID to apply (e.g., "0", "1", "2")

        Returns:
            True if action was applied, False if action not found

        Mutates: Updates current_key to point to new state
        """
        state = self.get_state()

        # Find matching action
        for u, v, key, action_type, edge_action_id in can_edges(state.graph):
            if edge_action_id == action_id:
                # Execute action (mutates state)
                execute_action(state, action_type, u, v)

                # Save to new key
                new_key = f"{self.current_key}/{action_id}"
                self.store.save_state(state, new_key, format_actions_fn=format_actions)

                # Update current position
                self.current_key = new_key
                return True

        return False

    def is_game_over(self) -> bool:
        """Check if current game is over."""
        state = self.get_state()
        return get_node_attr(state.graph, 'game', 'game_over', '0') == '1'

    def get_winner(self) -> str | None:
        """
        Get winner if game is over.

        Returns:
            Winner player node ("p1" or "p2"), or None if no winner yet
        """
        if not self.is_game_over():
            return None
        state = self.get_state()
        return get_node_attr(state.graph, 'game', 'winner', None)

    def get_path(self) -> str:
        """Get current path from root."""
        if self.current_key == self.root_key:
            return ""
        return self.current_key[len(self.root_key):]

    def reset(self):
        """Reset to initial state."""
        self.current_key = self.root_key

    def play_random_action(self, prefer_non_end: bool = True) -> bool:
        """
        Play a random action from current state.

        Args:
            prefer_non_end: If True, only choose 'end' if no other actions available

        Returns:
            True if action was played, False if no actions available
        """
        actions = self.get_actions()
        if not actions:
            return False

        # Filter non-end actions if preference set
        if prefer_non_end:
            non_end = [a for a in actions if a['description'] != 'end']
            if non_end:
                actions = non_end

        # Pick random action
        action = random.choice(actions)
        return self.apply_action(action['id'])

    def play_until_game_over(self, prefer_non_end: bool = True, max_actions: int = 1000) -> str:
        """
        Play random actions until game ends.

        Args:
            prefer_non_end: Prefer non-end actions when available
            max_actions: Maximum actions to prevent infinite loops

        Returns:
            Path to final state (e.g., "/0/3/1/2")
        """
        for _ in range(max_actions):
            if self.is_game_over():
                break
            if not self.play_random_action(prefer_non_end):
                break

        return self.get_path()
