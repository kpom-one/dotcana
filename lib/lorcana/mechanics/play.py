"""
Play card mechanic.

Compute when cards can be played, and execute the play action.
"""
import networkx as nx
from lib.core.graph import edges_by_label, get_node_attr
from lib.lorcana.helpers import ActionEdge, get_game_context, get_card_data


def compute_can_play(G: nx.MultiDiGraph) -> list[ActionEdge]:
    """Return CAN_PLAY edges for playable cards in current player's hand."""
    result = []

    # Get game context
    ctx = get_game_context(G)
    if not ctx:
        return result

    # Get ink_available
    ink_available = int(get_node_attr(G, ctx['player'], 'ink_available', 0))

    # Find cards IN hand
    cards_in_hand = [u for u, v, _ in edges_by_label(G, "IN") if v == ctx['hand_zone']]

    # Check each card for playability
    for card_node in cards_in_hand:
        card_data = get_card_data(G, card_node)
        cost = card_data.get('cost', 0)

        if ink_available >= cost:
            destination = ctx['discard_zone'] if card_data['type'] == "Action" else ctx['play_zone']
            result.append(ActionEdge(
                src=card_node,
                dst=destination,
                action_type="CAN_PLAY",
                description=f"play:{card_node}"
            ))

    return result


def execute_play(state, from_node: str, to_node: str) -> None:
    """Execute play action: move card to play, spend ink, track entered_play turn."""
    # Move card from hand to play/discard
    state.move_card(from_node, to_node)

    # Get card data and game context
    card_data = get_card_data(state.graph, from_node)
    ctx = get_game_context(state.graph)

    # Spend ink
    cost = card_data['cost']
    ink_available = int(get_node_attr(state.graph, ctx['player'], 'ink_available', 0))
    state.graph.nodes[ctx['player']]['ink_available'] = str(ink_available - cost)

    # If card entered play zone (not discard), track the turn
    zone_kind = get_node_attr(state.graph, to_node, 'kind', '')
    if zone_kind == 'play':
        state.graph.nodes[from_node]['entered_play'] = str(ctx['current_turn'])
        state.graph.nodes[from_node]['exerted'] = '0'


