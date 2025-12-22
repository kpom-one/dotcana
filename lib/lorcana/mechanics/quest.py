"""
Quest mechanic.

Compute when characters can quest, and execute the quest action.
"""
import networkx as nx
from lib.core.graph import edges_by_label, get_node_attr
from lib.lorcana.cards import get_card_db


def compute_can_quest(G: nx.MultiDiGraph) -> list[tuple[str, str, str]]:
    """Return CAN_QUEST edges for characters that can quest."""
    result = []

    # Get current player
    edges = edges_by_label(G, "CURRENT_TURN")
    if not edges:
        return result
    game, player, _ = edges[0]

    # Get current turn
    current_turn = int(get_node_attr(G, 'game', 'turn', 0))

    # Get play zone
    play_zone = f"z.{player}.play"

    # Find cards IN play
    cards_in_play = [u for u, v, _ in edges_by_label(G, "IN") if v == play_zone]

    # Check each card for quest eligibility
    card_db = get_card_db()
    for card_node in cards_in_play:
        # Get card data
        card_name = get_node_attr(G, card_node, 'label')
        card_data = card_db.get(card_name)

        # Only characters can quest
        if not card_data or card_data.get('type') != 'Character':
            continue

        # Must have lore to quest
        if card_data.get('lore', 0) <= 0:
            continue

        # Check if tapped
        tapped = get_node_attr(G, card_node, 'tapped', '0')
        if tapped == '1':
            continue

        # Check if entered play this turn (summoning sickness)
        entered_play = int(get_node_attr(G, card_node, 'entered_play', '-1'))
        if entered_play == current_turn:
            continue

        result.append((card_node, player, "CAN_QUEST"))

    return result


def execute_quest(state, from_node: str, to_node: str) -> None:
    """Execute quest action: tap card, add lore to player."""
    # Tap the card
    state.graph.nodes[from_node]['tapped'] = '1'

    # Get card data
    card_name = get_node_attr(state.graph, from_node, 'label')
    card_db = get_card_db()
    card_data = card_db.get(card_name)

    if card_data:
        lore_value = card_data.get('lore', 0)
        # Add lore to player
        player = to_node
        current_lore = int(get_node_attr(state.graph, player, 'lore', 0))
        state.graph.nodes[player]['lore'] = str(current_lore + lore_value)
