"""
Helper functions for Lorcana game logic.

Common patterns used across mechanics.
"""
from typing import NamedTuple
from lib.core.graph import edges_by_label, get_node_attr
from lib.lorcana.cards import get_card_db


class ActionEdge(NamedTuple):
    """
    Represents a potential action in the game.

    Used by compute_can_* functions to return available actions.
    """
    src: str          # Source node (e.g., card performing action)
    dst: str          # Destination node (e.g., target or zone)
    action_type: str  # Type of action (CAN_CHALLENGE, CAN_QUEST, etc.)
    description: str  # Human-readable description for UI


def get_player_zone(player: str, zone_kind: str) -> str:
    """
    Get zone node ID for a player.

    Args:
        player: Player ID ("p1" or "p2")
        zone_kind: Zone type ("hand", "play", "discard", "ink", "deck")

    Returns:
        Zone node ID (e.g., "z.p1.discard")
    """
    return f"z.{player}.{zone_kind}"


def get_game_context(G):
    """
    Get common game state information.

    Returns dict with current player, opponent, turn, and zones.
    Returns None if no current player (shouldn't happen in valid game state).

    Returns:
        dict with keys:
            - player: Current player ID ("p1" or "p2")
            - opponent: Opponent player ID
            - current_turn: Turn number (int)
            - play_zone: Current player's play zone
            - opponent_play_zone: Opponent's play zone
            - hand_zone: Current player's hand zone
            - ink_zone: Current player's ink zone
            - discard_zone: Current player's discard zone
    """
    edges = edges_by_label(G, "CURRENT_TURN")
    if not edges:
        return None

    game, player, _ = edges[0]
    opponent = "p2" if player == "p1" else "p1"
    current_turn = int(get_node_attr(G, 'game', 'turn', 0))

    return {
        'player': player,
        'opponent': opponent,
        'current_turn': current_turn,
        'play_zone': get_player_zone(player, 'play'),
        'opponent_play_zone': get_player_zone(opponent, 'play'),
        'hand_zone': get_player_zone(player, 'hand'),
        'ink_zone': get_player_zone(player, 'ink'),
        'discard_zone': get_player_zone(player, 'discard'),
    }


def get_card_data(G, card_node: str):
    """
    Get card database entry for a card node.

    Args:
        G: Game graph
        card_node: Card node ID (e.g., "p1.tinker_bell_giant_fairy.a")

    Returns:
        Card data dict from database

    Raises:
        KeyError: If card not found in database (data is broken)
    """
    card_db = get_card_db()
    card_name = get_node_attr(G, card_node, 'label')
    return card_db[card_name]  # Fail fast if missing
