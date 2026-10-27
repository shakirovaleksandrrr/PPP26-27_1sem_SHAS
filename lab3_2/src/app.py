"""Main application controller for A* Pathfinding visualization."""

import tkinter as tk


class PathfindingApp:
    """Main application controller managing window, canvas, and pathfinding loop."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize main application window, canvas, and event bindings.

        Args:
            root: Root Tkinter window instance.
        """
        self.root = root
        self.root.title("Алгоритм A* и поиск пути на сетке — Лабораторная работа 3.2 (Шакиров А. С.)")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        self.root.configure(bg="#12131c")

        self.canvas = tk.Canvas(
            self.root,
            bg="#181926",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.width = 1100
        self.height = 680

        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event: tk.Event) -> None:
        """Handle window resizing."""
        self.width = max(200, event.width)
        self.height = max(200, event.height)

    def run(self) -> None:
        """Start Tkinter event loop."""
        self.root.mainloop()
