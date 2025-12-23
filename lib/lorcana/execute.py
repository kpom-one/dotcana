"""
Execute actions on Lorcana game state.

Applies mutations to the graph based on action types.
Routes to specific mechanic implementations.
"""
from pathlib import Path
import sys
from lib.core.graph import can_edges
from lib.core.persistence import load_state, save_state
from lib.lorcana.state import LorcanaState
from lib.lorcana.compute import compute_all
from lib.lorcana.mechanics.end import execute_pass
from lib.lorcana.mechanics.ink import execute_ink
from lib.lorcana.mechanics.play import execute_play
from lib.lorcana.mechanics.quest import execute_quest
from lib.lorcana.mechanics.challenge import execute_challenge
from lib.lorcana.state_based_effects import check_state_based_effects


def execute_action(state: LorcanaState, action_type: str, from_node: str, to_node: str) -> None:
    """Execute an action, mutating the state."""
    if action_type == "CAN_PASS":
        execute_pass(state, from_node, to_node)
    elif action_type == "CAN_INK":
        execute_ink(state, from_node, to_node)
    elif action_type == "CAN_PLAY":
        execute_play(state, from_node, to_node)
    elif action_type == "CAN_QUEST":
        execute_quest(state, from_node, to_node)
    elif action_type == "CAN_CHALLENGE":
        execute_challenge(state, from_node, to_node)
    else:
        print(f"TODO: Implement {action_type}", file=sys.stderr)

    # Check state-based effects (banish damaged characters, etc.)
    check_state_based_effects(state)

    # Recompute legal actions after any mutation
    compute_all(state.graph)


def apply_action_at_path(path: Path) -> None:
    """
    Apply the action represented by this directory.

    Recursively ensures all parent states exist before applying this action.
    """
    from lib.core.navigation import format_actions

    path = Path(path)

    # If state already exists, nothing to do
    if (path / "game.dot").exists():
        return

    # Recursively ensure parent exists
    parent_path = path.parent
    if parent_path != path and not (parent_path / "game.dot").exists():
        apply_action_at_path(parent_path)

    # Now apply this action
    action_id = path.name

    # Load parent state
    parent = load_state(parent_path, LorcanaState)

    # Find the action edge that matches this ID
    action_found = False
    for u, v, key, action_type, edge_action_id in can_edges(parent.graph):
        if edge_action_id == action_id:
            # Apply the action (mutates parent.graph)
            execute_action(parent, action_type, u, v)
            action_found = True
            break

    if not action_found:
        raise ValueError(f"Action {action_id} not found in parent state")

    # Save new state at action path
    save_state(parent, path, format_actions_fn=format_actions)
