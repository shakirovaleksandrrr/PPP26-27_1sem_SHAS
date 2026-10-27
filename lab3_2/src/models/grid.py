"""Grid model managing discrete nodes, maze generation, and file serialization."""

import random
from pathlib import Path
from typing import List, Optional, Tuple
from src.models.node import Node, NodeType


class Grid:
    """Two-dimensional grid map containing nodes, walls, and endpoints."""

    def __init__(self, rows: int = 25, cols: int = 40) -> None:
        """Initialize grid dimensions and default start/goal positions.

        Args:
            rows: Total vertical count of grid rows.
            cols: Total horizontal count of grid columns.
        """
        self.rows = max(5, rows)
        self.cols = max(5, cols)
        self.nodes: List[List[Node]] = [
            [Node(r, c) for c in range(self.cols)]
            for r in range(self.rows)
        ]

        # Default start (top-left) and goal (bottom-right)
        self.start_node = self.nodes[2][2]
        self.start_node.node_type = NodeType.START

        self.goal_node = self.nodes[self.rows - 3][self.cols - 3]
        self.goal_node.node_type = NodeType.GOAL

    def get_node(self, row: int, col: int) -> Optional[Node]:
        """Safely fetch node by row and col, returning None if out of bounds."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.nodes[row][col]
        return None

    def get_neighbors(self, node: Node) -> List[Node]:
        """Get 4-way orthogonal neighbors (North, South, East, West).

        Args:
            node: Current node.

        Returns:
            List of valid, traversable neighboring nodes.
        """
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            neighbor = self.get_node(node.row + dr, node.col + dc)
            if neighbor is not None and neighbor.is_traversable:
                neighbors.append(neighbor)
        return neighbors

    def set_start(self, row: int, col: int) -> bool:
        """Relocate start point to specified coordinate.

        Args:
            row: Target row index.
            col: Target column index.

        Returns:
            True if position was successfully updated.
        """
        target = self.get_node(row, col)
        if target is None or target == self.goal_node:
            return False

        self.start_node.node_type = NodeType.EMPTY
        self.start_node = target
        self.start_node.node_type = NodeType.START
        self.clear_search()
        return True

    def set_goal(self, row: int, col: int) -> bool:
        """Relocate goal point to specified coordinate.

        Args:
            row: Target row index.
            col: Target column index.

        Returns:
            True if position was successfully updated.
        """
        target = self.get_node(row, col)
        if target is None or target == self.start_node:
            return False

        self.goal_node.node_type = NodeType.EMPTY
        self.goal_node = target
        self.goal_node.node_type = NodeType.GOAL
        self.clear_search()
        return True

    def toggle_wall(self, row: int, col: int, make_wall: bool = True) -> None:
        """Place or erase wall at given cell.

        Args:
            row: Row coordinate.
            col: Column coordinate.
            make_wall: If True, set wall; if False, make empty.
        """
        node = self.get_node(row, col)
        if node is not None and node != self.start_node and node != self.goal_node:
            node.node_type = NodeType.WALL if make_wall else NodeType.EMPTY

    def clear_search(self) -> None:
        """Clear search states (open, closed, path) while keeping walls and endpoints."""
        for row in self.nodes:
            for node in row:
                if node != self.start_node and node != self.goal_node:
                    node.reset_costs()
                else:
                    node.g_cost = float("inf")
                    node.h_cost = 0.0
                    node.f_cost = float("inf")
                    node.parent = None

    def clear_walls(self) -> None:
        """Clear all obstacle walls from the entire grid."""
        for row in self.nodes:
            for node in row:
                if node != self.start_node and node != self.goal_node:
                    node.reset_all()
        self.clear_search()

    def generate_random_walls(self, density: float = 0.25) -> None:
        """Populate grid with random obstacle walls.

        Args:
            density: Fraction of cells converted to walls (0.0 to 0.45).
        """
        self.clear_walls()
        for row in self.nodes:
            for node in row:
                if node != self.start_node and node != self.goal_node:
                    if random.random() < density:
                        node.node_type = NodeType.WALL

    def generate_maze(self) -> None:
        """Generate a labyrinth using the Recursive Backtracker (DFS) algorithm."""
        # 1. Fill entire grid with walls
        for row in self.nodes:
            for node in row:
                node.node_type = NodeType.WALL
                node.reset_costs()

        # 2. Carve corridors starting from (1, 1) with step 2
        start_r, start_c = 1, 1
        stack = [(start_r, start_c)]
        self.nodes[start_r][start_c].node_type = NodeType.EMPTY

        while stack:
            curr_r, curr_c = stack[-1]
            unvisited_neighbors = []

            # Check neighbors 2 steps away
            directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            random.shuffle(directions)

            for dr, dc in directions:
                nr, nc = curr_r + dr, curr_c + dc
                if 1 <= nr < self.rows - 1 and 1 <= nc < self.cols - 1:
                    if self.nodes[nr][nc].node_type == NodeType.WALL:
                        unvisited_neighbors.append((nr, nc, dr // 2, dc // 2))

            if unvisited_neighbors:
                nr, nc, wall_dr, wall_dc = unvisited_neighbors[0]
                # Knock down wall between cells
                self.nodes[curr_r + wall_dr][curr_c + wall_dc].node_type = NodeType.EMPTY
                # Open destination cell
                self.nodes[nr][nc].node_type = NodeType.EMPTY
                stack.append((nr, nc))
            else:
                stack.pop()

        # 3. Ensure start and goal points are clear corridors
        self.start_node = self.nodes[1][1]
        self.start_node.node_type = NodeType.START

        # Find closest open cell for goal near bottom-right
        goal_r = self.rows - 2 if (self.rows - 2) % 2 == 1 else self.rows - 3
        goal_c = self.cols - 2 if (self.cols - 2) % 2 == 1 else self.cols - 3
        self.goal_node = self.nodes[goal_r][goal_c]
        self.goal_node.node_type = NodeType.GOAL

    def export_to_file(self, filepath: str) -> bool:
        """Export current grid map layout to a text file.

        Format:
            '#' = Wall, '.' = Empty, 'S' = Start, 'G' = Goal

        Args:
            filepath: Target file path to write.

        Returns:
            True if export succeeded.
        """
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            for r in range(self.rows):
                row_chars = []
                for c in range(self.cols):
                    node = self.nodes[r][c]
                    if node == self.start_node or node.node_type == NodeType.START:
                        row_chars.append("S")
                    elif node == self.goal_node or node.node_type == NodeType.GOAL:
                        row_chars.append("G")
                    elif node.node_type == NodeType.WALL:
                        row_chars.append("#")
                    else:
                        row_chars.append(".")
                lines.append("".join(row_chars))

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            return True
        except Exception:
            return False

    def import_from_file(self, filepath: str) -> bool:
        """Load and reconstruct grid map from a text file.

        Args:
            filepath: Source text file path.

        Returns:
            True if import succeeded and was valid.
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return False

            with open(path, "r", encoding="utf-8") as f:
                lines = [line.rstrip("\r\n") for line in f if line.strip()]

            if not lines:
                return False

            new_rows = len(lines)
            new_cols = max(len(line) for line in lines)

            new_grid = [
                [Node(r, c) for c in range(new_cols)]
                for r in range(new_rows)
            ]
            new_start = None
            new_goal = None

            for r, line in enumerate(lines):
                for c, char in enumerate(line):
                    node = new_grid[r][c]
                    if char == "#":
                        node.node_type = NodeType.WALL
                    elif char == "S":
                        node.node_type = NodeType.START
                        new_start = node
                    elif char == "G":
                        node.node_type = NodeType.GOAL
                        new_goal = node
                    else:
                        node.node_type = NodeType.EMPTY

            # Apply imported map
            self.rows = new_rows
            self.cols = new_cols
            self.nodes = new_grid
            self.start_node = new_start if new_start else self.nodes[0][0]
            self.start_node.node_type = NodeType.START
            self.goal_node = new_goal if new_goal else self.nodes[new_rows - 1][new_cols - 1]
            self.goal_node.node_type = NodeType.GOAL
            return True
        except Exception:
            return False
