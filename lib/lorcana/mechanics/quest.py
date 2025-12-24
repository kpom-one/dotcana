"""
Quest mechanic.

Compute when characters can quest, and execute the quest action.
"""
import networkx as nx
from lib.core.graph import edges_by_label, get_node_attr
from lib.lorcana.helpers import ActionEdge, get_game_context, get_card_data


def compute_can_quest(G: nx.MultiDiGraph) -> list[ActionEdge]:
    """Return CAN_QUEST edges for characters that can quest."""
    result = []

    # Get game context
    ctx = get_game_context(G)
    if not ctx:
        return result

    # Find cards IN play
    cards_in_play = [u for u, v, _ in edges_by_label(G, "IN") if v == ctx['play_zone']]

    # Check each card for quest eligibility
    for card_node in cards_in_play:
        card_data = get_card_data(G, card_node)

        # Only characters can quest
        if card_data['type'] != 'Character':
            continue

        # Must have lore to quest
        if card_data.get('lore', 0) <= 0:
            continue

        # Must be ready (not tapped)
        if get_node_attr(G, card_node, 'tapped', '0') == '1':
            continue

        # Must be dry (entered play before this turn)
        entered_play = int(get_node_attr(G, card_node, 'entered_play', '-1'))
        if entered_play == ctx['current_turn']:
            continue

        result.append(ActionEdge(
            src=card_node,
            dst=ctx['player'],
            action_type="CAN_QUEST",
            description=f"quest:{card_node}"
        ))

    return result


def execute_quest(state, from_node: str, to_node: str) -> None:
    """Execute quest action: tap card, add lore to player."""
    # Tap the card
    state.graph.nodes[from_node]['tapped'] = '1'

    # Get lore value and add to player (checks win condition)
    card_data = get_card_data(state.graph, from_node)
    lore_value = card_data['lore']
    state.add_lore(to_node, lore_value)
