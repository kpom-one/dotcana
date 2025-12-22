"""
Lorcana deck operations - parsing, normalization, and shuffling.
"""
import random
import re
from pathlib import Path


def normalize_card_name(name: str) -> str:
    """Convert 'Tinker Bell - Giant Fairy' to 'tinker_bell_giant_fairy'."""
    return name.lower().replace(' - ', '_').replace(' ', '_').replace('-', '_')


def build_shuffled_deck(deck_txt: Path, hand_indices: list[int], shuffle_seed: str) -> list[str]:
    """
    Build shuffled deck from decklist: hand cards first, then shuffled remainder.

    Args:
        deck_txt: Path to decklist.txt (format: "4 Tinker Bell - Giant Fairy")
        hand_indices: 7 indices selecting starting hand from unique cards
        shuffle_seed: Seed string for deterministic shuffling

    Returns:
        List of 60 card IDs: [hand cards (7), shuffled remainder (53)]
        Card ID format: normalized_name.[a|b|c|d]
        Example: ["tinker_bell_giant_fairy.a", "tipo_growing_son.b", ...]
    """
    # Parse decklist: "4 Tinker Bell - Giant Fairy" -> (4, "Tinker Bell - Giant Fairy")
    cards = []  # [(count, name), ...]
    with open(deck_txt) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.match(r"(\d+)\s+(.+)", line)
            if match:
                cards.append((int(match.group(1)), match.group(2).strip()))

    # Build unique card list (for hand index lookup)
    unique_cards = [name for count, name in cards]

    # Expand to full deck with normalized IDs and copy suffixes
    card_map = {}  # card_name -> [card_ids]
    for count, name in cards:
        base = normalize_card_name(name)
        card_map[name] = []
        for i in range(count):
            suffix = chr(ord('a') + i)  # a, b, c, d (supports up to 4-of)
            card_map[name].append(f"{base}.{suffix}")

    # Extract hand cards (first 7)
    hand_cards = []
    for idx in hand_indices:
        if idx >= len(unique_cards):
            raise ValueError(f"Hand index {idx} out of range (deck has {len(unique_cards)} unique cards)")

        card_name = unique_cards[idx]
        if not card_map[card_name]:
            raise ValueError(f"Not enough copies of '{card_name}' for hand")

        hand_cards.append(card_map[card_name].pop(0))

    # Collect remaining 53 cards
    remaining = [card_id for ids in card_map.values() for card_id in ids]

    # Shuffle remainder deterministically
    rng = random.Random(shuffle_seed)
    rng.shuffle(remaining)

    # Return hand on top, shuffled remainder below
    return hand_cards + remaining
