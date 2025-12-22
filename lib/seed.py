"""
Seed parsing and deck shuffling.

Seed format: xxxxxxx.xxxxxxx.xx
- First 7 chars (0-9a-z): P1's starting hand (indices into deck1.txt)
- Second 7 chars (0-9a-z): P2's starting hand (indices into deck2.txt)
- Last 2 chars: RNG suffix for shuffling remainder

Character mapping: 0-9 → 0-9, a-z → 10-35
"""
import random
import re
from pathlib import Path


def parse_seed(seed: str) -> dict | None:
    """
    Parse seed format into hand specs.

    Returns:
        dict with 'p1_hand', 'p2_hand' (lists of indices), 'shuffle_seed'
        None if invalid format
    """
    parts = seed.split('.')
    if len(parts) != 3:
        return None

    p1_spec, p2_spec, suffix = parts
    if len(p1_spec) != 7 or len(p2_spec) != 7 or len(suffix) != 2:
        return None

    p1_hand = [_char_to_index(c) for c in p1_spec]
    p2_hand = [_char_to_index(c) for c in p2_spec]

    if None in p1_hand or None in p2_hand:
        return None

    return {
        'p1_hand': p1_hand,
        'p2_hand': p2_hand,
        'shuffle_seed': seed
    }


def generate_random_seed() -> str:
    """
    Generate random hand-spec seed.

    Uses indices 0-16 (17 unique cards) to fit typical Lorcana decks.
    """
    def random_chars(n):
        return ''.join(_index_to_char(random.randint(0, 16)) for _ in range(n))

    return f"{random_chars(7)}.{random_chars(7)}.{random_chars(2)}"


def normalize_card_name(name: str) -> str:
    """Convert 'Tinker Bell - Giant Fairy' to 'tinker_bell_giant_fairy'."""
    return name.lower().replace(' - ', '_').replace(' ', '_').replace('-', '_')


def create_deck_file(deck_txt: Path, hand_indices: list[int], shuffle_seed: str) -> list[str]:
    """
    Build shuffled deck: hand cards on top, shuffled remainder.

    Args:
        deck_txt: Original decklist.txt
        hand_indices: 7 indices for starting hand
        shuffle_seed: Seed for shuffling remainder

    Returns:
        List of card IDs: [hand cards (7), shuffled remainder (53)]
        IDs format: normalized_name.[a|b|c|d]
    """
    # Parse decklist
    cards = []  # [(count, name), ...]
    with open(deck_txt) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.match(r"(\d+)\s+(.+)", line)
            if match:
                cards.append((int(match.group(1)), match.group(2).strip()))

    # Build unique card list (for hand indices)
    unique_cards = [name for count, name in cards]

    # Expand to full deck with normalized IDs
    card_map = {}  # card_name -> [card_ids]
    for count, name in cards:
        base = normalize_card_name(name)
        card_map[name] = []
        for i in range(count):
            suffix = chr(ord('a') + i)  # a, b, c, d
            card_map[name].append(f"{base}.{suffix}")

    # Extract hand cards
    hand_cards = []
    for idx in hand_indices:
        if idx >= len(unique_cards):
            raise ValueError(f"Hand index {idx} out of range (deck has {len(unique_cards)} unique cards)")

        card_name = unique_cards[idx]
        if not card_map[card_name]:
            raise ValueError(f"Not enough copies of '{card_name}' for hand")

        hand_cards.append(card_map[card_name].pop(0))

    # Collect remaining cards
    remaining = [card_id for ids in card_map.values() for card_id in ids]

    # Shuffle remainder
    rng = random.Random(shuffle_seed)
    rng.shuffle(remaining)

    # Return hand + shuffled remainder
    return hand_cards + remaining


def _char_to_index(c: str) -> int | None:
    """Convert 0-9a-z to index 0-35."""
    if '0' <= c <= '9':
        return ord(c) - ord('0')
    elif 'a' <= c <= 'z':
        return ord(c) - ord('a') + 10
    return None


def _index_to_char(idx: int) -> str:
    """Convert index 0-35 to 0-9a-z."""
    if 0 <= idx <= 9:
        return chr(ord('0') + idx)
    elif 10 <= idx <= 35:
        return chr(ord('a') + idx - 10)
    return '0'
