"""Main application module for Starfield 3D animation."""

import tkinter as tk


class StarfieldApp:
    """Main application controller managing window, canvas, and animation loop."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize main application window, canvas and bindings.

        Args:
            root: Root Tkinter window instance.
        """
        self.root = root
        self.root.title("3D Звездное поле — Лабораторная работа 3.1 (Шакиров А. С.)")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Configure dark background theme
        self.root.configure(bg="#05050d")

        # Main canvas for graphics rendering
        self.canvas = tk.Canvas(
            self.root,
            bg="#030308",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.width = 1000
        self.height = 700

        # Bind window resize event
        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event: tk.Event) -> None:
        """Handle canvas resize event and update viewport dimensions.

        Args:
            event: Tkinter configure event containing new width and height.
        """
        self.width = max(100, event.width)
        self.height = max(100, event.height)

    def run(self) -> None:
        """Start the Tkinter main event loop."""
        self.root.mainloop()
