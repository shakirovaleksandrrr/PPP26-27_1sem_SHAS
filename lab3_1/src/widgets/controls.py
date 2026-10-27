"""Interactive control panel widget with sliders, toggles, and buttons."""

import tkinter as tk
from typing import Callable


class ControlsFrame(tk.Frame):
    """Bottom control panel with interactive UI controls for simulation parameters."""

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
        """Initialize control panel elements.

        Args:
            master: Parent widget.
            on_speed_change: Callback invoked when speed slider moves.
            on_count_change: Callback invoked when star count slider moves.
            on_warp_toggle: Callback invoked when warp trail checkbox changes.
            on_pause_toggle: Callback invoked when pause button is pressed.
            on_reset: Callback invoked when reset button is pressed.
            initial_speed: Initial speed slider value.
            initial_count: Initial star count slider value.
            initial_warp: Initial warp trails checkbox state.
        """
        super().__init__(master, bg="#12121f", padx=15, pady=8)

        self.on_speed_change = on_speed_change
        self.on_count_change = on_count_change
        self.on_warp_toggle = on_warp_toggle
        self.on_pause_toggle = on_pause_toggle
        self.on_reset = on_reset

        # Label font and colors
        lbl_font = ("Segoe UI", 9, "bold")
        lbl_fg = "#eceff1"

        # 1. Speed Slider
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

        # 2. Star Count Slider
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

        # 3. Warp Trails Checkbox
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

        # 4. Action Buttons (Pause & Reset)
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
        """Handle speed slider movement."""
        self.on_speed_change(float(val))

    def _handle_count_slider(self, val: str) -> None:
        """Handle count slider movement."""
        self.on_count_change(int(float(val)))

    def _handle_warp_toggle(self) -> None:
        """Handle warp checkbox state change."""
        self.on_warp_toggle(self.warp_var.get())

    def _handle_pause_button(self) -> None:
        """Handle pause button click and update its text."""
        is_paused = self.on_pause_toggle()
        self.update_pause_button_text(is_paused)

    def update_pause_button_text(self, is_paused: bool) -> None:
        """Update text on pause button depending on state."""
        if is_paused:
            self.btn_pause.config(text="Старт (Space)", bg="#2e7d32")
        else:
            self.btn_pause.config(text="Пауза (Space)", bg="#37474f")

    def sync_speed(self, speed: float) -> None:
        """Programmatically synchronize slider with external speed updates."""
        self.speed_slider.set(speed)
