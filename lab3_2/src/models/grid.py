"""Модель сетки, управляющая дискретными узлами, генерацией лабиринтов и сериализацией файлов."""

import random
from pathlib import Path
from typing import List, Optional, Tuple
from src.models.node import Node, NodeType


class Grid:
    """Двумерная карта сетки, содержащая узлы, стены и граничные точки маршрута."""

    def __init__(self, rows: int = 25, cols: int = 40) -> None:
        """Инициализация размеров сетки и расстановка начальных позиций старта и цели.

        Аргументы:
            rows: Общее число строк сетки по вертикали.
            cols: Общее число столбцов сетки по горизонтали.
        """
        self.rows = max(5, rows)
        self.cols = max(5, cols)
        self.nodes: List[List[Node]] = [
            [Node(r, c) for c in range(self.cols)]
            for r in range(self.rows)
        ]

        # Начальные позиции по умолчанию: старт (вверху слева) и цель (внизу справа)
        self.start_node = self.nodes[2][2]
        self.start_node.node_type = NodeType.START

        self.goal_node = self.nodes[self.rows - 3][self.cols - 3]
        self.goal_node.node_type = NodeType.GOAL

    def get_node(self, row: int, col: int) -> Optional[Node]:
        """Безопасное получение узла по индексам строки и столбца, возвращает None при выходе за границы."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.nodes[row][col]
        return None

    def get_neighbors(self, node: Node) -> List[Node]:
        """Получение 4 ортогональных соседей узла (север, юг, запад, восток).

        Аргументы:
            node: Текущий узел.

        Возвращает:
            Список валидных проходимых соседних узлов.
        """
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            neighbor = self.get_node(node.row + dr, node.col + dc)
            if neighbor is not None and neighbor.is_traversable:
                neighbors.append(neighbor)
        return neighbors

    def set_start(self, row: int, col: int) -> bool:
        """Перемещение точки старта в указанную ячейку.

        Аргументы:
            row: Индекс строки.
            col: Индекс столбца.

        Возвращает:
            True, если позиция была успешно обновлена.
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
        """Перемещение целевой точки финиша в указанную ячейку.

        Аргументы:
            row: Индекс строки.
            col: Индекс столбца.

        Возвращает:
            True, если позиция была успешно обновлена.
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
        """Установка или удаление стены в заданной ячейке.

        Аргументы:
            row: Индекс строки.
            col: Индекс столбца.
            make_wall: Если True — ставит стену, если False — делает клетку пустой.
        """
        node = self.get_node(row, col)
        if node is not None and node != self.start_node and node != self.goal_node:
            node.node_type = NodeType.WALL if make_wall else NodeType.EMPTY

    def clear_search(self) -> None:
        """Очистка состояний поиска (открытый/закрытый списки, путь) с сохранением стен и точек."""
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
        """Удаление всех стен-препятствий со всей сетки."""
        for row in self.nodes:
            for node in row:
                if node != self.start_node and node != self.goal_node:
                    node.reset_all()
        self.clear_search()

    def generate_random_walls(self, density: float = 0.25) -> None:
        """Заполнение сетки случайными стенами-препятствиями.

        Аргументы:
            density: Доля ячеек, преобразуемых в стены (от 0.0 до 0.45).
        """
        self.clear_walls()
        for row in self.nodes:
            for node in row:
                if node != self.start_node and node != self.goal_node:
                    if random.random() < density:
                        node.node_type = NodeType.WALL

    def generate_maze(self) -> None:
        """Генерация идеального лабиринта с помощью алгоритма Recursive Backtracker (DFS с возвратом)."""
        # 1. Заполнение всей сетки сплошными стенами
        for row in self.nodes:
            for node in row:
                node.node_type = NodeType.WALL
                node.reset_costs()

        # 2. Прорубание коридоров начиная с координаты (1, 1) с шагом 2
        start_r, start_c = 1, 1
        stack = [(start_r, start_c)]
        self.nodes[start_r][start_c].node_type = NodeType.EMPTY

        while stack:
            curr_r, curr_c = stack[-1]
            unvisited_neighbors = []

            # Проверка соседних клеток через 2 шага
            directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            random.shuffle(directions)

            for dr, dc in directions:
                nr, nc = curr_r + dr, curr_c + dc
                if 1 <= nr < self.rows - 1 and 1 <= nc < self.cols - 1:
                    if self.nodes[nr][nc].node_type == NodeType.WALL:
                        unvisited_neighbors.append((nr, nc, dr // 2, dc // 2))

            if unvisited_neighbors:
                nr, nc, wall_dr, wall_dc = unvisited_neighbors[0]
                # Прорубание стены между текущей и новой ячейками
                self.nodes[curr_r + wall_dr][curr_c + wall_dc].node_type = NodeType.EMPTY
                # Открытие целевой ячейки
                self.nodes[nr][nc].node_type = NodeType.EMPTY
                stack.append((nr, nc))
            else:
                stack.pop()

        # 3. Гарантированное размещение старта и цели в открытых коридорах
        self.start_node = self.nodes[1][1]
        self.start_node.node_type = NodeType.START

        # Поиск ближайшей открытой ячейки для цели в нижнем правом углу
        goal_r = self.rows - 2 if (self.rows - 2) % 2 == 1 else self.rows - 3
        goal_c = self.cols - 2 if (self.cols - 2) % 2 == 1 else self.cols - 3
        self.goal_node = self.nodes[goal_r][goal_c]
        self.goal_node.node_type = NodeType.GOAL

    def export_to_file(self, filepath: str) -> bool:
        """Экспорт текущей карты сетки в текстовый файл.

        Формат:
            '#' = Стена, '.' = Пусто, 'S' = Старт, 'G' = Цель

        Аргументы:
            filepath: Путь к целевому файлу для записи.

        Возвращает:
            True, если экспорт прошел успешно.
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
        """Загрузка и реконструкция карты сетки из текстового файла.

        Аргументы:
            filepath: Путь к исходному файлу.

        Возвращает:
            True, если импорт прошел успешно и файл валиден.
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

            # Применение импортированной карты
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
