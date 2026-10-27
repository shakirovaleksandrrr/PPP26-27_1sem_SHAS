"""Main application controller integrating grid, pathfinders, canvas renderer, and UI controls."""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional
from src.models.grid import Grid
from src.models.node import Node, NodeType
from src.models.pathfinders import (
    AStarFinder,
    BasePathfinder,
    BFSFinder,
    DijkstraFinder,
    GreedyBestFirstFinder,
    HeuristicType,
)
from src.renderers.grid_renderer import GridRenderer
from src.widgets.controls import ControlsFrame


class PathfindingApp:
    """Coordinates grid model, pathfinding algorithms, rendering, and interactive user input."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize main application window, subsystems, and event bindings.

        Args:
            root: Root Tkinter window instance.
        """
        self.root = root
        self.root.title("Алгоритм A* и поиск пути на сетке — Лабораторная работа 3.2 (Шакиров А. С.)")
        self.root.geometry("1100x780")
        self.root.minsize(900, 650)
        self.root.configure(bg="#12131c")

        self.width = 1100
        self.height = 680
        self.delay_ms = 15
        self.is_running = False

        # 1. Initialize Grid Model (25 rows by 41 cols)
        self.grid = Grid(rows=25, cols=41)

        # 2. Initialize Pathfinder
        self.current_algo_name = "A*"
        self.current_heuristic = HeuristicType.MANHATTAN
        self.finder: BasePathfinder = AStarFinder(self.grid, self.current_heuristic)
        self.status_text = "Готов к запуску"

        # 3. Canvas for Grid Visualization
        self.canvas = tk.Canvas(
            self.root,
            bg="#181926",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.renderer = GridRenderer(self.canvas)

        # 4. Bottom Controls Panel
        self.controls = ControlsFrame(
            master=self.root,
            on_start_toggle=self.on_start_toggle,
            on_step=self.on_step,
            on_reset_search=self.on_reset_search,
            on_clear_all=self.on_clear_all,
            on_generate_maze=self.on_generate_maze,
            on_generate_random=self.on_generate_random,
            on_algorithm_change=self.on_algorithm_change,
            on_heuristic_change=self.on_heuristic_change,
            on_delay_change=self.on_delay_change,
            on_export=self.on_export_map,
            on_import=self.on_import_map,
            initial_algorithm=self.current_algo_name,
            initial_heuristic="Манхэттен",
            initial_delay=self.delay_ms
        )
        self.controls.pack(fill=tk.X, side=tk.BOTTOM)

        # 5. Bind mouse and keyboard events
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.on_mouse_down_left)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag_left)
        self.canvas.bind("<Button-3>", self.on_mouse_down_right)
        self.canvas.bind("<B3-Motion>", self.on_mouse_drag_right)

        self.root.bind("<space>", lambda e: self.on_start_toggle())
        self.root.bind("<n>", lambda e: self.on_step())
        self.root.bind("<N>", lambda e: self.on_step())
        self.root.bind("<r>", lambda e: self.on_reset_search())
        self.root.bind("<R>", lambda e: self.on_reset_search())
        self.root.bind("<c>", lambda e: self.on_clear_all())
        self.root.bind("<C>", lambda e: self.on_clear_all())

        # Initial render
        self.root.after(50, self.draw)

    def on_resize(self, event: tk.Event) -> None:
        """Handle canvas resize."""
        self.width = max(100, event.width)
        self.height = max(100, event.height)
        self.draw()

    def draw(self) -> None:
        """Render current grid state and metrics."""
        self.renderer.render(
            grid=self.grid,
            algorithm_name=self.current_algo_name,
            visited_count=self.finder.visited_count,
            path_length=self.finder.path_length,
            status_text=self.status_text,
            canvas_width=self.width,
            canvas_height=self.height
        )

    def _create_finder(self) -> BasePathfinder:
        """Instantiate selected pathfinding algorithm."""
        if "Дейкстра" in self.current_algo_name:
            return DijkstraFinder(self.grid)
        elif "BFS" in self.current_algo_name:
            return BFSFinder(self.grid)
        elif "Жадный" in self.current_algo_name:
            return GreedyBestFirstFinder(self.grid, self.current_heuristic)
        else:
            return AStarFinder(self.grid, self.current_heuristic)

    def on_algorithm_change(self, algo_name: str) -> None:
        """Handle algorithm selection change."""
        self.stop_search()
        self.current_algo_name = algo_name
        self.finder = self._create_finder()
        self.status_text = f"Выбран алгоритм {algo_name}"
        self.draw()

    def on_heuristic_change(self, heur_name: str) -> None:
        """Handle heuristic distance metric change."""
        self.stop_search()
        if heur_name == "Евклид":
            self.current_heuristic = HeuristicType.EUCLIDEAN
        elif heur_name == "Чебышев":
            self.current_heuristic = HeuristicType.CHEBYSHEV
        else:
            self.current_heuristic = HeuristicType.MANHATTAN

        self.finder = self._create_finder()
        self.status_text = f"Эвристика: {heur_name}"
        self.draw()

    def on_delay_change(self, new_delay: int) -> None:
        """Handle animation speed adjustment."""
        self.delay_ms = new_delay

    def on_start_toggle(self) -> bool:
        """Toggle animation continuous search execution."""
        if self.is_running:
            self.stop_search()
        else:
            if self.finder.is_finished:
                self.finder.reset()
            self.is_running = True
            self.status_text = "Поиск пути..."
            self.controls.set_running_state(True)
            self._search_tick()
        return self.is_running

    def stop_search(self) -> None:
        """Halt continuous animation loop."""
        self.is_running = False
        self.controls.set_running_state(False)

    def on_step(self) -> None:
        """Perform a single step of the pathfinding algorithm."""
        self.stop_search()
        if self.finder.is_finished:
            self.finder.reset()

        has_more = self.finder.step()
        if not has_more:
            if self.finder.is_found:
                self.status_text = f"Путь найден! Длина: {self.finder.path_length}"
            else:
                self.status_text = "Путь не существует!"
        else:
            self.status_text = f"Шаг выполнен (Посещено: {self.finder.visited_count})"
        self.draw()

    def _search_tick(self) -> None:
        """Single tick in continuous search animation loop."""
        if not self.is_running:
            return

        has_more = self.finder.step()
        self.draw()

        if has_more:
            self.root.after(self.delay_ms, self._search_tick)
        else:
            self.stop_search()
            if self.finder.is_found:
                self.status_text = f"Путь найден! Длина: {self.finder.path_length}"
            else:
                self.status_text = "Путь не существует!"
            self.draw()

    def on_reset_search(self) -> None:
        """Clear search trails and reset pathfinder."""
        self.stop_search()
        self.finder.reset()
        self.status_text = "Путь сброшен"
        self.draw()

    def on_clear_all(self) -> None:
        """Clear all walls and search results."""
        self.stop_search()
        self.grid.clear_walls()
        self.finder.reset()
        self.status_text = "Сетка очищена"
        self.draw()

    def on_generate_maze(self) -> None:
        """Generate labyrinth using recursive backtracker."""
        self.stop_search()
        self.grid.generate_maze()
        self.finder = self._create_finder()
        self.status_text = "Сгенерирован лабиринт"
        self.draw()

    def on_generate_random(self) -> None:
        """Generate random obstacle walls."""
        self.stop_search()
        self.grid.generate_random_walls(density=0.25)
        self.finder = self._create_finder()
        self.status_text = "Сгенерированы случайные стены"
        self.draw()

    def on_mouse_down_left(self, event: tk.Event) -> None:
        """Handle left mouse click."""
        cell = self.renderer.screen_to_cell(event.x, event.y, self.grid)
        if not cell:
            return
        row, col = cell

        # Shift + Left click moves Start node
        if event.state & 0x0001:  # Shift mask
            self.grid.set_start(row, col)
            self.on_reset_search()
        else:
            self.grid.toggle_wall(row, col, make_wall=True)
            self.draw()

    def on_mouse_drag_left(self, event: tk.Event) -> None:
        """Handle left mouse drag (paint walls)."""
        cell = self.renderer.screen_to_cell(event.x, event.y, self.grid)
        if cell and not (event.state & 0x0001):
            row, col = cell
            self.grid.toggle_wall(row, col, make_wall=True)
            self.draw()

    def on_mouse_down_right(self, event: tk.Event) -> None:
        """Handle right mouse click."""
        cell = self.renderer.screen_to_cell(event.x, event.y, self.grid)
        if not cell:
            return
        row, col = cell

        # Shift + Right click moves Goal node
        if event.state & 0x0001:  # Shift mask
            self.grid.set_goal(row, col)
            self.on_reset_search()
        else:
            self.grid.toggle_wall(row, col, make_wall=False)
            self.draw()

    def on_mouse_drag_right(self, event: tk.Event) -> None:
        """Handle right mouse drag (erase walls)."""
        cell = self.renderer.screen_to_cell(event.x, event.y, self.grid)
        if cell and not (event.state & 0x0001):
            row, col = cell
            self.grid.toggle_wall(row, col, make_wall=False)
            self.draw()

    def on_export_map(self) -> None:
        """Export current map to a file."""
        filepath = filedialog.asksaveasfilename(
            title="Экспорт карты лабиринта",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            if self.grid.export_to_file(filepath):
                self.status_text = f"Карта сохранена: {filepath}"
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить файл!")
        self.draw()

    def on_import_map(self) -> None:
        """Import map from a text file."""
        filepath = filedialog.askopenfilename(
            title="Импорт карты лабиринта",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            if self.grid.import_from_file(filepath):
                self.finder = self._create_finder()
                self.status_text = f"Карта загружена: {filepath}"
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить файл карты!")
        self.draw()

    def run(self) -> None:
        """Start application mainloop."""
        self.root.mainloop()
