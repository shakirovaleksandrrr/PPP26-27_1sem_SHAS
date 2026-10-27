"""Main application controller integrating model, renderer, and controls."""

import tkinter as tk
from src.models.starfield_model import StarfieldModel
from src.renderers.star_renderer import StarRenderer
from src.widgets.controls import ControlsFrame


class StarfieldApp:
    """Coordinates simulation model, canvas rendering, and user input events."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize main application window, subsystems, and event bindings.

        Args:
            root: Root Tkinter window instance.
        """
        self.root = root
        self.root.title("3D Звездное поле — Лабораторная работа 3.1 (Шакиров А. С.)")
        self.root.geometry("1000x720")
        self.root.minsize(800, 600)
        self.root.configure(bg="#05050d")

        self.width = 1000
        self.height = 640

        # 1. Main Canvas for 3D animation
        self.canvas = tk.Canvas(
            self.root,
            bg="#030308",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 2. Instantiate Model and Renderer
        self.model = StarfieldModel(
            num_stars=500,
            max_z=1000.0,
            fov_distance=400.0,
            initial_speed=12.0
        )
        self.renderer = StarRenderer(self.canvas)

        # 3. Instantiate Bottom Controls Panel
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

        # 4. Bind window, mouse, and keyboard events
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

        # Start 60 FPS animation loop
        self._is_running = True
        self.root.after(16, self._tick)

    def on_resize(self, event: tk.Event) -> None:
        """Handle canvas resize and update viewport dimension.

        Args:
            event: Configure event with new canvas size.
        """
        self.width = max(100, event.width)
        self.height = max(100, event.height)

    def on_mouse_move(self, event: tk.Event) -> None:
        """Handle mouse movement to steer flight trajectory and vanishing point.

        Args:
            event: Mouse motion event containing pointer coordinates.
        """
        self.model.update_steering(event.x, event.y, self.width, self.height)

    def on_speed_change(self, new_speed: float) -> None:
        """Update flight speed from slider."""
        self.model.set_speed(new_speed)

    def on_count_change(self, new_count: int) -> None:
        """Update number of stars from slider."""
        self.model.set_num_stars(new_count)

    def on_warp_toggle(self, enabled: bool) -> None:
        """Toggle warp trail rendering."""
        self.model.warp_trails = enabled

    def on_pause_toggle(self) -> bool:
        """Toggle simulation pause state."""
        is_paused = self.model.toggle_pause()
        self.controls.update_pause_button_text(is_paused)
        return is_paused

    def on_reset(self) -> None:
        """Reset starfield and camera parameters."""
        self.model.reset()

    def on_key_space(self, event: tk.Event) -> None:
        """Handle Space key press to toggle pause."""
        self.on_pause_toggle()

    def on_key_reset(self, event: tk.Event) -> None:
        """Handle R key press to reset simulation."""
        self.on_reset()

    def on_key_speed_up(self, event: tk.Event) -> None:
        """Increase speed via keyboard shortcut."""
        new_speed = min(50.0, self.model.speed + 2.0)
        self.model.set_speed(new_speed)
        self.controls.sync_speed(new_speed)

    def on_key_speed_down(self, event: tk.Event) -> None:
        """Decrease speed via keyboard shortcut."""
        new_speed = max(0.0, self.model.speed - 2.0)
        self.model.set_speed(new_speed)
        self.controls.sync_speed(new_speed)

    def _tick(self) -> None:
        """Perform single frame animation tick at ~60 FPS."""
        if not self._is_running:
            return

        # 1. Update mathematical state
        self.model.update(self.width, self.height)

        # 2. Extract projection data and render
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

        # Schedule next frame in 16ms (~60 FPS)
        self.root.after(16, self._tick)

    def run(self) -> None:
        """Start the application mainloop."""
        try:
            self.root.mainloop()
        finally:
            self._is_running = False
