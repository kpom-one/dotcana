"""
File-based state storage using DOT files.

Persists game states to filesystem as .dot files and .dek files.
"""
from pathlib import Path
from lib.core.store import StateStore
from lib.core.graph import load_dot, save_dot
from lib.core.navigation import write_path_file, write_actions_file

# Deck file names
_DEK1_FILE = "deck1.dek"
_DEK2_FILE = "deck2.dek"
_GAME_FILE = "game.dot"


class FileStore(StateStore):
    """
    File-based state storage.

    Saves states as DOT graphs and deck lists to filesystem.
    """

    def load_state(self, path: Path | str, state_class):
        """
        Load game state from filesystem.

        Args:
            path: Directory containing game.dot and deck files
            state_class: Class to instantiate (e.g., LorcanaState)

        Returns:
            Loaded state instance

        Raises:
            FileNotFoundError: If game.dot doesn't exist
        """
        path = Path(path)
        game_file = path / _GAME_FILE

        if not game_file.exists():
            raise FileNotFoundError(f"No {_GAME_FILE} at {path}")

        graph = load_dot(game_file)
        deck1_ids = self._load_deck(path, player=1)
        deck2_ids = self._load_deck(path, player=2)

        return state_class(graph, deck1_ids, deck2_ids)

    def save_state(self, state, path: Path | str, format_actions_fn=None):
        """
        Save game state to filesystem.

        Args:
            state: State object with graph, deck1_ids, deck2_ids attributes
            path: Directory to save to
            format_actions_fn: Optional function to format actions for actions.txt
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save core state
        save_dot(state.graph, path / _GAME_FILE)
        self._save_deck(state.deck1_ids, path, player=1)
        self._save_deck(state.deck2_ids, path, player=2)

        # Write navigation files if formatter provided
        if format_actions_fn:
            write_path_file(path)
            actions = format_actions_fn(state.graph)
            write_actions_file(path, actions)

    def state_exists(self, path: Path | str) -> bool:
        """
        Check if state exists on filesystem.

        Args:
            path: Directory that should contain state

        Returns:
            True if game.dot exists, False otherwise
        """
        path = Path(path)
        return (path / _GAME_FILE).exists()

    # ========== Internal Helpers ==========

    def _load_deck(self, base_path: Path, player: int) -> list[str]:
        """Load deck card IDs for a player."""
        deck_file = _DEK1_FILE if player == 1 else _DEK2_FILE
        path = base_path / deck_file

        if not path.exists():
            return []

        with open(path) as f:
            return [line.strip() for line in f if line.strip()]

    def _save_deck(self, deck_ids: list[str], base_path: Path, player: int) -> None:
        """Save deck card IDs for a player."""
        deck_file = _DEK1_FILE if player == 1 else _DEK2_FILE
        path = base_path / deck_file

        with open(path, 'w') as f:
            for card_id in deck_ids:
                f.write(f"{card_id}\n")
