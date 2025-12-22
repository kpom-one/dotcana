"""
Card database singleton - loaded once, reused everywhere.
"""
import json
from lib.lorcana.deck import normalize_card_name

_CARD_DB = None


def get_card_db() -> dict:
    """
    Get card database indexed by normalized name (lazy loaded singleton).

    Different printings of the same card may exist with different IDs,
    but we just pick the first match since stats/abilities are identical.

    Returns:
        dict mapping normalized_card_name -> card data
    """
    global _CARD_DB
    if _CARD_DB is None:
        with open("data/cards.json") as f:
            data = json.load(f)

        _CARD_DB = {}
        for card in data["cards"]:
            normalized = normalize_card_name(card["fullName"])
            # First match wins (different printings don't matter)
            if normalized not in _CARD_DB:
                _CARD_DB[normalized] = card

    return _CARD_DB
