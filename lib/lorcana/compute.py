"""
Compute legal actions (CAN_* edges) from Lorcana game state.

Orchestrates mechanics to compute all legal actions.
"""
import networkx as nx
from lib.lorcana.mechanics.end import compute_can_pass
from lib.lorcana.mechanics.ink import compute_can_ink
from lib.lorcana.mechanics.play import compute_can_play
from lib.lorcana.mechanics.quest import compute_can_quest


def clear_can_edges(G: nx.MultiDiGraph) -> None:
    """Remove all existing action edges from the graph."""
    to_remove = []
    for u, v, key, data in G.edges(keys=True, data=True):
        if data.get("action_type"):
            to_remove.append((u, v, key))
    for edge in to_remove:
        G.remove_edge(*edge)


def add_can_edge(G: nx.MultiDiGraph, src: str, dst: str, action_type: str, action_id: str) -> str:
    """Add an action edge with sequential action_id."""
    key = G.add_edge(src, dst, action_type=action_type, action_id=action_id)
    return key


def compute_all(G: nx.MultiDiGraph) -> None:
    """Recompute all CAN_* edges from current state."""
    clear_can_edges(G)

    # Collect edges from all mechanics
    edges_to_add = []
    edges_to_add.extend(compute_can_pass(G))
    edges_to_add.extend(compute_can_ink(G))
    edges_to_add.extend(compute_can_play(G))
    edges_to_add.extend(compute_can_quest(G))
    # TODO: Add other mechanics (challenge, activate)

    # Sort deterministically and assign sequential action IDs
    sorted_edges = sorted(edges_to_add, key=lambda e: (e[2], e[0], e[1]))  # (action_type, from, to)

    # Add edges with sequential action_ids
    for idx, (src, dst, action_type) in enumerate(sorted_edges):
        add_can_edge(G, src, dst, action_type, action_id=str(idx))
