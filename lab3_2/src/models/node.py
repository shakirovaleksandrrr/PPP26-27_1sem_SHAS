"""Node model representing a discrete cell in the pathfinding grid."""

from enum import Enum
from typing import Optional, Tuple


class NodeType(Enum):
    """Enumeration of cell types and visual states in the grid."""
    EMPTY = 0
    WALL = 1
    START = 2
    GOAL = 3
    OPEN = 4       # Candidate in priority queue
    CLOSED = 5     # Fully explored / visited node
    PATH = 6       # Reconstructed shortest path node


class Node:
    """Represents a single graph node with spatial position, costs, and state."""

    def __init__(self, row: int, col: int) -> None:
        """Initialize node with grid matrix coordinates.

        Args:
            row: Row index in grid (0-indexed).
            col: Column index in grid (0-indexed).
        """
        self.row = row
        self.col = col
        self.node_type = NodeType.EMPTY

        # A* and Dijkstra cost values
        self.g_cost: float = float("inf")  # Exact distance from start to this node
        self.h_cost: float = 0.0           # Heuristic estimated distance to goal
        self.f_cost: float = float("inf")  # Total estimated cost: g + h
        self.parent: Optional["Node"] = None

    def reset_costs(self) -> None:
        """Reset search metrics and path backpointers."""
        self.g_cost = float("inf")
        self.h_cost = 0.0
        self.f_cost = float("inf")
        self.parent = None
        if self.node_type in (NodeType.OPEN, NodeType.CLOSED, NodeType.PATH):
            self.node_type = NodeType.EMPTY

    def reset_all(self) -> None:
        """Reset all state including walls, returning node to empty."""
        self.reset_costs()
        self.node_type = NodeType.EMPTY

    @property
    def is_traversable(self) -> bool:
        """Check if node can be navigated through."""
        return self.node_type != NodeType.WALL

    def __lt__(self, other: "Node") -> bool:
        """Compare nodes for priority queue ordering (heapq).

        Priority is based primarily on lower f_cost, breaking ties by lower h_cost.
        """
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost

    def __repr__(self) -> str:
        """Return debugging string representation."""
        return f"Node({self.row}, {self.col}, type={self.node_type.name})"
