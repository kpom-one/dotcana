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

    # Add cards from decklists
    _add_deck_to_game(G, deck1_txt, card_db, deck_num=1, deck_zone="Z_P1_DECK")
    _add_deck_to_game(G, deck2_txt, card_db, deck_num=2, deck_zone="Z_P2_DECK")

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


def _add_deck_to_game(G: nx.MultiDiGraph, deck_txt: Path, card_db: dict, deck_num: int, deck_zone: str) -> None:
    """Parse decklist.txt and add cards to game graph."""
    with open(deck_txt, "r") as f:
        card_index = 1
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse: "COUNT CARD_NAME"
            match = re.match(r"(\d+)\s+(.+)", line)
            if not match:
                continue

            count = int(match.group(1))
            name = match.group(2).strip()

            # Lookup card
            card = card_db.get(name)
            if not card:
                raise ValueError(f"Card '{name}' not found in database")

            # Add card instances
            for _ in range(count):
                node_id = f"D{deck_num}_{card_index:02d}"
                G.add_node(
                    node_id,
                    type="Card",
                    card_id=card["id"],
                    exerted="0",
                    damage="0",
                    label=name
                )
                G.add_edge(node_id, deck_zone, label="IN", position=str(card_index - 1))
                card_index += 1


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
