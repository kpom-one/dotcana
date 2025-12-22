"""
LorcanaState - stateful game state with Lorcana-specific operations.

Supports both usage patterns:
1. Stateless: load() → operate → save()
2. Stateful: load() once → operate many times → save() when needed
"""
import networkx as nx
from pathlib import Path

from lib.core.graph import load_dot, save_dot, load_deck, save_deck, GAME_FILE, can_edges
from lib.lorcana.cards import get_card_db
from lib.lorcana.deck import normalize_card_name
from lib.lorcana.compute import compute_all
from lib.lorcana.actions import make_action_id


class LorcanaState:
    """
    Lorcana game state - wraps graph + decks with game-specific operations.

    This is where ALL Lorcana game logic lives. Core infrastructure (graph.py)
    stays game-agnostic.
    """

    def __init__(self, path: Path | str):
        """
        Create state for a game directory.

        Args:
            path: Path to game state directory (e.g., "output/b013/seed/a0")
        """
        self.path = Path(path)

        # In-memory state (lazy loaded)
        self.graph = None
        self.deck1_ids = None
        self.deck2_ids = None

    def load(self):
        """Load graph and decks from filesystem."""
        game_file = self.path / GAME_FILE
        if not game_file.exists():
            raise FileNotFoundError(f"No {GAME_FILE} at {self.path}")

        self.graph = load_dot(game_file)
        self.deck1_ids = load_deck(self.path, player=1)
        self.deck2_ids = load_deck(self.path, player=2)

    def save(self):
        """Save graph and decks to filesystem, creating action directories."""
        save_dot(self.graph, self.path / GAME_FILE)
        save_deck(self.deck1_ids, self.path, player=1)
        save_deck(self.deck2_ids, self.path, player=2)

        # Create empty directories for all possible actions
        for u, v, key, action_type in can_edges(self.graph):
            action_id = make_action_id(action_type, u, v)
            action_dir = self.path / action_id
            action_dir.mkdir(exist_ok=True)

    # ========== Game Operations ==========

    def draw(self, player: int, count: int = 1):
        """
        Draw cards from deck to hand.

        Args:
            player: Player number (1 or 2)
            count: Number of cards to draw

        Mutates: graph (adds card nodes), deck_ids (removes drawn cards)
        """
        deck_ids = self.deck1_ids if player == 1 else self.deck2_ids
        hand_zone = f"z.p{player}.hand"

        # Draw cards
        for card_id in deck_ids[:count]:
            node_id = self._create_card_node(card_id, player)
            self.graph.add_edge(node_id, hand_zone, label="IN")

        # Update deck state
        remaining = deck_ids[count:]
        if player == 1:
            self.deck1_ids = remaining
        else:
            self.deck2_ids = remaining

    def exert(self, card_node: str):
        """Set card to exerted state."""
        self.graph.nodes[card_node]['exerted'] = '1'

    def ready(self, card_node: str):
        """Set card to ready state."""
        self.graph.nodes[card_node]['exerted'] = '0'

    def add_lore(self, player: str, amount: int):
        """Add lore to player."""
        current = int(self.graph.nodes[player].get('lore', 0))
        self.graph.nodes[player]['lore'] = str(current + amount)

    def move_card(self, card_node: str, to_zone: str):
        """
        Move card to different zone.

        Removes old IN edge, adds new IN edge.
        """
        # Remove existing IN edges
        to_remove = []
        for u, v, key, data in self.graph.edges(card_node, keys=True, data=True):
            if data.get('label') == 'IN':
                to_remove.append((u, v, key))

        for edge in to_remove:
            self.graph.remove_edge(*edge)

        # Add new IN edge
        self.graph.add_edge(card_node, to_zone, label="IN")

    def damage_card(self, card_node: str, amount: int):
        """Deal damage to card."""
        current = int(self.graph.nodes[card_node].get('damage', 0))
        self.graph.nodes[card_node]['damage'] = str(current + amount)

    # ========== Internal Helpers ==========

    def _create_card_node(self, card_id: str, player: int) -> str:
        """
        Create card node in graph.

        Args:
            card_id: Normalized ID like "tinker_bell_giant_fairy.a"
            player: Player number (1 or 2)

        Returns:
            Node ID: "p1.tinker_bell_giant_fairy.a"
        """
        card_db = get_card_db()

        # Extract base card name
        base_name = card_id.rsplit('.', 1)[0]

        # Reverse lookup in card database
        original_name = None
        for name in card_db.keys():
            if normalize_card_name(name) == base_name:
                original_name = name
                break

        if not original_name:
            raise ValueError(f"Card not found for ID: {card_id}")

        card_data = card_db[original_name]
        node_id = f"p{player}.{card_id}"

        self.graph.add_node(
            node_id,
            type="Card",
            card_id=card_data["id"],
            exerted="0",
            damage="0",
            label=original_name
        )

        return node_id
