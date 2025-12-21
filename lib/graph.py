"""
Graph loading and saving utilities using networkx + pydot.
"""
import networkx as nx
from pathlib import Path


def load_dot(path: str | Path) -> nx.MultiDiGraph:
    """Load a DOT file into a networkx MultiDiGraph."""
    G = nx.drawing.nx_pydot.read_dot(str(path))
    return G


def save_dot(G: nx.MultiDiGraph, path: str | Path) -> None:
    """Save a networkx graph to DOT format."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    nx.drawing.nx_pydot.write_dot(G, str(path))


def get_node_attr(G: nx.MultiDiGraph, node: str, attr: str, default=None):
    """Get a node attribute, stripping quotes if present."""
    val = G.nodes[node].get(attr, default)
    if isinstance(val, str):
        val = val.strip('"')
    return val


def get_edge_attr(G: nx.MultiDiGraph, u: str, v: str, key: str, attr: str, default=None):
    """Get an edge attribute."""
    val = G.edges[u, v, key].get(attr, default)
    if isinstance(val, str):
        val = val.strip('"')
    return val


def nodes_by_type(G: nx.MultiDiGraph, node_type: str) -> list[str]:
    """Get all nodes of a given type."""
    return [n for n in G.nodes() if get_node_attr(G, n, "type") == node_type]


def edges_by_label(G: nx.MultiDiGraph, label: str) -> list[tuple[str, str, str]]:
    """Get all edges with a given label. Returns list of (u, v, key)."""
    result = []
    for u, v, key, data in G.edges(keys=True, data=True):
        edge_label = data.get("label", key)
        if isinstance(edge_label, str):
            edge_label = edge_label.strip('"')
        if edge_label == label:
            result.append((u, v, key))
    return result


def can_edges(G: nx.MultiDiGraph) -> list[tuple[str, str, str, str]]:
    """Get all action edges. Returns list of (u, v, key, action_type)."""
    result = []
    for u, v, key, data in G.edges(keys=True, data=True):
        action_type = data.get("action_type")
        if action_type:
            if isinstance(action_type, str):
                action_type = action_type.strip('"')
            result.append((u, v, key, action_type))
    return result
