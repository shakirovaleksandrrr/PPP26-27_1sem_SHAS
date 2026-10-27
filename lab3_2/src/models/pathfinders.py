"""Pathfinding algorithms implementation: A*, Dijkstra, BFS, and Greedy Best-First."""

import heapq
import math
from collections import deque
from enum import Enum
from typing import Callable, Deque, Dict, Generator, List, Optional, Set, Tuple
from src.models.grid import Grid
from src.models.node import Node, NodeType


class HeuristicType(Enum):
    """Supported distance heuristics for informed search."""
    MANHATTAN = "Манхэттен"
    EUCLIDEAN = "Евклид"
    CHEBYSHEV = "Чебышев"


def calculate_heuristic(n1: Node, n2: Node, h_type: HeuristicType = HeuristicType.MANHATTAN) -> float:
    """Calculate heuristic distance estimate between two grid nodes.

    Args:
        n1: Source node.
        n2: Target / goal node.
        h_type: Distance formula metric.

    Returns:
        Estimated distance as float.
    """
    dr = abs(n1.row - n2.row)
    dc = abs(n1.col - n2.col)
    if h_type == HeuristicType.MANHATTAN:
        return float(dr + dc)
    elif h_type == HeuristicType.EUCLIDEAN:
        return math.sqrt(dr * dr + dc * dc)
    elif h_type == HeuristicType.CHEBYSHEV:
        return float(max(dr, dc))
    return float(dr + dc)


class BasePathfinder:
    """Abstract base class for pathfinding search algorithms."""

    def __init__(self, grid: Grid, heuristic: HeuristicType = HeuristicType.MANHATTAN) -> None:
        """Initialize pathfinder on specified grid.

        Args:
            grid: Grid model instance.
            heuristic: Distance heuristic function to use.
        """
        self.grid = grid
        self.heuristic = heuristic
        self.start_node = grid.start_node
        self.goal_node = grid.goal_node

        self.is_finished: bool = False
        self.is_found: bool = False
        self.visited_count: int = 0
        self.path_length: int = 0
        self.path: List[Node] = []

        self.reset()

    def reset(self) -> None:
        """Reset search structures and prepare initial frontier."""
        self.grid.clear_search()
        self.start_node = self.grid.start_node
        self.goal_node = self.grid.goal_node
        self.is_finished = False
        self.is_found = False
        self.visited_count = 0
        self.path_length = 0
        self.path = []

    def reconstruct_path(self) -> List[Node]:
        """Reconstruct shortest path by following node parent pointers from goal to start.

        Returns:
            Ordered list of nodes forming the path from start to goal.
        """
        path = []
        curr = self.goal_node
        while curr is not None:
            path.append(curr)
            if curr != self.start_node and curr != self.goal_node:
                curr.node_type = NodeType.PATH
            curr = curr.parent
        path.reverse()
        self.path = path
        self.path_length = len(path)
        return path

    def step(self) -> bool:
        """Execute one step of the search algorithm.

        Returns:
            True if search should continue, False if search finished.
        """
        raise NotImplementedError

    def run_all(self) -> Tuple[List[Node], bool]:
        """Execute search until completion immediately.

        Returns:
            Tuple of (reconstructed_path, is_found).
        """
        while self.step():
            pass
        return self.path, self.is_found


class AStarFinder(BasePathfinder):
    """A* Pathfinding Algorithm (f = g + h). Guaranteed to find shortest path."""

    def reset(self) -> None:
        """Initialize A* priority queue with start node."""
        super().reset()
        self.start_node.g_cost = 0.0
        self.start_node.h_cost = calculate_heuristic(self.start_node, self.goal_node, self.heuristic)
        self.start_node.f_cost = self.start_node.g_cost + self.start_node.h_cost

        self.count = 0
        # Priority queue item: (f_cost, count, node)
        self.open_set: List[Tuple[float, int, Node]] = []
        heapq.heappush(self.open_set, (self.start_node.f_cost, self.count, self.start_node))
        self.open_set_hash: Set[Node] = {self.start_node}
        self.closed_set: Set[Node] = set()

    def step(self) -> bool:
        """Perform one iteration of A* expansion."""
        if self.is_finished or not self.open_set:
            self.is_finished = True
            return False

        _, _, current = heapq.heappop(self.open_set)
        self.open_set_hash.discard(current)

        if current == self.goal_node:
            self.reconstruct_path()
            self.is_found = True
            self.is_finished = True
            return False

        self.closed_set.add(current)
        self.visited_count += 1
        if current != self.start_node and current != self.goal_node:
            current.node_type = NodeType.CLOSED

        for neighbor in self.grid.get_neighbors(current):
            if neighbor in self.closed_set:
                continue

            tentative_g = current.g_cost + 1.0  # Unit grid step cost

            if tentative_g < neighbor.g_cost:
                neighbor.parent = current
                neighbor.g_cost = tentative_g
                neighbor.h_cost = calculate_heuristic(neighbor, self.goal_node, self.heuristic)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost

                if neighbor not in self.open_set_hash:
                    self.count += 1
                    heapq.heappush(self.open_set, (neighbor.f_cost, self.count, neighbor))
                    self.open_set_hash.add(neighbor)
                    if neighbor != self.start_node and neighbor != self.goal_node:
                        neighbor.node_type = NodeType.OPEN

        return True


