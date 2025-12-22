"""
End turn mechanic.

Compute when a player can end turn, and execute the end turn action.
"""
import networkx as nx
from lib.core.graph import edges_by_label, get_node_attr


def compute_can_pass(G: nx.MultiDiGraph) -> list[tuple[str, str, str]]:
    """Return CAN_PASS edge for current player."""
    edges = edges_by_label(G, "CURRENT_TURN")
    if edges:
        game, player, _ = edges[0]  # GAME -> Player
        return [(player, game, "CAN_PASS")]
    return []


def execute_pass(state, from_node: str, to_node: str) -> None:
    """Execute pass action: switch players, increment turn, reset ink."""
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

        # Give the new player 1 ink drop for their turn
        state.graph.nodes[other_player]['ink_drops'] = '1'

        # Refresh ink_available to match ink_total
        ink_total = int(get_node_attr(state.graph, other_player, 'ink_total', 0))
        state.graph.nodes[other_player]['ink_available'] = str(ink_total)

    # Increment turn counter
    turn = int(get_node_attr(state.graph, 'game', 'turn', 0))
    state.graph.nodes['game']['turn'] = str(turn + 1)
