"""Интерактивная панель управления со слайдерами, переключателями и кнопками."""

import tkinter as tk
from typing import Callable


class ControlsFrame(tk.Frame):
    """Нижняя панель управления с интерактивными элементами для настройки параметров симуляции."""

    def __init__(
        self,
        master: tk.Widget,
        on_speed_change: Callable[[float], None],
        on_count_change: Callable[[int], None],
        on_warp_toggle: Callable[[bool], None],
        on_pause_toggle: Callable[[], bool],
        on_reset: Callable[[], None],
        initial_speed: float = 12.0,
        initial_count: int = 500,
        initial_warp: bool = True
    ) -> None:
        """Инициализация элементов панели управления.

        Аргументы:
            master: Родительский виджет.
            on_speed_change: Обратный вызов при перемещении слайдера скорости.
            on_count_change: Обратный вызов при перемещении слайдера числа звезд.
            on_warp_toggle: Обратный вызов при изменении флага шлейфов warp speed.
            on_pause_toggle: Обратный вызов при нажатии кнопки паузы.
            on_reset: Обратный вызов при нажатии кнопки сброса.
            initial_speed: Начальное значение скорости на слайдере.
            initial_count: Начальное число звезд на слайдере.
            initial_warp: Начальное состояние переключателя шлейфов.
        """
        super().__init__(master, bg="#12121f", padx=15, pady=8)

        self.on_speed_change = on_speed_change
        self.on_count_change = on_count_change
        self.on_warp_toggle = on_warp_toggle
        self.on_pause_toggle = on_pause_toggle
        self.on_reset = on_reset

        # Шрифт и цвета меток
        lbl_font = ("Segoe UI", 9, "bold")
        lbl_fg = "#eceff1"

        # 1. Слайдер скорости
        speed_frame = tk.Frame(self, bg="#12121f")
        speed_frame.pack(side=tk.LEFT, padx=15)
        tk.Label(
            speed_frame,
            text="Скорость (ly/s):",
            font=lbl_font,
            fg=lbl_fg,
            bg="#12121f"
        ).pack(anchor="w")

        self.speed_slider = tk.Scale(
            speed_frame,
            from_=0.0,
            to=50.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            length=160,
            bg="#1e1e2f",
            fg="#80d8ff",
            troughcolor="#0a0a14",
            highlightthickness=0,
            command=self._handle_speed_slider
        )
        self.speed_slider.set(initial_speed)
        self.speed_slider.pack()

        # 2. Слайдер количества звезд
        count_frame = tk.Frame(self, bg="#12121f")
        count_frame.pack(side=tk.LEFT, padx=15)
        tk.Label(
            count_frame,
            text="Число звезд:",
            font=lbl_font,
            fg=lbl_fg,
            bg="#12121f"
        ).pack(anchor="w")

        self.count_slider = tk.Scale(
            count_frame,
            from_=50,
            to=1500,
            resolution=50,
            orient=tk.HORIZONTAL,
            length=160,
            bg="#1e1e2f",
            fg="#ffd54f",
            troughcolor="#0a0a14",
            highlightthickness=0,
            command=self._handle_count_slider
        )
        self.count_slider.set(initial_count)
        self.count_slider.pack()

        # 3. Чекбокс шлейфов гиперпрыжка (Warp Trails)
        self.warp_var = tk.BooleanVar(value=initial_warp)
        self.warp_check = tk.Checkbutton(
            self,
            text="Шлейфы (Warp)",
            variable=self.warp_var,
            command=self._handle_warp_toggle,
            font=lbl_font,
            fg="#81c784",
            bg="#12121f",
            selectcolor="#0a0a14",
            activebackground="#12121f",
            activeforeground="#a5d6a7"
        )
        self.warp_check.pack(side=tk.LEFT, padx=15)

        # 4. Кнопки управления (Пауза и Сброс)
        btn_frame = tk.Frame(self, bg="#12121f")
        btn_frame.pack(side=tk.RIGHT, padx=10)

        self.btn_pause = tk.Button(
            btn_frame,
            text="Пауза (Space)",
            command=self._handle_pause_button,
            font=lbl_font,
            bg="#37474f",
            fg="#ffffff",
            activebackground="#455a64",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2"
        )
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_reset = tk.Button(
            btn_frame,
            text="Сброс (R)",
            command=self.on_reset,
            font=lbl_font,
            bg="#c62828",
            fg="#ffffff",
            activebackground="#d32f2f",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2"
        )
        self.btn_reset.pack(side=tk.LEFT, padx=5)

    def _handle_speed_slider(self, val: str) -> None:
        """Обработка движения слайдера скорости."""
        self.on_speed_change(float(val))

    def _handle_count_slider(self, val: str) -> None:
        """Обработка движения слайдера количества звезд."""
        self.on_count_change(int(float(val)))

    def _handle_warp_toggle(self) -> None:
        """Обработка переключения чекбокса световых шлейфов."""
        self.on_warp_toggle(self.warp_var.get())

    def _handle_pause_button(self) -> None:
        """Обработка нажатия кнопки паузы и обновление ее текста."""
        is_paused = self.on_pause_toggle()
        self.update_pause_button_text(is_paused)

    def update_pause_button_text(self, is_paused: bool) -> None:
        """Обновление надписи и цвета кнопки паузы в зависимости от состояния."""
        if is_paused:
            self.btn_pause.config(text="Старт (Space)", bg="#2e7d32")
        else:
            self.btn_pause.config(text="Пауза (Space)", bg="#37474f")

    def sync_speed(self, speed: float) -> None:
        """Программная синхронизация положения слайдера при изменении скорости с клавиатуры."""
        self.speed_slider.set(speed)
