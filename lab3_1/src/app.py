"""Главный модуль контроллера приложения, объединяющий модель, рендерер и элементы управления."""

import tkinter as tk
from src.models.starfield_model import StarfieldModel
from src.renderers.star_renderer import StarRenderer
from src.widgets.controls import ControlsFrame


class StarfieldApp:
    """Координирует математическую модель, отрисовку на холсте и пользовательский ввод."""

    def __init__(self, root: tk.Tk) -> None:
        """Инициализация главного окна, подсистем и привязок событий.

        Аргументы:
            root: Экземпляр корневого окна Tkinter.
        """
        self.root = root
        self.root.title("3D Звездное поле — Лабораторная работа 3.1 (Шакиров А. С.)")
        self.root.geometry("1000x720")
        self.root.minsize(800, 600)
        self.root.configure(bg="#05050d")

        self.width = 1000
        self.height = 640

        # 1. Основной холст для 3D-анимации
        self.canvas = tk.Canvas(
            self.root,
            bg="#030308",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 2. Создание экземпляров модели и рендерера
        self.model = StarfieldModel(
            num_stars=500,
            max_z=1000.0,
            fov_distance=400.0,
            initial_speed=12.0
        )
        self.renderer = StarRenderer(self.canvas)

        # 3. Создание нижней панели управления
        self.controls = ControlsFrame(
            master=self.root,
            on_speed_change=self.on_speed_change,
            on_count_change=self.on_count_change,
            on_warp_toggle=self.on_warp_toggle,
            on_pause_toggle=self.on_pause_toggle,
            on_reset=self.on_reset,
            initial_speed=self.model.speed,
            initial_count=len(self.model.stars),
            initial_warp=self.model.warp_trails
        )
        self.controls.pack(fill=tk.X, side=tk.BOTTOM)

        # 4. Привязка событий окна, мыши и клавиатуры
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        self.root.bind("<space>", self.on_key_space)
        self.root.bind("<r>", self.on_key_reset)
        self.root.bind("<R>", self.on_key_reset)
        self.root.bind("<Up>", self.on_key_speed_up)
        self.root.bind("<w>", self.on_key_speed_up)
        self.root.bind("<W>", self.on_key_speed_up)
        self.root.bind("<Down>", self.on_key_speed_down)
        self.root.bind("<s>", self.on_key_speed_down)
        self.root.bind("<S>", self.on_key_speed_down)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Запуск анимационного цикла ~60 FPS
        self._is_running = True
        self.root.after(16, self._tick)

    def on_resize(self, event: tk.Event) -> None:
        """Обработка изменения размера холста и обновление габаритов области просмотра.

        Аргументы:
            event: Событие конфигурации с новыми размерами холста.
        """
        self.width = max(100, event.width)
        self.height = max(100, event.height)

    def on_mouse_move(self, event: tk.Event) -> None:
        """Обработка движения мыши для управления вектором полета и точкой схода.

        Аргументы:
            event: Событие движения мыши с координатами курсора.
        """
        self.model.update_steering(event.x, event.y, self.width, self.height)

    def on_speed_change(self, new_speed: float) -> None:
        """Обновление скорости полета со слайдера."""
        self.model.set_speed(new_speed)

    def on_count_change(self, new_count: int) -> None:
        """Обновление количества звезд со слайдера."""
        self.model.set_num_stars(new_count)

    def on_warp_toggle(self, enabled: bool) -> None:
        """Переключение отрисовки световых шлейфов гиперпрыжка."""
        self.model.warp_trails = enabled

    def on_pause_toggle(self) -> bool:
        """Переключение состояния паузы симуляции."""
        is_paused = self.model.toggle_pause()
        self.controls.update_pause_button_text(is_paused)
        return is_paused

    def on_reset(self) -> None:
        """Сброс координат звездного поля и параметров камеры."""
        self.model.reset()

    def on_key_space(self, event: tk.Event) -> None:
        """Обработка нажатия клавиши Пробел для паузы."""
        self.on_pause_toggle()

    def on_key_reset(self, event: tk.Event) -> None:
        """Обработка нажатия клавиши R для сброса симуляции."""
        self.on_reset()

    def on_key_speed_up(self, event: tk.Event) -> None:
        """Увеличение скорости полета по горячей клавише."""
        new_speed = min(50.0, self.model.speed + 2.0)
        self.model.set_speed(new_speed)
        self.controls.sync_speed(new_speed)

    def on_key_speed_down(self, event: tk.Event) -> None:
        """Уменьшение скорости полета по горячей клавише."""
        new_speed = max(0.0, self.model.speed - 2.0)
        self.model.set_speed(new_speed)
        self.controls.sync_speed(new_speed)

    def _tick(self) -> None:
        """Выполнение одного кадра анимации с частотой ~60 FPS."""
        if not self._is_running:
            return

        # 1. Обновление математического состояния
        self.model.update(self.width, self.height)

        # 2. Получение данных проекции и отрисовка кадра
        render_data = self.model.get_render_data(self.width, self.height)
        self.renderer.render(
            render_data=render_data,
            warp_trails=self.model.warp_trails,
            width=self.width,
            height=self.height,
            speed=self.model.speed,
            star_count=len(self.model.stars),
            is_paused=self.model.is_paused
        )

        # Планирование следующего кадра через 16 мс (~60 кадров в секунду)
        self.root.after(16, self._tick)

    def run(self) -> None:
        """Запуск главного цикла обработки событий Tkinter."""
        try:
            self.root.mainloop()
        finally:
            self._is_running = False
