"""
Action utilities - ID generation and action-related helpers.
"""
import hashlib


def make_action_id(action_type: str, from_node: str, to_node: str) -> str:
    """
    Generate action directory name.

    Format: [prefix][xx]
    - prefix: e=end, i=ink, p=play, q=quest, c=challenge, a=activate
    - xx: 2-char hex hash of from_node:to_node

    Examples:
        - e3a (end turn)
        - i7f (ink:p1.tinker_bell_giant_fairy.a)
        - p2c (play:p1.tipo_growing_son.a)
    """
    prefixes = {
        "CAN_PASS": "e",
        "CAN_INK": "i",
        "CAN_PLAY": "p",
        "CAN_QUEST": "q",
        "CAN_CHALLENGE": "c",
        "CAN_ACTIVATE": "a",
    }

    prefix = prefixes.get(action_type, "x")
    edge_str = f"{from_node}:{to_node}"
    hash_val = hashlib.md5(edge_str.encode()).hexdigest()[:2]

    return f"{prefix}{hash_val}"
