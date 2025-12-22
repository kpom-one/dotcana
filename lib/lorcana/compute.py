"""
Compute legal actions (CAN_* edges) from Lorcana game state.
"""
import networkx as nx
from lib.core.graph import nodes_by_type, get_node_attr, edges_by_label


def clear_can_edges(G: nx.MultiDiGraph) -> None:
    """Remove all existing action edges from the graph."""
    to_remove = []
    for u, v, key, data in G.edges(keys=True, data=True):
        if data.get("action_type"):
            to_remove.append((u, v, key))
    for edge in to_remove:
        G.remove_edge(*edge)


def add_can_edge(G: nx.MultiDiGraph, src: str, dst: str, action_type: str) -> str:
    """Add an action edge and return its key."""
    key = G.add_edge(src, dst, action_type=action_type)
    return key


def compute_can_pass(G: nx.MultiDiGraph) -> None:
    """Add CAN_PASS edge for current player."""
    edges = edges_by_label(G, "CURRENT_TURN")
    if edges:
        game, player, _ = edges[0]  # GAME -> Player
        add_can_edge(G, player, game, "CAN_PASS")


def compute_can_ink(G: nx.MultiDiGraph) -> None:
    """Add CAN_INK edges for inkable cards in current player's hand."""
    # TODO: Check ink_drops remaining, card is inkable
    # For now, stub - no ink actions
    pass


def compute_can_play(G: nx.MultiDiGraph) -> None:
    """Add CAN_PLAY edges for playable cards in current player's hand."""
    # TODO: Check ink available >= card cost
    # For now, stub - no play actions
    pass


def compute_can_quest(G: nx.MultiDiGraph) -> None:
    """Add CAN_QUEST edges for ready characters in play."""
    # TODO: Check card is Character, not exerted, been in play since turn start
    # For now, stub - no quest actions
    pass


def compute_can_challenge(G: nx.MultiDiGraph) -> None:
    """Add CAN_CHALLENGE edges for ready characters vs exerted opponents."""
    # TODO: Check challenger ready, target exerted
    # For now, stub - no challenge actions
    pass


def compute_can_activate(G: nx.MultiDiGraph) -> None:
    """Add CAN_ACTIVATE edges for cards with activated abilities."""
    # TODO: Check ability requirements met
    # For now, stub - no activate actions
    pass


def compute_all(G: nx.MultiDiGraph) -> None:
    """Recompute all CAN_* edges from current state."""
    clear_can_edges(G)

    compute_can_pass(G)
    compute_can_ink(G)
    compute_can_play(G)
    compute_can_quest(G)
    compute_can_challenge(G)
    compute_can_activate(G)