class DijkstraFinder(BasePathfinder):
    """Dijkstra's Algorithm (equivalent to A* with h = 0)."""

    def reset(self) -> None:
        """Initialize priority queue with start node."""
        super().reset()
        self.start_node.g_cost = 0.0
        self.start_node.f_cost = 0.0

        self.count = 0
        self.open_set: List[Tuple[float, int, Node]] = []
        heapq.heappush(self.open_set, (self.start_node.g_cost, self.count, self.start_node))
        self.open_set_hash: Set[Node] = {self.start_node}
        self.closed_set: Set[Node] = set()

    def step(self) -> bool:
        """Perform one iteration of Dijkstra expansion."""
        if self.is_finished or not self.open_set:
            self.is_finished = True
            return False

        _, _, current = heapq.heappop(self.open_set)
        self.open_set_hash.discard(current)

        if current == self.goal_node:
            self.reconstruct_path()
            self.is_found = True
            self.is_finished = True
            return False

        self.closed_set.add(current)
        self.visited_count += 1
        if current != self.start_node and current != self.goal_node:
            current.node_type = NodeType.CLOSED

        for neighbor in self.grid.get_neighbors(current):
            if neighbor in self.closed_set:
                continue

            tentative_g = current.g_cost + 1.0

            if tentative_g < neighbor.g_cost:
                neighbor.parent = current
                neighbor.g_cost = tentative_g
                neighbor.f_cost = tentative_g

                if neighbor not in self.open_set_hash:
                    self.count += 1
                    heapq.heappush(self.open_set, (neighbor.g_cost, self.count, neighbor))
                    self.open_set_hash.add(neighbor)
                    if neighbor != self.start_node and neighbor != self.goal_node:
                        neighbor.node_type = NodeType.OPEN

        return True


class BFSFinder(BasePathfinder):
    """Breadth-First Search (BFS) using FIFO queue."""

    def reset(self) -> None:
        """Initialize FIFO queue with start node."""
        super().reset()
        self.queue: Deque[Node] = deque([self.start_node])
        self.visited: Set[Node] = {self.start_node}

    def step(self) -> bool:
        """Perform one iteration of BFS exploration."""
        if self.is_finished or not self.queue:
            self.is_finished = True
            return False

        current = self.queue.popleft()

        if current == self.goal_node:
            self.reconstruct_path()
            self.is_found = True
            self.is_finished = True
            return False

        self.visited_count += 1
        if current != self.start_node and current != self.goal_node:
            current.node_type = NodeType.CLOSED

        for neighbor in self.grid.get_neighbors(current):
            if neighbor not in self.visited:
                self.visited.add(neighbor)
                neighbor.parent = current
                self.queue.append(neighbor)
                if neighbor != self.start_node and neighbor != self.goal_node:
                    neighbor.node_type = NodeType.OPEN

        return True


class GreedyBestFirstFinder(BasePathfinder):
    """Greedy Best-First Search prioritizing solely by heuristic h(n)."""

    def reset(self) -> None:
        """Initialize priority queue sorted strictly by heuristic h(n)."""
        super().reset()
        self.start_node.h_cost = calculate_heuristic(self.start_node, self.goal_node, self.heuristic)

        self.count = 0
        self.open_set: List[Tuple[float, int, Node]] = []
        heapq.heappush(self.open_set, (self.start_node.h_cost, self.count, self.start_node))
        self.open_set_hash: Set[Node] = {self.start_node}
        self.closed_set: Set[Node] = set()

    def step(self) -> bool:
        """Perform one iteration of Greedy Best-First Search."""
        if self.is_finished or not self.open_set:
            self.is_finished = True
            return False

        _, _, current = heapq.heappop(self.open_set)
        self.open_set_hash.discard(current)

        if current == self.goal_node:
            self.reconstruct_path()
            self.is_found = True
            self.is_finished = True
            return False

        self.closed_set.add(current)
        self.visited_count += 1
        if current != self.start_node and current != self.goal_node:
            current.node_type = NodeType.CLOSED

        for neighbor in self.grid.get_neighbors(current):
            if neighbor in self.closed_set or neighbor in self.open_set_hash:
                continue

            neighbor.parent = current
            neighbor.h_cost = calculate_heuristic(neighbor, self.goal_node, self.heuristic)
            self.count += 1
            heapq.heappush(self.open_set, (neighbor.h_cost, self.count, neighbor))
            self.open_set_hash.add(neighbor)
            if neighbor != self.start_node and neighbor != self.goal_node:
                neighbor.node_type = NodeType.OPEN

        return True
