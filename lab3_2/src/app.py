"""Главный контроллер приложения, объединяющий модель сетки, алгоритмы поиска, рендерер и элементы управления."""

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
    """Координирует модель сетки, алгоритмы поиска пути, визуализацию и интерактивный ввод пользователя."""

    def __init__(self, root: tk.Tk) -> None:
        """Инициализация главного окна приложения, подсистем и привязок событий.

        Аргументы:
            root: Экземпляр корневого окна Tkinter.
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

        # 1. Инициализация модели сетки (25 строк на 41 столбец)
        self.grid = Grid(rows=25, cols=41)

        # 2. Инициализация алгоритма поиска по умолчанию (A*)
        self.current_algo_name = "A*"
        self.current_heuristic = HeuristicType.MANHATTAN
        self.finder: BasePathfinder = AStarFinder(self.grid, self.current_heuristic)
        self.status_text = "Готов к запуску"

        # 3. Холст для визуализации сетки
        self.canvas = tk.Canvas(
            self.root,
            bg="#181926",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.renderer = GridRenderer(self.canvas)

        # 4. Нижняя панель управления
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

        # 5. Привязка событий мыши и клавиатуры
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

        # Первоначальная отрисовка
        self.root.after(50, self.draw)

    def on_resize(self, event: tk.Event) -> None:
        """Обработка изменения размера холста."""
        self.width = max(100, event.width)
        self.height = max(100, event.height)
        self.draw()

    def draw(self) -> None:
        """Отрисовка текущего состояния сетки, маршрута и телеметрии."""
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
        """Создание экземпляра выбранного пользователем алгоритма поиска."""
        if "Дейкстра" in self.current_algo_name:
            return DijkstraFinder(self.grid)
        elif "BFS" in self.current_algo_name:
            return BFSFinder(self.grid)
        elif "Жадный" in self.current_algo_name:
            return GreedyBestFirstFinder(self.grid, self.current_heuristic)
        else:
            return AStarFinder(self.grid, self.current_heuristic)

    def on_algorithm_change(self, algo_name: str) -> None:
        """Обработка переключения алгоритма поиска."""
        self.stop_search()
        self.current_algo_name = algo_name
        self.finder = self._create_finder()
        self.status_text = f"Выбран алгоритм {algo_name}"
        self.draw()

    def on_heuristic_change(self, heur_name: str) -> None:
        """Обработка смены эвристики расстояния."""
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
        """Обработка изменения скорости анимации со слайдера."""
        self.delay_ms = new_delay

    def on_start_toggle(self) -> bool:
        """Переключение непрерывного выполнения анимации поиска пути."""
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
        """Остановка непрерывного цикла анимации."""
        self.is_running = False
        self.controls.set_running_state(False)

    def on_step(self) -> None:
        """Выполнение одного дискретного шага алгоритма поиска пути."""
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
        """Один такт непрерывного цикла анимации поиска."""
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
        """Сброс исследованных узлов и найденного пути."""
        self.stop_search()
        self.finder.reset()
        self.status_text = "Путь сброшен"
        self.draw()

    def on_clear_all(self) -> None:
        """Очистка всех стен и результатов поиска."""
        self.stop_search()
        self.grid.clear_walls()
        self.finder.reset()
        self.status_text = "Сетка очищена"
        self.draw()

    def on_generate_maze(self) -> None:
        """Генерация лабиринта алгоритмом Recursive Backtracker."""
        self.stop_search()
        self.grid.generate_maze()
        self.finder = self._create_finder()
        self.status_text = "Сгенерирован лабиринт"
        self.draw()

    def on_generate_random(self) -> None:
        """Генерация случайных стен-препятствий."""
        self.stop_search()
        self.grid.generate_random_walls(density=0.25)
        self.finder = self._create_finder()
        self.status_text = "Сгенерированы случайные стены"
        self.draw()

    def on_mouse_down_left(self, event: tk.Event) -> None:
        """Обработка клика левой кнопкой мыши."""
        cell = self.renderer.screen_to_cell(event.x, event.y, self.grid)
        if not cell:
            return
        row, col = cell

        # Shift + Левый клик — перемещение точки старта
        if event.state & 0x0001:  # Маска клавиши Shift
            self.grid.set_start(row, col)
            self.on_reset_search()
        else:
            self.grid.toggle_wall(row, col, make_wall=True)
            self.draw()

    def on_mouse_drag_left(self, event: tk.Event) -> None:
        """Обработка рисования стен при зажатой левой кнопке мыши."""
        cell = self.renderer.screen_to_cell(event.x, event.y, self.grid)
        if cell and not (event.state & 0x0001):
            row, col = cell
            self.grid.toggle_wall(row, col, make_wall=True)
            self.draw()

    def on_mouse_down_right(self, event: tk.Event) -> None:
        """Обработка клика правой кнопкой мыши."""
        cell = self.renderer.screen_to_cell(event.x, event.y, self.grid)
        if not cell:
            return
        row, col = cell

        # Shift + Правый клик — перемещение целевой точки
        if event.state & 0x0001:  # Маска клавиши Shift
            self.grid.set_goal(row, col)
            self.on_reset_search()
        else:
            self.grid.toggle_wall(row, col, make_wall=False)
            self.draw()

    def on_mouse_drag_right(self, event: tk.Event) -> None:
        """Обработка стирания стен при зажатой правой кнопке мыши."""
        cell = self.renderer.screen_to_cell(event.x, event.y, self.grid)
        if cell and not (event.state & 0x0001):
            row, col = cell
            self.grid.toggle_wall(row, col, make_wall=False)
            self.draw()

    def on_export_map(self) -> None:
        """Экспорт текущей карты в файл."""
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
        """Импорт карты из текстового файла."""
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
        """Запуск главного цикла приложения Tkinter."""
        self.root.mainloop()
