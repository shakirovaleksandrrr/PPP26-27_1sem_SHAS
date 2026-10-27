"""Unit tests for A*, Dijkstra, BFS pathfinding and grid models."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure lab3_2 directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.grid import Grid
from src.models.node import Node, NodeType
from src.models.pathfinders import (
    AStarFinder,
    BFSFinder,
    DijkstraFinder,
    GreedyBestFirstFinder,
    HeuristicType,
    calculate_heuristic,
)


class TestPathfindingAlgorithms(unittest.TestCase):
    """Test suite verifying pathfinding optimality and grid behavior."""

    def setUp(self) -> None:
        """Create fresh grid for each test."""
        self.grid = Grid(rows=12, cols=12)

    def test_heuristics(self) -> None:
        """Verify distance formulas for Manhattan, Euclidean, and Chebyshev metrics."""
        n1 = Node(0, 0)
        n2 = Node(3, 4)

        # Manhattan: |3-0| + |4-0| = 7.0
        self.assertEqual(calculate_heuristic(n1, n2, HeuristicType.MANHATTAN), 7.0)
        # Euclidean: sqrt(3^2 + 4^2) = 5.0
        self.assertEqual(calculate_heuristic(n1, n2, HeuristicType.EUCLIDEAN), 5.0)
        # Chebyshev: max(3, 4) = 4.0
        self.assertEqual(calculate_heuristic(n1, n2, HeuristicType.CHEBYSHEV), 4.0)

    def test_astar_finds_optimal_path(self) -> None:
        """Verify A* finds the mathematically shortest route on unobstructed grid."""
        self.grid.set_start(0, 0)
        self.grid.set_goal(5, 5)

        finder = AStarFinder(self.grid, HeuristicType.MANHATTAN)
        path, is_found = finder.run_all()

        self.assertTrue(is_found)
        # Path includes start and goal, so length is Manhattan distance + 1
        expected_len = abs(5 - 0) + abs(5 - 0) + 1
        self.assertEqual(len(path), expected_len)
        self.assertEqual(path[0], self.grid.start_node)
        self.assertEqual(path[-1], self.grid.goal_node)

    def test_astar_navigates_around_walls(self) -> None:
        """Verify A* successfully routes around a blocking vertical wall."""
        self.grid.set_start(2, 2)
        self.grid.set_goal(2, 6)

        # Place vertical wall between start and goal: col 4 from row 0 to 4
        for r in range(0, 5):
            self.grid.toggle_wall(r, 4, make_wall=True)

        finder = AStarFinder(self.grid, HeuristicType.MANHATTAN)
        path, is_found = finder.run_all()

        self.assertTrue(is_found)
        self.assertGreater(len(path), 0)
        # Path must not traverse any wall
        for node in path:
            self.assertNotEqual(node.node_type, NodeType.WALL)

    def test_astar_unreachable_goal(self) -> None:
        """Verify A* handles completely blocked goals gracefully."""
        self.grid.set_start(0, 0)
        self.grid.set_goal(2, 2)

        # Enclose goal with surrounding walls
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.grid.toggle_wall(2 + dr, 2 + dc, make_wall=True)

        finder = AStarFinder(self.grid)
        path, is_found = finder.run_all()

        self.assertFalse(is_found)
        self.assertEqual(len(path), 0)

    def test_dijkstra_finds_same_optimal_length(self) -> None:
        """Verify Dijkstra finds the identical optimal shortest path length as A*."""
        self.grid.set_start(1, 1)
        self.grid.set_goal(8, 8)
        # Place an L-shaped obstacle
        for r in range(3, 7):
            self.grid.toggle_wall(r, 5, make_wall=True)

        # Run A*
        astar = AStarFinder(self.grid)
        astar_path, astar_found = astar.run_all()

        # Run Dijkstra on identical obstacle grid
        self.grid.clear_search()
        dijkstra = DijkstraFinder(self.grid)
        dijkstra_path, dijkstra_found = dijkstra.run_all()

        self.assertTrue(astar_found)
        self.assertTrue(dijkstra_found)
        self.assertEqual(len(astar_path), len(dijkstra_path))
        # A* with heuristic typically visits fewer or equal nodes than uninformed Dijkstra
        self.assertLessEqual(astar.visited_count, dijkstra.visited_count)

    def test_bfs_finds_path(self) -> None:
        """Verify Breadth-First Search finds the optimal hop count."""
        self.grid.set_start(0, 0)
        self.grid.set_goal(4, 4)

        bfs = BFSFinder(self.grid)
        path, is_found = bfs.run_all()

        self.assertTrue(is_found)
        self.assertEqual(len(path), 9)

    def test_maze_generator(self) -> None:
        """Verify recursive backtracker maze produces valid connected path."""
        # Use odd dimensions for maze carving
        maze_grid = Grid(rows=15, cols=15)
        maze_grid.generate_maze()

        finder = AStarFinder(maze_grid)
        path, is_found = finder.run_all()

        self.assertTrue(is_found)
        self.assertGreater(len(path), 0)

    def test_grid_export_and_import(self) -> None:
        """Verify map serializing to disk and reconstructing preserves structure."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            self.grid.set_start(1, 1)
            self.grid.set_goal(5, 5)
            self.grid.toggle_wall(2, 3, make_wall=True)
            self.grid.toggle_wall(3, 3, make_wall=True)

            # Export
            self.assertTrue(self.grid.export_to_file(tmp_path))

            # Import into new grid
            new_grid = Grid(rows=5, cols=5)
            self.assertTrue(new_grid.import_from_file(tmp_path))

            self.assertEqual(new_grid.rows, self.grid.rows)
            self.assertEqual(new_grid.cols, self.grid.cols)
            self.assertEqual(new_grid.start_node.row, 1)
            self.assertEqual(new_grid.start_node.col, 1)
            self.assertEqual(new_grid.goal_node.row, 5)
            self.assertEqual(new_grid.goal_node.col, 5)
            self.assertEqual(new_grid.nodes[2][3].node_type, NodeType.WALL)
            self.assertEqual(new_grid.nodes[3][3].node_type, NodeType.WALL)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
