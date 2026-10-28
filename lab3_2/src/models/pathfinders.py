"""Реализация алгоритмов поиска пути на сетке: A*, Дейкстра, BFS и жадный поиск (Greedy Best-First)."""

import heapq
import math
from collections import deque
from enum import Enum
from typing import Callable, Deque, Dict, Generator, List, Optional, Set, Tuple
from src.models.grid import Grid
from src.models.node import Node, NodeType


class HeuristicType(Enum):
    """Поддерживаемые эвристики расстояния для информированного поиска."""
    MANHATTAN = "Манхэттен"
    EUCLIDEAN = "Евклид"
    CHEBYSHEV = "Чебышев"


def calculate_heuristic(n1: Node, n2: Node, h_type: HeuristicType = HeuristicType.MANHATTAN) -> float:
    """Вычисление эвристической оценки расстояния между двумя узлами сетки.

    Аргументы:
        n1: Исходный узел.
        n2: Целевой узел назначения.
        h_type: Метрика расстояния.

    Возвращает:
        Оценочное расстояние в виде числа с плавающей точкой.
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
    """Абстрактный базовый класс для алгоритмов поиска пути на дискретной сетке."""

    def __init__(self, grid: Grid, heuristic: HeuristicType = HeuristicType.MANHATTAN) -> None:
        """Инициализация алгоритма поиска на заданной сетке.

        Аргументы:
            grid: Экземпляр модели сетки Grid.
            heuristic: Используемая эвристическая функция расстояния.
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
        """Сброс внутренних структур данных поиска и подготовка начального фронта."""
        self.grid.clear_search()
        self.start_node = self.grid.start_node
        self.goal_node = self.grid.goal_node
        self.is_finished = False
        self.is_found = False
        self.visited_count = 0
        self.path_length = 0
        self.path = []

    def reconstruct_path(self) -> List[Node]:
        """Восстановление кратчайшего пути по цепочке родительских указателей от цели к старту.

        Возвращает:
            Упорядоченный список узлов, образующих маршрут от старта к цели.
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
        """Выполнение одной дискретной итерации алгоритма поиска.

        Возвращает:
            True, если поиск продолжается; False, если поиск завершен.
        """
        raise NotImplementedError

    def run_all(self) -> Tuple[List[Node], bool]:
        """Немедленное выполнение поиска до полного завершения.

        Возвращает:
            Кортеж (восстановленный_путь, флаг_успеха).
        """
        while self.step():
            pass
        return self.path, self.is_found


class AStarFinder(BasePathfinder):
    """Алгоритм A* (f = g + h). Гарантирует нахождение математически кратчайшего пути."""

    def reset(self) -> None:
        """Инициализация очереди с приоритетом начальным узлом."""
        super().reset()
        self.start_node.g_cost = 0.0
        self.start_node.h_cost = calculate_heuristic(self.start_node, self.goal_node, self.heuristic)
        self.start_node.f_cost = self.start_node.g_cost + self.start_node.h_cost

        self.count = 0
        # Элемент очереди с приоритетом: (f_cost, счетчик_добавления, узел)
        self.open_set: List[Tuple[float, int, Node]] = []
        heapq.heappush(self.open_set, (self.start_node.f_cost, self.count, self.start_node))
        self.open_set_hash: Set[Node] = {self.start_node}
        self.closed_set: Set[Node] = set()

    def step(self) -> bool:
        """Выполнение одной итерации раскрытия узла алгоритмом A*."""
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

            tentative_g = current.g_cost + 1.0  # Единичная стоимость шага по сетке

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
    """Алгоритм Дейкстры (эквивалентен A* с эвристикой h = 0)."""

    def reset(self) -> None:
        """Инициализация очереди с приоритетом начальным узлом со стоимостью 0."""
        super().reset()
        self.start_node.g_cost = 0.0
        self.start_node.f_cost = 0.0

        self.count = 0
        self.open_set: List[Tuple[float, int, Node]] = []
        heapq.heappush(self.open_set, (self.start_node.g_cost, self.count, self.start_node))
        self.open_set_hash: Set[Node] = {self.start_node}
        self.closed_set: Set[Node] = set()

    def step(self) -> bool:
        """Выполнение одной итерации раскрытия узла алгоритмом Дейкстры."""
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
    """Поиск в ширину (BFS) с использованием очереди FIFO."""

    def reset(self) -> None:
        """Инициализация очереди FIFO начальным узлом."""
        super().reset()
        self.queue: Deque[Node] = deque([self.start_node])
        self.visited: Set[Node] = {self.start_node}

    def step(self) -> bool:
        """Выполнение одной итерации исследования в ширину."""
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
    """Жадный поиск по первому наилучшему совпадению (сортировка строго по h(n))."""

    def reset(self) -> None:
        """Инициализация очереди с приоритетом, отсортированной исключительно по оценке h(n)."""
        super().reset()
        self.start_node.h_cost = calculate_heuristic(self.start_node, self.goal_node, self.heuristic)

        self.count = 0
        self.open_set: List[Tuple[float, int, Node]] = []
        heapq.heappush(self.open_set, (self.start_node.h_cost, self.count, self.start_node))
        self.open_set_hash: Set[Node] = {self.start_node}
        self.closed_set: Set[Node] = set()

    def step(self) -> bool:
        """Выполнение одной итерации жадного поиска."""
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
