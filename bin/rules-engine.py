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

from lib.core.graph import load_dot, save_dot, can_edges, get_node_attr
from lib.lorcana.setup import init_game, shuffle_and_draw, show_actions
from lib.lorcana.state import LorcanaState
from lib.lorcana.actions import make_action_id
from lib.lorcana.compute import compute_all


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

    # If directory is empty (no game.dot), apply the action
    if not (path / "game.dot").exists():
        apply_action_at_path(path)
        print(f"[rules-engine] Applied action: {path.name}", file=sys.stderr)

    # Load and show available actions
    state = LorcanaState(path)
    state.load()
    actions = show_actions(state.graph)

    print(f"[rules-engine] play: {path}", file=sys.stderr)

    if not actions:
        print("No actions available.")
        return

    print("\nAvailable actions:")
    for a in actions:
        print(f"  [{a['id']}] {a['description']}")


def apply_action_at_path(path: Path) -> None:
    """Apply the action represented by this directory."""
    from lib.core.graph import edges_by_label

    parent_path = path.parent
    action_id = path.name

    # Load parent state
    parent = LorcanaState(parent_path)
    parent.load()

    # Find the action edge that matches this ID
    action_found = False
    for u, v, key, action_type in can_edges(parent.graph):
        if make_action_id(action_type, u, v) == action_id:
            # Apply the action (mutates parent.graph)
            execute_action(parent, action_type, u, v)
            action_found = True
            break

    if not action_found:
        raise ValueError(f"Action {action_id} not found in parent state")

    # Create new state at action path with mutated graph
    new_state = LorcanaState(path)
    new_state.graph = parent.graph
    new_state.deck1_ids = parent.deck1_ids
    new_state.deck2_ids = parent.deck2_ids
    new_state.save()


def execute_action(state: LorcanaState, action_type: str, from_node: str, to_node: str) -> None:
    """Execute an action, mutating the state."""
    from lib.core.graph import edges_by_label

    if action_type == "CAN_PASS":
        # Switch current player
        edges = edges_by_label(state.graph, "CURRENT_TURN")
        if edges:
            game, current_player, key = edges[0]
            # Remove current turn edge
            state.graph.remove_edge(game, current_player, key)

            # Determine other player
            other_player = "p2" if current_player == "p1" else "p1"

            # Add current turn edge to other player
            state.graph.add_edge(game, other_player, label="CURRENT_TURN")

        # Increment turn counter
        turn = int(get_node_attr(state.graph, 'game', 'turn', 0))
        state.graph.nodes['game']['turn'] = str(turn + 1)

    elif action_type == "CAN_INK":
        # Move card from hand to inkwell
        state.move_card(from_node, to_node)

        # Decrement ink_drops for current player
        edges = edges_by_label(state.graph, "CURRENT_TURN")
        if edges:
            game, player, _ = edges[0]
            ink_drops = int(get_node_attr(state.graph, player, 'ink_drops', 1))
            state.graph.nodes[player]['ink_drops'] = str(ink_drops - 1)

    else:
        print(f"TODO: Implement {action_type}", file=sys.stderr)

    # Recompute legal actions after any mutation
    compute_all(state.graph)


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
