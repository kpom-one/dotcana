"""
Graph I/O and query utilities.

DESIGN NOTE: Asymmetry between getters and setters
--------------------------------------------------
We provide query helpers but NOT mutation helpers. Why?

Getters need transformation:
- pydot adds quotes when loading DOT: node['type'] = '"Player"'
- We want clean strings: 'Player'
- Helpers abstract quote-stripping and common filtering patterns

Setters don't need transformation:
- We write clean values: node['lore'] = '5'
- pydot adds quotes when saving (we don't care)
- Direct graph access is fine: G.nodes[n]['attr'] = value

If you're writing game logic, use graph mutations directly.
If you're reading graph state, use the helpers below.
"""
import networkx as nx
from pathlib import Path


# ========== I/O Functions ==========

# File naming conventions
GAME_FILE = "game.dot"
DECK1_SOURCE = "deck1.txt"
DECK2_SOURCE = "deck2.txt"

# Internal file naming (not exported)
_DECK1_FILE = "deck1.dek"
_DECK2_FILE = "deck2.dek"


def load_dot(path: str | Path) -> nx.MultiDiGraph:
    """Load a DOT file into a networkx MultiDiGraph."""
    G = nx.drawing.nx_pydot.read_dot(str(path))
    return G


def save_dot(G: nx.MultiDiGraph, path: str | Path) -> None:
    """Save a networkx graph to DOT format."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    nx.drawing.nx_pydot.write_dot(G, str(path))


def get_node_attr(G: nx.MultiDiGraph, node: str, attr: str, default=None):
    """Get a node attribute, stripping quotes if present."""
    val = G.nodes[node].get(attr, default)
    if isinstance(val, str):
        val = val.strip('"')
    return val


def nodes_by_type(G: nx.MultiDiGraph, node_type: str) -> list[str]:
    """Get all nodes of a given type."""
    return [n for n in G.nodes() if get_node_attr(G, n, "type") == node_type]


def edges_by_label(G: nx.MultiDiGraph, label: str) -> list[tuple[str, str, str]]:
    """Get all edges with a given label. Returns list of (u, v, key)."""
    result = []
    for u, v, key, data in G.edges(keys=True, data=True):
        edge_label = data.get("label", key)
        if isinstance(edge_label, str):
            edge_label = edge_label.strip('"')
        if edge_label == label:
            result.append((u, v, key))
    return result


def can_edges(G: nx.MultiDiGraph) -> list[tuple[str, str, str, str]]:
    """Get all action edges. Returns list of (u, v, key, action_type)."""
    result = []
    for u, v, key, data in G.edges(keys=True, data=True):
        action_type = data.get("action_type")
        if action_type:
            if isinstance(action_type, str):
                action_type = action_type.strip('"')
            result.append((u, v, key, action_type))
    return result


def load_deck(base_path: str | Path, player: int) -> list[str]:
    """
    Load deck card IDs for a player.

    Args:
        base_path: Directory containing deck files
        player: Player number (1 or 2)

    Returns:
        List of card IDs, or empty list if file doesn't exist
    """
    deck_file = _DECK1_FILE if player == 1 else _DECK2_FILE
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
    deck_file = _DECK1_FILE if player == 1 else _DECK2_FILE
    path = Path(base_path) / deck_file
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        for card_id in deck_ids:
            f.write(f"{card_id}\n")
