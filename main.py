"""Entry point for 3D Starfield animation application."""

import tkinter as tk
from src.app import StarfieldApp


def main() -> None:
    """Instantiate and run the Starfield application."""
    root = tk.Tk()
    app = StarfieldApp(root)
    app.run()


if __name__ == "__main__":
    main()
