"""
Rules engine - orchestrates game state transitions.
"""
import hashlib
import json
import re
import shutil
import networkx as nx
from pathlib import Path

from lib.graph import load_dot, save_dot, can_edges
from lib.compute import compute_all
from lib.seed import parse_seed, create_deck_file, normalize_card_name


def init_game(deck1_txt: str | Path, deck2_txt: str | Path) -> tuple[nx.MultiDiGraph, str]:
    """
    Initialize a game from deck text files.

    Args:
        deck1_txt: Path to P1's decklist.txt
        deck2_txt: Path to P2's decklist.txt

    Returns:
        (game_graph, matchup_hash)
    """
    deck1_txt = Path(deck1_txt)
    deck2_txt = Path(deck2_txt)

    # Generate hash from deck contents
    matchup_hash = _generate_matchup_hash(deck1_txt, deck2_txt)
    matchdir = Path("output") / matchup_hash
    matchdir.mkdir(parents=True, exist_ok=True)

    # Load template
    G = load_dot(Path("data/template.dot"))

    # Load card database
    card_db = _load_card_database()

    # Copy deck files to matchup directory for reference
    shutil.copy(deck1_txt, matchdir / "deck1.txt")
    shutil.copy(deck2_txt, matchdir / "deck2.txt")

    # Store card database in graph for later lookups
    # (cards are not created as nodes until drawn)
    G.graph['card_db'] = card_db

    # Compute initial legal actions
    compute_all(G)

    return G, matchup_hash


def _generate_matchup_hash(deck1: Path, deck2: Path) -> str:
    """Generate 4-char hash from deck contents."""
    content1 = deck1.read_text()
    content2 = deck2.read_text()
    combined = content1 + content2
    return hashlib.md5(combined.encode()).hexdigest()[:4]


def _load_card_database() -> dict:
    """Load card database from cards.json."""
    with open("data/cards.json", "r") as f:
        data = json.load(f)
    return {card["fullName"]: card for card in data["cards"]}


def _create_card_node(G: nx.MultiDiGraph, card_id: str, player: int) -> str:
    """
    Create a card node from a card ID.

    Args:
        card_id: Normalized ID like "tinker_bell_giant_fairy.a"
        player: 1 or 2

    Returns:
        Node ID: "p1.tinker_bell_giant_fairy.a"
    """
    # Extract card name from ID (before the .suffix)
    base_name = card_id.rsplit('.', 1)[0]

    # Look up original card name in database
    card_db = G.graph['card_db']

    # Find matching card (reverse lookup by normalized name)
    original_name = None
    for name in card_db.keys():
        if normalize_card_name(name) == base_name:
            original_name = name
            break

    if not original_name:
        raise ValueError(f"Card not found for ID: {card_id}")

    card_data = card_db[original_name]
    node_id = f"p{player}.{card_id}"

    G.add_node(
        node_id,
        type="Card",
        card_id=card_data["id"],
        exerted="0",
        damage="0",
        label=original_name
    )

    return node_id


def shuffle_and_draw(matchdir: str | Path, seed: str) -> str:
    """
    Shuffle decks and draw starting hands (7 cards each).

    Creates output/<matchdir>/<seed>/ with:
    - deck1.dek (53 cards remaining)
    - deck2.dek (53 cards remaining)
    - game.dot (14 cards in hands)

    Args:
        matchdir: Matchup directory (e.g., "output/b013")
        seed: Hand-spec seed (xxxxxxx.xxxxxxx.xx)

    Returns:
        Seed (for display)
    """
    matchdir = Path(matchdir)
    hand_spec = parse_seed(seed)
    if not hand_spec:
        raise ValueError(f"Invalid seed format: {seed}")

    seed_dir = matchdir / seed
    seed_dir.mkdir(parents=True, exist_ok=True)

    # Load base game
    G = load_dot(matchdir / "game.dot")

    # Load card database (not persisted in DOT format)
    G.graph['card_db'] = _load_card_database()

    # Create shuffled decks and draw hands
    for player_num, hand_indices in [('1', hand_spec['p1_hand']), ('2', hand_spec['p2_hand'])]:
        deck_txt = matchdir / f"deck{player_num}.txt"
        deck_dek = seed_dir / f"deck{player_num}.dek"
        hand_zone = f"z.p{player_num}.hand"

        # Build shuffled deck (hand + remainder)
        shuffled = create_deck_file(deck_txt, hand_indices, hand_spec['shuffle_seed'])

        # First 7 cards: create nodes and add to hand
        for card_id in shuffled[:7]:
            node_id = _create_card_node(G, card_id, int(player_num))
            G.add_edge(node_id, hand_zone, label="IN")

        # Remaining 53 cards written to .dek (not in graph yet)
        with open(deck_dek, 'w') as f:
            for card_id in shuffled[7:]:
                f.write(f"{card_id}\n")

    # Recompute legal actions
    compute_all(G)

    # Save game state
    save_dot(G, seed_dir / "game.dot")

    return seed




def show_actions(G: nx.MultiDiGraph) -> list[dict]:
    """Return list of available actions."""
    actions = []
    for i, (u, v, key, action_type) in enumerate(can_edges(G)):
        actions.append({
            "id": _make_action_id(i),
            "type": action_type,
            "from": u,
            "to": v,
            "key": key,
        })
    return actions


def _make_action_id(index: int) -> str:
    """Generate a 2-char base36 action ID."""
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if index < 36:
        return chars[index]
    else:
        return chars[index // 36] + chars[index % 36]
