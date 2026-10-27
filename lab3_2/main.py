"""Entry point for A* and pathfinding visualization application."""

import sys
from pathlib import Path
import tkinter as tk

# Ensure lab3_2 directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.app import PathfindingApp


def main() -> None:
    """Instantiate and run the Pathfinding application."""
    root = tk.Tk()
    app = PathfindingApp(root)
    app.run()


if __name__ == "__main__":
    main()
