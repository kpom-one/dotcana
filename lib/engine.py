"""
Rules engine - orchestrates game state transitions.
"""
import networkx as nx
from pathlib import Path

from lib.graph import load_dot, save_dot, can_edges
from lib.compute import compute_all


def init_game(matchdir: str | Path) -> nx.MultiDiGraph:
    """
    Initialize a game from a matchup directory.

    Combines template.dot + deck1.dot + deck2.dot into initial game state.
    Cards start in decks (unshuffled - shuffle is an action).
    """
    matchdir = Path(matchdir)
    template_path = Path("data/template.dot")
    deck1 = matchdir / "deck1.dot"
    deck2 = matchdir / "deck2.dot"

    # Load template
    G = load_dot(template_path)

    # Merge deck cards into graph
    _merge_deck(G, deck1, deck_zone="Z_P1_DECK")
    _merge_deck(G, deck2, deck_zone="Z_P2_DECK")

    # Compute initial legal actions
    compute_all(G)

    return G


def _merge_deck(G: nx.MultiDiGraph, deck_path: Path, deck_zone: str) -> None:
    """Load a deck .dot file and merge cards into the main graph."""
    deck = load_dot(deck_path)

    position = 0
    for node, attrs in deck.nodes(data=True):
        G.add_node(node, **attrs)
        G.add_edge(node, deck_zone, label="IN", position=str(position))
        position += 1


def apply_action(G: nx.MultiDiGraph, action_id: str) -> nx.MultiDiGraph:
    """
    Apply an action to the game state.

    action_id corresponds to an edge key or can be matched to a CAN_* edge.
    """
    # For now, actions are identified by finding the CAN_* edge
    # In the future, action_id will map to a specific edge

    # TODO: Implement action dispatch based on action type
    # For now, just recompute (stub)

    compute_all(G)
    return G


def show_actions(G: nx.MultiDiGraph) -> list[dict]:
    """Return list of available actions."""
    actions = []
    for i, (u, v, key, action_type) in enumerate(can_edges(G)):
        # Generate a short action ID
        action_id = _make_action_id(i)
        actions.append({
            "id": action_id,
            "type": action_type,
            "from": u.strip('"'),
            "to": v.strip('"'),
            "key": key,
        })
    return actions


def _make_action_id(index: int) -> str:
    """Generate a 2-char base36 action ID."""
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if index < 36:
        return chars[index]
    else:
        return chars[index // 36] + chars[index % 36]
