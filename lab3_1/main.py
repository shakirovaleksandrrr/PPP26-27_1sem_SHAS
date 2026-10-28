"""Точка входа в приложение 3D-анимации звездного поля."""

import sys
from pathlib import Path
import tkinter as tk

# Добавление каталога лабораторной работы в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.app import StarfieldApp


def main() -> None:
    """Инициализация и запуск приложения «Звездное поле»."""
    root = tk.Tk()
    app = StarfieldApp(root)
    app.run()


if __name__ == "__main__":
    main()
