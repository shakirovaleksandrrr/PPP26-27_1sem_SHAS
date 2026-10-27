"""Entry point for 3D Starfield animation application."""

import sys
from pathlib import Path
import tkinter as tk

# Ensure lab directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.app import StarfieldApp


def main() -> None:
    """Instantiate and run the Starfield application."""
    root = tk.Tk()
    app = StarfieldApp(root)
    app.run()


if __name__ == "__main__":
    main()
