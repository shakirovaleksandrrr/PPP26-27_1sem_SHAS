"""Canvas renderer for drawing 3D stars, warp trails, and telemetry HUD."""

import tkinter as tk
from typing import List, Tuple


class StarRenderer:
    """Renders graphical primitives on Tkinter Canvas."""

    def __init__(self, canvas: tk.Canvas) -> None:
        """Initialize renderer with target canvas.

        Args:
            canvas: Tkinter Canvas widget used for drawing.
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
        """Draw all stars, trails, and HUD telemetry on the canvas.

        Args:
            render_data: List of tuples (curr_x, curr_y, radius, prev_x, prev_y, color).
            warp_trails: Flag indicating whether to draw warp speed light lines.
            width: Viewport width.
            height: Viewport height.
            speed: Current flight speed.
            star_count: Active number of stars.
            is_paused: Pause state flag.
        """
        # Clear canvas before frame drawing
        self.canvas.delete("all")

        # 1. Render stars and warp trails
        for sx, sy, radius, px, py, color in render_data:
            # Skip stars fully off screen to optimize rendering
            if sx < -50 or sx > width + 50 or sy < -50 or sy > height + 50:
                continue

            # Draw warp light trail connecting previous and current projected points
            if warp_trails and speed > 1.0:
                trail_width = max(1, int(radius * 0.7))
                self.canvas.create_line(
                    px, py, sx, sy,
                    fill=color,
                    width=trail_width,
                    capstyle=tk.ROUND
                )

            # Draw star sphere / disk
            r = max(1.0, radius)
            self.canvas.create_oval(
                sx - r, sy - r,
                sx + r, sy + r,
                fill=color,
                outline=""
            )

        # 2. Render Telemetry HUD in top-left corner
        hud_lines = [
            f"Звезд: {star_count}",
            f"Скорость: {speed:.1f} ly/s",
            f"Шлейфы (Warp): {'ВКЛ' if warp_trails else 'ВЫКЛ'}",
            f"Статус: {'ПАУЗА' if is_paused else 'ПОЛЕТ'}"
        ]

        # Semi-transparent HUD background tag
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
