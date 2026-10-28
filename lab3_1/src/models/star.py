"""Модель звезды, представляющая отдельное небесное тело в 3D-пространстве."""

import random
from typing import Tuple

# Естественные спектральные цвета звезд
STAR_COLORS = [
    "#ffffff",  # Белый (Спектральный класс A)
    "#e0f7fa",  # Светло-голубой (Спектральный класс B)
    "#80d8ff",  # Синий (Спектральный класс O)
    "#fff9c4",  # Желтовато-белый (Спектральный класс F/G)
    "#ffe0b2",  # Светло-оранжевый (Спектральный класс K)
]


class Star:
    """Представляет 3D-звезду с пространственными координатами, цветом и историей глубины."""

    def __init__(self, x: float, y: float, z: float, max_z: float) -> None:
        """Инициализация координат звезды и визуальных свойств.

        Аргументы:
            x: Начальная координата X относительно центра проекции.
            y: Начальная координата Y относительно центра проекции.
            z: Координата глубины вдоль оси камеры (z > 0).
            max_z: Максимальная плоскость глубины для перерождения звезды.
        """
        self.x = x
        self.y = y
        self.z = max(1.0, z)
        self.prev_z = self.z
        self.max_z = max_z
        self.base_radius = random.uniform(1.2, 2.8)
        self.color = random.choice(STAR_COLORS)

    def respawn(self, spread_x: float, spread_y: float) -> None:
        """Перерождение звезды на дальней плоскости при выходе за пределы обзора.

        Аргументы:
            spread_x: Полуширина распределения координат.
            spread_y: Полувысота распределения координат.
        """
        self.x = random.uniform(-spread_x, spread_x)
        self.y = random.uniform(-spread_y, spread_y)
        self.z = self.max_z
        self.prev_z = self.z
        self.base_radius = random.uniform(1.2, 2.8)
        self.color = random.choice(STAR_COLORS)

    def update(self, speed: float, spread_x: float, spread_y: float) -> None:
        """Обновление глубины звезды по скорости полета и респавн при пролете за камеру.

        Аргументы:
            speed: Скорость движения вдоль оси Z по направлению к наблюдателю.
            spread_x: Полуширина области для респавна.
            spread_y: Полувысота области для респавна.
        """
        self.prev_z = self.z
        self.z -= speed

        if self.z <= 1.0:
            self.respawn(spread_x, spread_y)

    def get_projection(
        self,
        center_x: float,
        center_y: float,
        fov_distance: float
    ) -> Tuple[float, float, float, float, float]:
        """Вычисление 2D-перспективной проекции для текущей и предыдущей позиций.

        Аргументы:
            center_x: Горизонтальный центр экрана (точка схода).
            center_y: Вертикальный центр экрана (точка схода).
            fov_distance: Фокусное расстояние камеры / множитель поля зрения.

        Возвращает:
            Кортеж (curr_screen_x, curr_screen_y, radius, prev_screen_x, prev_screen_y).
        """
        # Формула перспективной проекции: screen_x = (x / z) * fov + center_x
        scale = fov_distance / self.z
        screen_x = self.x * scale + center_x
        screen_y = self.y * scale + center_y

        # Видимый радиус возрастает обратно пропорционально расстоянию z
        radius = max(0.5, self.base_radius * (fov_distance / (self.z * 1.5)))

        # Предыдущая позиция для отрисовки шлейфов гиперпрыжка
        prev_scale = fov_distance / max(1.0, self.prev_z)
        prev_screen_x = self.x * prev_scale + center_x
        prev_screen_y = self.y * prev_scale + center_y

        return screen_x, screen_y, radius, prev_screen_x, prev_screen_y
