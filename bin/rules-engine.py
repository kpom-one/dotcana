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

from lib.core.graph import load_dot, save_dot
from lib.lorcana.setup import init_game, shuffle_and_draw, show_actions
from lib.lorcana.state import LorcanaState
from lib.lorcana.execute import apply_action_at_path


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


def cmd_play(path: str) -> None:
    """Navigate to state, apply action if needed, show available actions."""
    from pathlib import Path
    from lib.core.graph import edges_by_label

    path = Path(path)

    # Recursively ensure all parent states exist
    def ensure_state_exists(p: Path):
        """Recursively apply actions from root to this path."""
        if (p / "game.dot").exists():
            return  # State already exists

        # Check if parent exists, recurse if needed
        parent = p.parent
        if parent != p and not (parent / "game.dot").exists():
            ensure_state_exists(parent)

        # Apply this action
        apply_action_at_path(p)
        print(f"[rules-engine] Applied action: {p.name}", file=sys.stderr)

    ensure_state_exists(path)

    # Load and show available actions
    state = LorcanaState(path)
    state.load()
    actions = show_actions(state.graph)

    print(f"[rules-engine] play: {path}", file=sys.stderr)

    # Show game state summary
    from lib.core.graph import get_node_attr

    # Get current turn
    turn_edges = edges_by_label(state.graph, "CURRENT_TURN")
    current_player = turn_edges[0][1] if turn_edges else "?"

    # Get player stats
    p1_lore = get_node_attr(state.graph, 'p1', 'lore', '0')
    p2_lore = get_node_attr(state.graph, 'p2', 'lore', '0')
    p1_ink_avail = get_node_attr(state.graph, 'p1', 'ink_available', '0')
    p1_ink_total = get_node_attr(state.graph, 'p1', 'ink_total', '0')
    p2_ink_avail = get_node_attr(state.graph, 'p2', 'ink_available', '0')
    p2_ink_total = get_node_attr(state.graph, 'p2', 'ink_total', '0')

    marker_p1 = "►" if current_player == "p1" else " "
    marker_p2 = "►" if current_player == "p2" else " "

    print(f"\n{marker_p1} P1: {p1_lore} lore, {p1_ink_avail}/{p1_ink_total} ink")
    print(f"{marker_p2} P2: {p2_lore} lore, {p2_ink_avail}/{p2_ink_total} ink")

    if not actions:
        print("\nNo actions available.")
        return

    print("\nAvailable actions:")
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

    elif cmd == "play":
        if len(sys.argv) != 3:
            print("Usage: rules-engine.py play <path>")
            sys.exit(1)
        cmd_play(sys.argv[2])

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
