#!/usr/bin/env python3
"""
Dotcana Rules Engine

Commands:
    init <matchdir>      - Create base game.dot from template + decks
    show <game.dot>      - Show available actions
    <path>               - Apply action (path format: .../parent/action_id)
"""
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.graph import load_dot, save_dot, can_edges
from lib.engine import init_game, apply_action, show_actions


def cmd_init(matchdir: str) -> None:
    """Create base game.dot from template + decks."""
    matchdir = Path(matchdir)
    output = matchdir / "game.dot"

    G = init_game(matchdir)
    save_dot(G, output)

    print(f"[rules-engine] init: {output}", file=sys.stderr)


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
        print(f"  [{a['id']}] {a['type']}: {a['from']} -> {a['to']}")


def cmd_apply(target_path: str) -> None:
    """Apply action. Path format: .../parent_dir/action_id"""
    target_path = Path(target_path.rstrip("/"))
    parent_dir = target_path.parent
    action_id = target_path.name
    parent_game = parent_dir / "game.dot"
    output_game = target_path / "game.dot"

    if not parent_game.exists():
        print(f"Error: Parent state not found: {parent_game}", file=sys.stderr)
        sys.exit(1)

    G = load_dot(parent_game)
    G = apply_action(G, action_id)
    save_dot(G, output_game)

    print(f"[rules-engine] apply: {action_id} -> {output_game}", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        if len(sys.argv) != 3:
            print("Usage: rules-engine.py init <matchdir>")
            sys.exit(1)
        cmd_init(sys.argv[2])

    elif cmd == "show":
        if len(sys.argv) != 3:
            print("Usage: rules-engine.py show <game.dot>")
            sys.exit(1)
        cmd_show(sys.argv[2])

    else:
        # Assume it's a path for apply
        cmd_apply(cmd)


if __name__ == "__main__":
    main()
