"""
State persistence - loading and saving game states to filesystem.

Handles all filesystem I/O for game states. Works with any state class
that has graph + deck attributes.
"""
from pathlib import Path
from lib.core.graph import load_dot, save_dot
from lib.core.navigation import write_path_file, write_actions_file

# Deck file names
_DEK1_FILE = "deck1.dek"
_DEK2_FILE = "deck2.dek"
_GAME_FILE = "game.dot"


def load_deck(base_path: str | Path, player: int) -> list[str]:
    """
    Load deck card IDs for a player.

    Args:
        base_path: Directory containing deck files
        player: Player number (1 or 2)

    Returns:
        List of card IDs, or empty list if file doesn't exist
    """
    deck_file = _DEK1_FILE if player == 1 else _DEK2_FILE
    path = Path(base_path) / deck_file

    if not path.exists():
        return []

    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def save_deck(deck_ids: list[str], base_path: str | Path, player: int) -> None:
    """
    Save deck card IDs for a player.

    Args:
        deck_ids: List of card IDs to save
        base_path: Directory to save deck file in
        player: Player number (1 or 2)
    """
    # TODO: Premature optimization opportunity: Symlink if it's the same decklist as before
    deck_file = _DEK1_FILE if player == 1 else _DEK2_FILE
    path = Path(base_path) / deck_file
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        for card_id in deck_ids:
            f.write(f"{card_id}\n")


def load_state(path: Path | str, state_class):
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
    deck1_ids = load_deck(path, player=1)
    deck2_ids = load_deck(path, player=2)

    return state_class(graph, deck1_ids, deck2_ids)


def save_state(state, path: Path | str, format_actions_fn=None):
    """
    Save game state to filesystem.

    Args:
        state: State object with graph, deck1_ids, deck2_ids attributes
        path: Directory to save to
        format_actions_fn: Optional function to format actions for actions.txt
                          If None, only saves graph and decks (no navigation files)
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    # Save core state
    save_dot(state.graph, path / _GAME_FILE)
    save_deck(state.deck1_ids, path, player=1)
    save_deck(state.deck2_ids, path, player=2)

    # Write navigation files if formatter provided
    if format_actions_fn:
        write_path_file(path)
        actions = format_actions_fn(state.graph)
        write_actions_file(path, actions)
