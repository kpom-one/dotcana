"""
Navigation file utilities for game tree exploration.

Manages path.txt and actions.txt files that document game state navigation.
"""
import networkx as nx
from pathlib import Path
from lib.core.graph import can_edges, get_edge_attr


def format_actions(G: nx.MultiDiGraph) -> list[dict]:
    """
    Format action edges into list of action dicts.

    Generic formatter that reads description from edge metadata.

    Returns:
        List of dicts with keys: id, type, from, to, key, description
    """
    actions = []
    # Sort edges by action_type for deterministic ordering
    sorted_edges = sorted(can_edges(G), key=lambda e: (e[3], e[0], e[1]))  # (action_type, from, to)

    for u, v, key, action_type, action_id in sorted_edges:
        description = get_edge_attr(G, u, v, key, "description", action_type.lower())
        actions.append({
            "id": action_id,
            "type": action_type,
            "from": u,
            "to": v,
            "key": key,
            "description": description,
        })
    return actions


def write_path_file(path: Path, parent_path: Path | None = None) -> None:
    """
    Write path.txt showing how we got to this state.

    Copies parent's path.txt and appends the action that got us here.

    Args:
        path: Current state directory
        parent_path: Parent state directory (if None, uses path.parent)
    """
    if parent_path is None:
        parent_path = path.parent

    lines = []

    # If we have a parent with a path file, copy it
    parent_path_file = parent_path / "path.txt"
    if parent_path_file.exists():
        with open(parent_path_file) as f:
            lines = [line.rstrip() for line in f]

        # Append the action that got us here by looking it up in parent's actions.txt
        action_id = path.name
        parent_actions_file = parent_path / "actions.txt"
        if parent_actions_file.exists():
            with open(parent_actions_file) as f:
                for line in f:
                    if line.startswith(action_id + ":"):
                        lines.append(line.rstrip())
                        break

    # Write path.txt
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "path.txt", 'w') as f:
        for line in lines:
            f.write(line + '\n')


def write_actions_file(path: Path, actions: list[dict]) -> None:
    """
    Write actions.txt showing available actions from this state.

    Args:
        path: Current state directory
        actions: List of action dicts with 'id' and 'description' keys
    """
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "actions.txt", 'w') as f:
        for action in actions:
            f.write(f"{action['id']}: {action['description']}\n")


def read_actions_file(path: Path) -> list[dict]:
    """
    Read actions.txt and return list of action dicts.

    Args:
        path: Directory containing actions.txt

    Returns:
        List of dicts with 'id' and 'description' keys
    """
    actions = []
    actions_file = Path(path) / "actions.txt"

    if not actions_file.exists():
        return actions

    with open(actions_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Parse "id: description" format
            if ':' in line:
                action_id, description = line.split(':', 1)
                actions.append({
                    'id': action_id.strip(),
                    'description': description.strip()
                })

    return actions
