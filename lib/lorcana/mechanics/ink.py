"""
Ink card mechanic.

Compute when cards can be inked, and execute the ink action.
"""
import networkx as nx
from lib.core.graph import edges_by_label, get_node_attr
from lib.lorcana.cards import get_card_db


def compute_can_ink(G: nx.MultiDiGraph) -> list[tuple[str, str, str, str]]:
    """Return CAN_INK edges for inkable cards in current player's hand."""
    result = []

    # Get current player from CURRENT_TURN edge
    edges = edges_by_label(G, "CURRENT_TURN")
    if not edges:
        return result
    game, player, _ = edges[0]  # Game -> Player

    # Check ink_drops > 0
    ink_drops = int(get_node_attr(G, player, 'ink_drops', 0))
    if ink_drops <= 0:
        return result

    # Get zones
    hand_zone = f"z.{player}.hand"
    inkwell_zone = f"z.{player}.ink"

    # Find cards IN hand
    cards_in_hand = [u for u, v, _ in edges_by_label(G, "IN") if v == hand_zone]

    # Check each card for inkwell property
    card_db = get_card_db()
    for card_node in cards_in_hand:
        card_name = get_node_attr(G, card_node, 'label')
        card_data = card_db.get(card_name)

        if card_data and card_data.get('inkwell'):
            result.append((card_node, inkwell_zone, "CAN_INK", f"ink:{card_node}"))

    return result


def execute_ink(state, from_node: str, to_node: str) -> None:
    """Execute ink action: move card to inkwell, update ink tracking."""
    # Move card from hand to inkwell
    state.move_card(from_node, to_node)

    # Update ink for current player
    edges = edges_by_label(state.graph, "CURRENT_TURN")
    if edges:
        game, player, _ = edges[0]
        # Decrement ink_drops
        ink_drops = int(get_node_attr(state.graph, player, 'ink_drops', 1))
        state.graph.nodes[player]['ink_drops'] = str(ink_drops - 1)

        # Increment ink_total and ink_available
        ink_total = int(get_node_attr(state.graph, player, 'ink_total', 0))
        state.graph.nodes[player]['ink_total'] = str(ink_total + 1)
        ink_available = int(get_node_attr(state.graph, player, 'ink_available', 0))
        state.graph.nodes[player]['ink_available'] = str(ink_available + 1)
