#!/usr/bin/env python3
"""
Dotcana Rules Engine

Commands:
    init <deck1.txt> <deck2.txt>   - Create matchup from decklists
    shuffle <matchdir> <seed>      - Shuffle and deal starting hands
    show <game.dot>                - Show available actions
"""
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.core.graph import load_dot, save_dot, can_edges
from lib.lorcana.setup import init_game, shuffle_and_draw, show_actions


def cmd_init(deck1: str, deck2: str) -> None:
    """Create matchup from decklist files."""
    G, matchup_hash = init_game(deck1, deck2)
    output = Path("output") / matchup_hash / "game.dot"
    save_dot(G, output)

    # Print hash to stdout for justfile to capture
    print(matchup_hash)
    print(f"[rules-engine] init: {output}", file=sys.stderr)


def cmd_shuffle(matchdir: str, seed: str) -> None:
    """Shuffle decks and draw starting hands."""
    seed = shuffle_and_draw(matchdir, seed)
    output = Path(matchdir) / seed / "game.dot"

    print(seed)
    print(f"[rules-engine] shuffle: seed={seed} -> {output}", file=sys.stderr)

    # Show available actions
    G = load_dot(output)
    actions = show_actions(G)

    if actions:
        print("\nAvailable actions:", file=sys.stderr)
        for a in actions:
            print(f"  [{a['id']}] {a['description']}", file=sys.stderr)


def cmd_show(game_dot: str) -> None:
    """Show available actions."""
    G = load_dot(game_dot)
    actions = show_actions(G)

    print(f"[rules-engine] show: {game_dot}", file=sys.stderr)

    if not actions:
        print("No actions available.")
        return

    print("Available actions:")
    for a in actions:
        print(f"  [{a['id']}] {a['description']}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        if len(sys.argv) != 4:
            print("Usage: rules-engine.py init <deck1.txt> <deck2.txt>")
            sys.exit(1)
        cmd_init(sys.argv[2], sys.argv[3])

    elif cmd == "shuffle":
        if len(sys.argv) != 4:
            print("Usage: rules-engine.py shuffle <matchdir> <seed>")
            sys.exit(1)
        cmd_shuffle(sys.argv[2], sys.argv[3])

    elif cmd == "show":
        if len(sys.argv) != 3:
            print("Usage: rules-engine.py show <game.dot>")
            sys.exit(1)
        cmd_show(sys.argv[2])

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
