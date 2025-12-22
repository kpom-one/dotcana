#!/usr/bin/env python3
"""
Lightweight web viewer for Lorcana game states.

Browse the game tree and visualize states.
"""
import sys
from pathlib import Path

# Add parent dir to path to import from lib/
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess

from flask import Flask, render_template
from lib.core.graph import load_dot, get_node_attr, edges_by_label
from lib.lorcana.setup import show_actions

app = Flask(__name__)


@app.route('/')
@app.route('/<path:subpath>')
def browse(subpath=''):
    """Browse game tree and show state visualization."""
    base_path = Path(__file__).parent.parent / 'output'
    current_path = base_path / subpath if subpath else base_path

    # If directory exists but has no game.dot, apply the action
    if current_path.exists() and current_path.is_dir() and not (current_path / 'game.dot').exists():
        # Check if parent has a game.dot (meaning this is an action directory)
        if (current_path.parent / 'game.dot').exists():
            # Shell out to rules-engine to apply the action
            python_path = Path(__file__).parent.parent / '.venv' / 'bin' / 'python'
            subprocess.run([str(python_path), 'bin/rules-engine.py', 'play', str(current_path)],
                         cwd=Path(__file__).parent.parent,
                         capture_output=True)

    # List child directories (available actions/states)
    children = []
    if current_path.exists() and current_path.is_dir():
        children = sorted([d.name for d in current_path.iterdir() if d.is_dir()])

    # Visualize game state and get actions if it exists
    state_view = None
    action_descriptions = {}
    game_file = current_path / 'game.dot'
    if game_file.exists():
        G = load_dot(game_file)
        state_view = visualize_game_graph(G)
        actions = show_actions(G)
        action_descriptions = {a['id']: a['description'] for a in actions}

    # Breadcrumb path for navigation
    parts = subpath.split('/') if subpath else []
    breadcrumbs = []

    # Root breadcrumb
    breadcrumbs.append(('output', ''))

    # Build incremental paths for each part
    for i, part in enumerate(parts):
        path = '/'.join(parts[:i+1])
        breadcrumbs.append((part, path))

    return render_template('game.html',
                         current_path=subpath,
                         breadcrumbs=breadcrumbs,
                         children=children,
                         action_descriptions=action_descriptions,
                         state=state_view)


def visualize_game_graph(G) -> str:
    """Generate ASCII visualization of game state from graph."""

    lines = []
    lines.append("=" * 60)

    # Game info
    turn = get_node_attr(G, 'game', 'turn', '0')

    # Find current player
    edges = edges_by_label(G, "CURRENT_TURN")
    current_player = edges[0][1] if edges else "p1"

    lines.append(f"  TURN {turn}  •  {current_player.upper()}'S TURN")
    lines.append("=" * 60)
    lines.append("")

    # Show both players
    for player in ['p1', 'p2']:
        is_current = (player == current_player)
        marker = "►" if is_current else " "

        # Player stats
        lore = get_node_attr(G, player, 'lore', '0')
        ink_drops = get_node_attr(G, player, 'ink_drops', '0')

        lines.append(f"{marker} PLAYER {player[-1].upper()}")
        lines.append(f"  Lore: {lore}/20")
        lines.append(f"  Ink drops: {ink_drops}")

        # Cards in zones
        hand_zone = f"z.{player}.hand"
        play_zone = f"z.{player}.play"
        ink_zone = f"z.{player}.ink"

        # Get cards in each zone
        hand_cards = get_cards_in_zone(G, hand_zone)
        play_cards = get_cards_in_zone(G, play_zone)
        ink_cards = get_cards_in_zone(G, ink_zone)

        # Show hand
        if player == current_player:
            # Show current player's hand
            lines.append(f"  Hand ({len(hand_cards)}):")
            for card in hand_cards[:5]:  # Limit display
                label = get_node_attr(G, card, 'label', card)
                lines.append(f"    • {label}")
            if len(hand_cards) > 5:
                lines.append(f"    ... and {len(hand_cards) - 5} more")
        else:
            # Hide opponent's hand
            lines.append(f"  Hand: {len(hand_cards)} cards")

        # Show play area
        lines.append(f"  In Play ({len(play_cards)}):")
        for card in play_cards:
            label = get_node_attr(G, card, 'label', card)
            exerted = get_node_attr(G, card, 'exerted', '0')
            damage = get_node_attr(G, card, 'damage', '0')

            status = "💤 exerted" if exerted == '1' else "⚡ ready"
            dmg_str = f", {damage} dmg" if damage != '0' else ""
            lines.append(f"    {status}: {label}{dmg_str}")

        # Show inkwell
        lines.append(f"  Inkwell: {len(ink_cards)} cards")

        lines.append("")

    lines.append("=" * 60)

    return '\n'.join(lines)


def get_cards_in_zone(G, zone_name: str) -> list[str]:
    """Get list of card nodes in a zone."""
    cards = []
    for u, v, key, data in G.edges(keys=True, data=True):
        label = data.get('label', '')
        if isinstance(label, str):
            label = label.strip('"')
        if label == 'IN' and v == zone_name:
            cards.append(u)
    return cards


if __name__ == '__main__':
    print("Starting web viewer at http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, port=5000)
