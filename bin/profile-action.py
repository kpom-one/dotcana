#!/usr/bin/env python3
"""Profile where time is spent in action application."""
import time
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.core.file_store import FileStore
from lib.lorcana.state import LorcanaState
from lib.lorcana.execute import execute_action
from lib.lorcana.compute import compute_all
from lib.core.graph import can_edges

def profile_action(parent_path, action_id):
    """Profile applying a single action."""
    store = FileStore()

    t0 = time.time()
    state = store.load_state(parent_path, LorcanaState)
    t1 = time.time()
    print(f"Load state: {(t1-t0)*1000:.1f}ms")

    # Find action
    for u, v, key, action_type, edge_action_id in can_edges(state.graph):
        if edge_action_id == action_id:
            # Profile execute_action internals
            t2 = time.time()

            # Manually replicate execute_action to profile parts
            from lib.lorcana.mechanics.ink import execute_ink
            from lib.lorcana.mechanics.play import execute_play
            from lib.lorcana.mechanics.quest import execute_quest
            from lib.lorcana.mechanics.challenge import execute_challenge
            from lib.lorcana.mechanics.turn import advance_turn

            if action_type == "CAN_PASS":
                advance_turn(state, u, v)
            elif action_type == "CAN_INK":
                execute_ink(state, u, v)
            elif action_type == "CAN_PLAY":
                execute_play(state, u, v)
            elif action_type == "CAN_QUEST":
                execute_quest(state, u, v)
            elif action_type == "CAN_CHALLENGE":
                execute_challenge(state, u, v)

            t3 = time.time()
            print(f"Execute mechanic: {(t3-t2)*1000:.1f}ms")

            from lib.lorcana.state_based_effects import check_state_based_effects
            check_state_based_effects(state)
            t3b = time.time()
            print(f"State-based effects: {(t3b-t3)*1000:.1f}ms")

            t4 = time.time()

            # Profile each compute function
            from lib.lorcana.mechanics.turn import compute_can_pass
            from lib.lorcana.mechanics.ink import compute_can_ink
            from lib.lorcana.mechanics.play import compute_can_play
            from lib.lorcana.mechanics.quest import compute_can_quest
            from lib.lorcana.mechanics.challenge import compute_can_challenge

            t_start = time.time()
            compute_can_pass(state.graph)
            print(f"  compute_can_pass: {(time.time()-t_start)*1000:.1f}ms")

            t_start = time.time()
            compute_can_ink(state.graph)
            print(f"  compute_can_ink: {(time.time()-t_start)*1000:.1f}ms")

            t_start = time.time()
            compute_can_play(state.graph)
            print(f"  compute_can_play: {(time.time()-t_start)*1000:.1f}ms")

            t_start = time.time()
            compute_can_quest(state.graph)
            print(f"  compute_can_quest: {(time.time()-t_start)*1000:.1f}ms")

            t_start = time.time()
            compute_can_challenge(state.graph)
            print(f"  compute_can_challenge: {(time.time()-t_start)*1000:.1f}ms")

            # Now run full compute_all for consistency
            compute_all(state.graph)
            t5 = time.time()
            print(f"Compute actions (total): {(t5-t4)*1000:.1f}ms")

            child_path = Path(parent_path) / action_id
            child_path.mkdir(parents=True, exist_ok=True)

            t6 = time.time()
            from lib.core.navigation import format_actions
            store.save_state(state, child_path, format_actions_fn=format_actions)
            t7 = time.time()
            print(f"Save state: {(t7-t6)*1000:.1f}ms")

            print(f"TOTAL: {(t7-t0)*1000:.1f}ms")
            return

    print(f"Action {action_id} not found")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: profile-action.py <parent_path> <action_id>")
        sys.exit(1)

    profile_action(sys.argv[1], sys.argv[2])
