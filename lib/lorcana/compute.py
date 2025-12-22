"""
Compute legal actions (CAN_* edges) from Lorcana game state.
"""
import networkx as nx
from lib.core.graph import nodes_by_type, get_node_attr, edges_by_label
from lib.lorcana.cards import get_card_db


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
    # Get current player from CURRENT_TURN edge
    edges = edges_by_label(G, "CURRENT_TURN")
    if not edges:
        return
    game, player, _ = edges[0]  # Game -> Player

    # Check ink_drops > 0
    ink_drops = int(get_node_attr(G, player, 'ink_drops', 0))
    if ink_drops <= 0:
        return

    # Get zones
    hand_zone = f"z.{player}.hand"
    inkwell_zone = f"z.{player}.ink"

    # Find cards IN hand
    cards_in_hand = [u for u, v, _ in edges_by_label(G, "IN") if v == hand_zone]

    # Check each card for inkwell property
    card_db = get_card_db()
    for card_node in cards_in_hand:
        card_id = int(get_node_attr(G, card_node, 'card_id'))

        # Find card by ID in database
        card_data = None
        for card in card_db.values():
            if card['id'] == card_id:
                card_data = card
                break

        if card_data and card_data.get('inkwell'):
            add_can_edge(G, card_node, inkwell_zone, "CAN_INK")


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
