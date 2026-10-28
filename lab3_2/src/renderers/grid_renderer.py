"""Рендерер сетки для отрисовки узлов, стен, состояний поиска и телеметрии HUD."""

import tkinter as tk
from typing import Optional, Tuple
from src.models.grid import Grid
from src.models.node import Node, NodeType

# Цветовая палитра для состояний ячеек (темная тема)
COLORS = {
    NodeType.EMPTY: "#1e2030",
    NodeType.WALL: "#11121d",
    NodeType.START: "#a6da95",    # Зеленый (старт)
    NodeType.GOAL: "#ed8796",     # Красный (цель)
    NodeType.OPEN: "#8aadf4",     # Голубой (открытый список / кандидаты)
    NodeType.CLOSED: "#5b6078",   # Сине-серый (закрытый список / посещенные)
    NodeType.PATH: "#eed49f",     # Золотистый (кратчайший путь)
}


class GridRenderer:
    """Отрисовывает 2D-сетку, процесс поиска и найденный маршрут на Tkinter Canvas."""

    def __init__(self, canvas: tk.Canvas) -> None:
        """Инициализация рендерера целевым холстом Tkinter Canvas.

        Аргументы:
            canvas: Экземпляр виджета Tkinter Canvas.
        """
        self.canvas = canvas
        self.cell_size: int = 24
        self.offset_x: int = 10
        self.offset_y: int = 40

    def compute_layout(self, grid: Grid, canvas_width: int, canvas_height: int) -> None:
        """Расчет оптимального размера ячеек и отступов для центрирования сетки.

        Аргументы:
            grid: Модель сетки Grid.
            canvas_width: Доступная ширина холста в пикселях.
            canvas_height: Доступная высота холста в пикселях.
        """
        top_bar_height = 45
        avail_w = max(100, canvas_width - 20)
        avail_h = max(100, canvas_height - top_bar_height - 20)

        size_w = avail_w // grid.cols
        size_h = avail_h // grid.rows
        self.cell_size = max(10, min(size_w, size_h))

        grid_w = self.cell_size * grid.cols
        grid_h = self.cell_size * grid.rows

        self.offset_x = max(10, (canvas_width - grid_w) // 2)
        self.offset_y = max(top_bar_height, (canvas_height - top_bar_height - grid_h) // 2 + top_bar_height)

    def screen_to_cell(self, screen_x: int, screen_y: int, grid: Grid) -> Optional[Tuple[int, int]]:
        """Преобразование пиксельных экранных координат мыши в индексы (row, col) сетки.

        Аргументы:
            screen_x: Экранная координата X.
            screen_y: Экранная координата Y.
            grid: Модель сетки.

        Возвращает:
            Кортеж (row, col) или None, если клик совершен вне сетки.
        """
        col = (screen_x - self.offset_x) // self.cell_size
        row = (screen_y - self.offset_y) // self.cell_size
        if 0 <= row < grid.rows and 0 <= col < grid.cols:
            return row, col
        return None

    def render(
        self,
        grid: Grid,
        algorithm_name: str,
        visited_count: int,
        path_length: int,
        status_text: str,
        canvas_width: int,
        canvas_height: int
    ) -> None:
        """Отрисовка всей сетки, состояний ячеек и телеметрии на холсте.

        Аргументы:
            grid: Модель сетки, содержащая узлы.
            algorithm_name: Название текущего выбранного алгоритма.
            visited_count: Число исследованных узлов в закрытом списке.
            path_length: Число шагов в итоговом найденном пути.
            status_text: Текстовое описание текущего статуса симуляции.
            canvas_width: Ширина холста.
            canvas_height: Высота холста.
        """
        self.canvas.delete("all")
        self.compute_layout(grid, canvas_width, canvas_height)

        # 1. Отрисовка верхней информационной панели (HUD)
        hud_text = (
            f"Алгоритм: {algorithm_name}  |  "
            f"Посещено ячеек: {visited_count}  |  "
            f"Длина пути: {path_length}  |  "
            f"Статус: {status_text}"
        )
        self.canvas.create_text(
            20, 22,
            text=hud_text,
            anchor="w",
            fill="#cad3f5",
            font=("Consolas", 11, "bold")
        )

        # 2. Отрисовка ячеек сетки
        cs = self.cell_size
        ox = self.offset_x
        oy = self.offset_y

        for r in range(grid.rows):
            for c in range(grid.cols):
                node = grid.nodes[r][c]
                x1 = ox + c * cs
                y1 = oy + r * cs
                x2 = x1 + cs
                y2 = y1 + cs

                cell_color = COLORS.get(node.node_type, "#1e2030")

                # Прямоугольник ячейки
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=cell_color,
                    outline="#24273a",
                    width=1
                )

                # Специальные маркеры для старта (S) и цели (G)
                if node.node_type == NodeType.START:
                    pad = max(2, cs // 4)
                    self.canvas.create_oval(
                        x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                        fill="#24273a", outline=""
                    )
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="S", fill="#a6da95", font=("Segoe UI", max(8, cs // 2), "bold")
                    )
                elif node.node_type == NodeType.GOAL:
                    pad = max(2, cs // 4)
                    self.canvas.create_oval(
                        x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                        fill="#24273a", outline=""
                    )
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="G", fill="#ed8796", font=("Segoe UI", max(8, cs // 2), "bold")
                    )
