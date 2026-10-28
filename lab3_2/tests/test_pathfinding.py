"""Модульные тесты для алгоритмов поиска пути A*, Дейкстры, BFS и модели сетки."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Добавление каталога лабораторной работы в sys.path
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
    """Набор тестов для проверки оптимальности поиска пути и поведения сетки."""

    def setUp(self) -> None:
        """Создание новой чистой сетки перед каждым тестом."""
        self.grid = Grid(rows=12, cols=12)

    def test_heuristics(self) -> None:
        """Проверка формул вычисления расстояний: Манхэттен, Евклид и Чебышев."""
        n1 = Node(0, 0)
        n2 = Node(3, 4)

        # Манхэттенское расстояние: |3-0| + |4-0| = 7.0
        self.assertEqual(calculate_heuristic(n1, n2, HeuristicType.MANHATTAN), 7.0)
        # Евклидово расстояние: sqrt(3^2 + 4^2) = 5.0
        self.assertEqual(calculate_heuristic(n1, n2, HeuristicType.EUCLIDEAN), 5.0)
        # Расстояние Чебышева: max(3, 4) = 4.0
        self.assertEqual(calculate_heuristic(n1, n2, HeuristicType.CHEBYSHEV), 4.0)

    def test_astar_finds_optimal_path(self) -> None:
        """Проверка нахождения алгоритмом A* математически кратчайшего пути на свободной сетке."""
        self.grid.set_start(0, 0)
        self.grid.set_goal(5, 5)

        finder = AStarFinder(self.grid, HeuristicType.MANHATTAN)
        path, is_found = finder.run_all()

        self.assertTrue(is_found)
        # Путь включает начальную и конечную точки, длина = манхэттенское расстояние + 1
        expected_len = abs(5 - 0) + abs(5 - 0) + 1
        self.assertEqual(len(path), expected_len)
        self.assertEqual(path[0], self.grid.start_node)
        self.assertEqual(path[-1], self.grid.goal_node)

    def test_astar_navigates_around_walls(self) -> None:
        """Проверка успешного обхода алгоритмом A* вертикальной стены-препятствия."""
        self.grid.set_start(2, 2)
        self.grid.set_goal(2, 6)

        # Установка вертикальной стены между стартом и целью: колонка 4 с 0 по 4 строки
        for r in range(0, 5):
            self.grid.toggle_wall(r, 4, make_wall=True)

        finder = AStarFinder(self.grid, HeuristicType.MANHATTAN)
        path, is_found = finder.run_all()

        self.assertTrue(is_found)
        self.assertGreater(len(path), 0)
        # Путь не должен содержать ни одного узла-стены
        for node in path:
            self.assertNotEqual(node.node_type, NodeType.WALL)

    def test_astar_unreachable_goal(self) -> None:
        """Проверка корректной обработки ситуации при полностью заблокированной цели."""
        self.grid.set_start(0, 0)
        self.grid.set_goal(2, 2)

        # Окружение цели сплошным кольцом стен
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.grid.toggle_wall(2 + dr, 2 + dc, make_wall=True)

        finder = AStarFinder(self.grid)
        path, is_found = finder.run_all()

        self.assertFalse(is_found)
        self.assertEqual(len(path), 0)

    def test_dijkstra_finds_same_optimal_length(self) -> None:
        """Проверка совпадения длины кратчайшего пути у алгоритма Дейкстры и A*."""
        self.grid.set_start(1, 1)
        self.grid.set_goal(8, 8)
        # Установка Г-образного препятствия
        for r in range(3, 7):
            self.grid.toggle_wall(r, 5, make_wall=True)

        # Запуск A*
        astar = AStarFinder(self.grid)
        astar_path, astar_found = astar.run_all()

        # Запуск Дейкстры на той же конфигурации
        self.grid.clear_search()
        dijkstra = DijkstraFinder(self.grid)
        dijkstra_path, dijkstra_found = dijkstra.run_all()

        self.assertTrue(astar_found)
        self.assertTrue(dijkstra_found)
        self.assertEqual(len(astar_path), len(dijkstra_path))
        # Алгоритм A* с эвристикой исследует меньше либо столько же узлов, сколько Дейкстра
        self.assertLessEqual(astar.visited_count, dijkstra.visited_count)

    def test_bfs_finds_path(self) -> None:
        """Проверка нахождения корректного пути алгоритмом поиска в ширину (BFS)."""
        self.grid.set_start(0, 0)
        self.grid.set_goal(4, 4)

        bfs = BFSFinder(self.grid)
        path, is_found = bfs.run_all()

        self.assertTrue(is_found)
        self.assertEqual(len(path), 9)

    def test_maze_generator(self) -> None:
        """Проверка генерации связного пути в лабиринте (Recursive Backtracker)."""
        maze_grid = Grid(rows=15, cols=15)
        maze_grid.generate_maze()

        finder = AStarFinder(maze_grid)
        path, is_found = finder.run_all()

        self.assertTrue(is_found)
        self.assertGreater(len(path), 0)

    def test_grid_export_and_import(self) -> None:
        """Проверка сериализации карты в текстовый файл и ее точного восстановления."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            self.grid.set_start(1, 1)
            self.grid.set_goal(5, 5)
            self.grid.toggle_wall(2, 3, make_wall=True)
            self.grid.toggle_wall(3, 3, make_wall=True)

            # Экспорт карты в файл
            self.assertTrue(self.grid.export_to_file(tmp_path))

            # Импорт карты в новый экземпляр сетки
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
