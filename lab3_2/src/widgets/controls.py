"""Control panel widget for configuring pathfinding algorithms, maze generation, and animation."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List


class ControlsFrame(tk.Frame):
    """Bottom control panel with interactive UI controls for algorithm manipulation."""

    def __init__(
        self,
        master: tk.Widget,
        on_start_toggle: Callable[[], bool],
        on_step: Callable[[], None],
        on_reset_search: Callable[[], None],
        on_clear_all: Callable[[], None],
        on_generate_maze: Callable[[], None],
        on_generate_random: Callable[[], None],
        on_algorithm_change: Callable[[str], None],
        on_heuristic_change: Callable[[str], None],
        on_delay_change: Callable[[int], None],
        on_export: Callable[[], None],
        on_import: Callable[[], None],
        initial_algorithm: str = "A*",
        initial_heuristic: str = "Манхэттен",
        initial_delay: int = 15
    ) -> None:
        """Initialize controls panel and action triggers.

        Args:
            master: Parent widget.
            on_start_toggle: Callback for Start/Pause toggle button.
            on_step: Callback for single step button.
            on_reset_search: Callback for resetting path.
            on_clear_all: Callback for clearing walls and field.
            on_generate_maze: Callback for maze generation.
            on_generate_random: Callback for random walls generation.
            on_algorithm_change: Callback when user picks a different algorithm.
            on_heuristic_change: Callback when user picks a different distance metric.
            on_delay_change: Callback for animation speed slider.
            on_export: Callback for exporting map file.
            on_import: Callback for importing map file.
            initial_algorithm: Selected algorithm default name.
            initial_heuristic: Selected heuristic default name.
            initial_delay: Default delay in milliseconds.
        """
        super().__init__(master, bg="#181926", padx=12, pady=10)

        self.on_start_toggle = on_start_toggle
        self.on_step = on_step
        self.on_reset_search = on_reset_search
        self.on_clear_all = on_clear_all
        self.on_generate_maze = on_generate_maze
        self.on_generate_random = on_generate_random
        self.on_algorithm_change = on_algorithm_change
        self.on_heuristic_change = on_heuristic_change
        self.on_delay_change = on_delay_change
        self.on_export = on_export
        self.on_import = on_import

        lbl_font = ("Segoe UI", 9, "bold")
        btn_font = ("Segoe UI", 9, "bold")
        lbl_fg = "#cad3f5"

        # Row 1: Algorithm & Heuristic Selectors
        top_row = tk.Frame(self, bg="#181926")
        top_row.pack(fill=tk.X, pady=(0, 6))

        # 1. Algorithm Dropdown
        tk.Label(top_row, text="Алгоритм:", font=lbl_font, fg=lbl_fg, bg="#181926").pack(side=tk.LEFT, padx=(5, 3))
        self.algo_var = tk.StringVar(value=initial_algorithm)
        algo_options = ["A*", "Дейкстра (Dijkstra)", "BFS (Поиск в ширину)", "Жадный (Greedy Best-First)"]
        self.algo_menu = ttk.Combobox(
            top_row,
            textvariable=self.algo_var,
            values=algo_options,
            state="readonly",
            width=26
        )
        self.algo_menu.pack(side=tk.LEFT, padx=5)
        self.algo_menu.bind("<<ComboboxSelected>>", self._handle_algo_change)

        # 2. Heuristic Dropdown
        tk.Label(top_row, text="Эвристика:", font=lbl_font, fg=lbl_fg, bg="#181926").pack(side=tk.LEFT, padx=(15, 3))
        self.heur_var = tk.StringVar(value=initial_heuristic)
        heur_options = ["Манхэттен", "Евклид", "Чебышев"]
        self.heur_menu = ttk.Combobox(
            top_row,
            textvariable=self.heur_var,
            values=heur_options,
            state="readonly",
            width=14
        )
        self.heur_menu.pack(side=tk.LEFT, padx=5)
        self.heur_menu.bind("<<ComboboxSelected>>", self._handle_heur_change)

        # 3. Speed / Delay Slider
        tk.Label(top_row, text="Задержка (мс):", font=lbl_font, fg=lbl_fg, bg="#181926").pack(side=tk.LEFT, padx=(15, 3))
        self.delay_slider = tk.Scale(
            top_row,
            from_=1,
            to=80,
            orient=tk.HORIZONTAL,
            length=140,
            bg="#24273a",
            fg="#8aadf4",
            troughcolor="#11121d",
            highlightthickness=0,
            command=lambda v: self.on_delay_change(int(float(v)))
        )
        self.delay_slider.set(initial_delay)
        self.delay_slider.pack(side=tk.LEFT, padx=5)

        # Row 2: Action Buttons
        bot_row = tk.Frame(self, bg="#181926")
        bot_row.pack(fill=tk.X)

        self.btn_start = tk.Button(
            bot_row,
            text="▶ Старт (Space)",
            command=self._handle_start_click,
            font=btn_font,
            bg="#a6da95",
            fg="#181926",
            activebackground="#8bd5ca",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_start.pack(side=tk.LEFT, padx=4)

        self.btn_step = tk.Button(
            bot_row,
            text="⏯ Шаг (N)",
            command=self.on_step,
            font=btn_font,
            bg="#363a4f",
            fg="#cad3f5",
            activebackground="#494d64",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_step.pack(side=tk.LEFT, padx=4)

        self.btn_reset = tk.Button(
            bot_row,
            text="Сбросить путь (R)",
            command=self.on_reset_search,
            font=btn_font,
            bg="#363a4f",
            fg="#eed49f",
            activebackground="#494d64",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        self.btn_clear = tk.Button(
            bot_row,
            text="Очистить стены (C)",
            command=self.on_clear_all,
            font=btn_font,
            bg="#ed8796",
            fg="#181926",
            activebackground="#ee99a0",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_clear.pack(side=tk.LEFT, padx=4)

        # Maze and Map I/O tools on right
        self.btn_export = tk.Button(
            bot_row,
            text="💾 Экспорт",
            command=self.on_export,
            font=btn_font,
            bg="#363a4f",
            fg="#cad3f5",
            activebackground="#494d64",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_export.pack(side=tk.RIGHT, padx=4)

        self.btn_import = tk.Button(
            bot_row,
            text="📂 Импорт",
            command=self.on_import,
            font=btn_font,
            bg="#363a4f",
            fg="#cad3f5",
            activebackground="#494d64",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_import.pack(side=tk.RIGHT, padx=4)

        self.btn_maze = tk.Button(
            bot_row,
            text="🧩 Лабиринт",
            command=self.on_generate_maze,
            font=btn_font,
            bg="#c6a0f6",
            fg="#181926",
            activebackground="#b7bdf8",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_maze.pack(side=tk.RIGHT, padx=4)

        self.btn_random = tk.Button(
            bot_row,
            text="🎲 Случайные стены",
            command=self.on_generate_random,
            font=btn_font,
            bg="#363a4f",
            fg="#cad3f5",
            activebackground="#494d64",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_random.pack(side=tk.RIGHT, padx=4)

    def _handle_algo_change(self, event: tk.Event) -> None:
        """Handle algorithm selection change."""
        self.on_algorithm_change(self.algo_var.get())

    def _handle_heur_change(self, event: tk.Event) -> None:
        """Handle heuristic selection change."""
        self.on_heuristic_change(self.heur_var.get())

    def _handle_start_click(self) -> None:
        """Handle start/pause toggle click."""
        is_running = self.on_start_toggle()
        self.set_running_state(is_running)

    def set_running_state(self, is_running: bool) -> None:
        """Update start button label and color depending on running state."""
        if is_running:
            self.btn_start.config(text="⏸ Пауза (Space)", bg="#f5a97f", fg="#181926")
        else:
            self.btn_start.config(text="▶ Старт (Space)", bg="#a6da95", fg="#181926")
