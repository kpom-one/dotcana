"""
State-based effects.

Checks and resolves state-based effects after each action.
"""
from lib.core.graph import edges_by_label, get_node_attr
from lib.lorcana.cards import get_willpower
from lib.lorcana.helpers import get_card_data, get_player_zone


def check_state_based_effects(state) -> None:
    """
    Check and resolve state-based effects.

    Currently handles:
    - Banish characters with damage >= willpower
    """
    check_and_banish_damaged_characters(state)


def check_and_banish_damaged_characters(state) -> None:
    """Check all characters in play and banish those with lethal damage."""
    # Find all play zones
    play_zones = [
        node for node in state.graph.nodes()
        if get_node_attr(state.graph, node, 'kind', '') == 'play'
    ]

    cards_to_banish = []

    for play_zone in play_zones:
        # Find cards IN this play zone
        cards_in_play = [u for u, v, _ in edges_by_label(state.graph, "IN") if v == play_zone]

        for card_node in cards_in_play:
            card_data = get_card_data(state.graph, card_node)

            # Only check characters
            if card_data['type'] != 'Character':
                continue

            # Only check if card has damage
            damage = int(get_node_attr(state.graph, card_node, 'damage', '0'))
            if damage == 0:
                continue

            # Check damage vs willpower
            willpower = get_willpower(state, card_node)

            if damage >= willpower:
                cards_to_banish.append(card_node)

    # Banish all marked cards
    for card_node in cards_to_banish:
        # Find which zone this card is in (via IN edge)
        in_edges = [v for u, v, _ in edges_by_label(state.graph, "IN") if u == card_node]
        if in_edges:
            current_zone = in_edges[0]
            # Extract player from zone name (e.g., "z.p1.play" -> "p1")
            player = current_zone.split('.')[1]
            discard_zone = get_player_zone(player, 'discard')

            state.move_card(card_node, discard_zone)
