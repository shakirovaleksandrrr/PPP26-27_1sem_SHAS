"""Рендерер холста для отрисовки 3D-звезд, световых шлейфов и телеметрии HUD."""

import tkinter as tk
from typing import List, Tuple


class StarRenderer:
    """Отрисовывает графические примитивы на Tkinter Canvas."""

    def __init__(self, canvas: tk.Canvas) -> None:
        """Инициализация рендерера целевым холстом.

        Аргументы:
            canvas: Экземпляр виджета Tkinter Canvas, используемый для отрисовки.
        """
        self.canvas = canvas

    def render(
        self,
        render_data: List[Tuple[float, float, float, float, float, str]],
        warp_trails: bool,
        width: float,
        height: float,
        speed: float,
        star_count: int,
        is_paused: bool
    ) -> None:
        """Отрисовка всех звезд, шлейфов гиперпрыжка и телеметрии на холсте.

        Аргументы:
            render_data: Список кортежей (curr_x, curr_y, radius, prev_x, prev_y, color).
            warp_trails: Флаг отображения световых шлейфов гиперпрыжка.
            width: Ширина области просмотра.
            height: Высота области просмотра.
            speed: Текущая скорость полета.
            star_count: Число активных звезд.
            is_paused: Флаг состояния паузы.
        """
        # Очистка холста перед отрисовкой текущего кадра
        self.canvas.delete("all")

        # 1. Отрисовка звезд и световых шлейфов
        for sx, sy, radius, px, py, color in render_data:
            # Пропуск звезд, находящихся далеко за пределами экрана, для оптимизации FPS
            if sx < -50 or sx > width + 50 or sy < -50 or sy > height + 50:
                continue

            # Отрисовка светового шлейфа от предыдущей к текущей позиции
            if warp_trails and speed > 1.0:
                trail_width = max(1, int(radius * 0.7))
                self.canvas.create_line(
                    px, py, sx, sy,
                    fill=color,
                    width=trail_width,
                    capstyle=tk.ROUND
                )

            # Отрисовка диска звезды
            r = max(1.0, radius)
            self.canvas.create_oval(
                sx - r, sy - r,
                sx + r, sy + r,
                fill=color,
                outline=""
            )

        # 2. Отрисовка информационной панели телеметрии в верхнем левом углу
        hud_lines = [
            f"Звезд: {star_count}",
            f"Скорость: {speed:.1f} ly/s",
            f"Шлейфы (Warp): {'ВКЛ' if warp_trails else 'ВЫКЛ'}",
            f"Статус: {'ПАУЗА' if is_paused else 'ПОЛЕТ'}"
        ]

        y_pos = 20
        for text in hud_lines:
            self.canvas.create_text(
                20, y_pos,
                text=text,
                anchor="w",
                fill="#4fc3f7" if "ПОЛЕТ" in text else "#cfd8dc",
                font=("Consolas", 10, "bold")
            )
            y_pos += 20
