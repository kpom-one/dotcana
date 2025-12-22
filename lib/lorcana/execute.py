"""
Execute actions on Lorcana game state.

Applies mutations to the graph based on action types.
Routes to specific mechanic implementations.
"""
from pathlib import Path
import sys
from lib.core.graph import can_edges
from lib.lorcana.state import LorcanaState
from lib.lorcana.actions import make_action_id
from lib.lorcana.compute import compute_all
from lib.lorcana.mechanics.end import execute_pass
from lib.lorcana.mechanics.ink import execute_ink
from lib.lorcana.mechanics.play import execute_play


def execute_action(state: LorcanaState, action_type: str, from_node: str, to_node: str) -> None:
    """Execute an action, mutating the state."""
    if action_type == "CAN_PASS":
        execute_pass(state, from_node, to_node)
    elif action_type == "CAN_INK":
        execute_ink(state, from_node, to_node)
    elif action_type == "CAN_PLAY":
        execute_play(state, from_node, to_node)
    else:
        print(f"TODO: Implement {action_type}", file=sys.stderr)

    # Recompute legal actions after any mutation
    compute_all(state.graph)


def apply_action_at_path(path: Path) -> None:
    """Apply the action represented by this directory."""
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
