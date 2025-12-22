"""
Play card mechanic.

Compute when cards can be played, and execute the play action.
"""
import networkx as nx
from lib.core.graph import edges_by_label, get_node_attr
from lib.lorcana.cards import get_card_db


def compute_can_play(G: nx.MultiDiGraph) -> list[tuple[str, str, str]]:
    """Return CAN_PLAY edges for playable cards in current player's hand."""
    result = []

    # Get current player
    edges = edges_by_label(G, "CURRENT_TURN")
    if not edges:
        return result
    game, player, _ = edges[0]

    # Get ink_available
    ink_available = int(get_node_attr(G, player, 'ink_available', 0))

    # Get zones
    hand_zone = f"z.{player}.hand"
    play_zone = f"z.{player}.play"
    discard_zone = f"z.{player}.discard"

    # Find cards IN hand
    cards_in_hand = [u for u, v, _ in edges_by_label(G, "IN") if v == hand_zone]

    # Check each card for playability
    card_db = get_card_db()
    for card_node in cards_in_hand:
        card_name = get_node_attr(G, card_node, 'label')
        card_data = card_db.get(card_name)

        if card_data:
            cost = card_data.get('cost', 0)
            if ink_available >= cost:
                destination = discard_zone if card_data.get('type', None) == "Action" else play_zone
                result.append((card_node, destination, "CAN_PLAY"))

    return result


def execute_play(state, from_node: str, to_node: str) -> None:
    """Execute play action: move card to play, spend ink, track entered_play turn."""
    # Move card from hand to play/discard
    state.move_card(from_node, to_node)

    # Get card data
    card_name = get_node_attr(state.graph, from_node, 'label')
    card_db = get_card_db()
    card_data = card_db.get(card_name)

    if card_data:
        cost = card_data.get('cost', 0)
        # Spend ink
        edges = edges_by_label(state.graph, "CURRENT_TURN")
        if edges:
            game, player, _ = edges[0]
            ink_available = int(get_node_attr(state.graph, player, 'ink_available', 0))
            state.graph.nodes[player]['ink_available'] = str(ink_available - cost)

            # If card entered play zone (not discard), track the turn
            zone_kind = get_node_attr(state.graph, to_node, 'kind', '')
            if zone_kind == 'play':
                current_turn = get_node_attr(state.graph, 'game', 'turn', '0')
                state.graph.nodes[from_node]['entered_play'] = current_turn
                state.graph.nodes[from_node]['tapped'] = '0'


