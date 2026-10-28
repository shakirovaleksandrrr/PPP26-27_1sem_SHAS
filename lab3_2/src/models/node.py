"""Модель узла, представляющая дискретную ячейку на сетке поиска пути."""

from enum import Enum
from typing import Optional, Tuple


class NodeType(Enum):
    """Перечисление типов ячеек и визуальных состояний на сетке."""
    EMPTY = 0
    WALL = 1
    START = 2
    GOAL = 3
    OPEN = 4       # Кандидат в очереди с приоритетом (открытый список)
    CLOSED = 5     # Полностью исследованный узел (закрытый список / посещенные)
    PATH = 6       # Узел восстановленного кратчайшего пути


class Node:
    """Представляет отдельный узел графа с пространственными координатами, стоимостями и состоянием."""

    def __init__(self, row: int, col: int) -> None:
        """Инициализация узла координатами в матрице сетки.

        Аргументы:
            row: Индекс строки в сетке (начиная с 0).
            col: Индекс столбца в сетке (начиная с 0).
        """
        self.row = row
        self.col = col
        self.node_type = NodeType.EMPTY

        # Стоимости для алгоритмов A* и Дейкстры
        self.g_cost: float = float("inf")  # Точное расстояние от старта до данного узла
        self.h_cost: float = 0.0           # Эвристическая оценка расстояния до цели
        self.f_cost: float = float("inf")  # Полная оценочная стоимость: f = g + h
        self.parent: Optional["Node"] = None

    def reset_costs(self) -> None:
        """Сброс расчетных метрик поиска и указателей на родительский узел."""
        self.g_cost = float("inf")
        self.h_cost = 0.0
        self.f_cost = float("inf")
        self.parent = None
        if self.node_type in (NodeType.OPEN, NodeType.CLOSED, NodeType.PATH):
            self.node_type = NodeType.EMPTY

    def reset_all(self) -> None:
        """Сброс всех параметров узла, включая стены, возвращая его в пустое состояние."""
        self.reset_costs()
        self.node_type = NodeType.EMPTY

    @property
    def is_traversable(self) -> bool:
        """Проверка проходимости узла (не является ли узел стеной)."""
        return self.node_type != NodeType.WALL

    def __lt__(self, other: "Node") -> bool:
        """Сравнение узлов для упорядочивания в очереди с приоритетом (heapq).

        Приоритет отдается наименьшему значению f_cost, при равенстве — наименьшему h_cost.
        """
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost

    def __repr__(self) -> str:
        """Возвращает строковое представление узла для отладки."""
        return f"Node({self.row}, {self.col}, type={self.node_type.name})"
