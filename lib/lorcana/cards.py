"""
Card database singleton - loaded once, reused everywhere.
"""
import json

_CARD_DB = None


def get_card_db() -> dict:
    """
    Get card database (lazy loaded singleton).

    Returns:
        dict mapping card full name -> card data
    """
    global _CARD_DB
    if _CARD_DB is None:
        with open("data/cards.json") as f:
            data = json.load(f)
        _CARD_DB = {card["fullName"]: card for card in data["cards"]}
    return _CARD_DB
