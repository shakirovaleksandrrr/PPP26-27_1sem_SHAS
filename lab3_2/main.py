"""Точка входа в приложение визуализации алгоритма A* и поиска пути на сетке."""

import sys
from pathlib import Path
import tkinter as tk

# Добавление каталога лабораторной работы в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.app import PathfindingApp


def main() -> None:
    """Инициализация и запуск приложения поиска пути."""
    root = tk.Tk()
    app = PathfindingApp(root)
    app.run()


if __name__ == "__main__":
    main()
