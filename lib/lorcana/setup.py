"""
Lorcana game setup - initialization and shuffling.
"""
import hashlib
import shutil
import networkx as nx
from pathlib import Path

from lib.core.graph import load_dot, save_dot, can_edges, DECK1_SOURCE, DECK2_SOURCE
from lib.core.seed import parse_seed
from lib.lorcana.cards import get_card_db
from lib.lorcana.state import LorcanaState
from lib.lorcana.deck import build_shuffled_deck
from lib.lorcana.compute import compute_all


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

    # Preload card database (singleton)
    get_card_db()

    # Copy deck files to matchup directory for reference
    shutil.copy(deck1_txt, matchdir / DECK1_SOURCE)
    shutil.copy(deck2_txt, matchdir / DECK2_SOURCE)

    # Compute initial legal actions
    compute_all(G)

    return G, matchup_hash


def _generate_matchup_hash(deck1: Path, deck2: Path) -> str:
    """Generate 4-char hash from deck contents."""
    content1 = deck1.read_text()
    content2 = deck2.read_text()
    combined = content1 + content2
    return hashlib.md5(combined.encode()).hexdigest()[:4]


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

    # Load parent state
    parent = LorcanaState(matchdir)
    parent.load()

    # Build shuffled decks from .txt files
    deck1_txt = matchdir / DECK1_SOURCE
    deck2_txt = matchdir / DECK2_SOURCE
    deck1_ids = build_shuffled_deck(deck1_txt, hand_spec['p1_hand'], hand_spec['shuffle_seed'])
    deck2_ids = build_shuffled_deck(deck2_txt, hand_spec['p2_hand'], hand_spec['shuffle_seed'])

    # Create new state at seed path
    state = LorcanaState(matchdir / seed)
    state.graph = parent.graph

    # Set decks and draw hands
    state.deck1_ids = deck1_ids
    state.deck2_ids = deck2_ids
    state.draw(player=1, count=7)
    state.draw(player=2, count=7)

    # Recompute legal actions
    compute_all(state.graph)

    # Save
    state.save()

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
