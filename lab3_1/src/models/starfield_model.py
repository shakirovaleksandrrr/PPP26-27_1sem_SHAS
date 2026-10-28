"""Математическая модель звездного поля, управляющая координатами, физикой и проекцией."""

import random
from typing import List, Tuple
from src.models.star import Star


class StarfieldModel:
    """Математическая и физическая модель для 3D-симуляции звездного поля."""

    def __init__(
        self,
        num_stars: int = 500,
        max_z: float = 1000.0,
        fov_distance: float = 400.0,
        initial_speed: float = 12.0
    ) -> None:
        """Инициализация параметров симуляции и создание коллекции звезд.

        Аргументы:
            num_stars: Начальное количество активных звезд.
            max_z: Максимальная плоскость глубины в пространстве координат.
            fov_distance: Фокусное расстояние камеры для перспективной проекции.
            initial_speed: Начальная скорость полета вдоль оси Z.
        """
        self.max_z = max_z
        self.fov_distance = fov_distance
        self.speed = initial_speed
        self.is_paused = False
        self.warp_trails = True

        # Смещение точки схода (управляется курсором мыши)
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.target_offset_x = 0.0
        self.target_offset_y = 0.0

        # Коллекция звезд
        self.stars: List[Star] = []
        self.set_num_stars(num_stars)

    def set_num_stars(self, count: int) -> None:
        """Установка активного числа звезд (генерация новых или усечение списка).

        Аргументы:
            count: Требуемое общее количество звезд.
        """
        count = max(10, count)
        current = len(self.stars)
        if count > current:
            # Добавление новых звезд, равномерно распределенных по всему объему
            for _ in range(count - current):
                x = random.uniform(-1000.0, 1000.0)
                y = random.uniform(-800.0, 800.0)
                z = random.uniform(10.0, self.max_z)
                self.stars.append(Star(x, y, z, self.max_z))
        elif count < current:
            self.stars = self.stars[:count]

    def reset(self) -> None:
        """Сброс всех звезд на случайные позиции и обнуление смещения камеры."""
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.target_offset_x = 0.0
        self.target_offset_y = 0.0
        for star in self.stars:
            star.x = random.uniform(-1000.0, 1000.0)
            star.y = random.uniform(-800.0, 800.0)
            star.z = random.uniform(10.0, self.max_z)
            star.prev_z = star.z

    def toggle_pause(self) -> bool:
        """Переключение состояния паузы симуляции.

        Возвращает:
            Текущее состояние паузы после переключения.
        """
        self.is_paused = not self.is_paused
        return self.is_paused

    def set_speed(self, new_speed: float) -> None:
        """Установка скорости полета.

        Аргументы:
            new_speed: Новое значение скорости (ограничено диапазоном от 0 до 60).
        """
        self.speed = max(0.0, min(60.0, new_speed))

    def update_steering(self, mouse_x: float, mouse_y: float, width: float, height: float) -> None:
        """Обновление целевого смещения точки схода на основе положения мыши.

        Аргументы:
            mouse_x: Текущая координата мыши X.
            mouse_y: Текущая координата мыши Y.
            width: Ширина области просмотра.
            height: Высота области просмотра.
        """
        # Расчет нормализованного смещения от центра экрана для плавного маневрирования
        norm_x = (mouse_x - width / 2.0) / (width / 2.0)
        norm_y = (mouse_y - height / 2.0) / (height / 2.0)
        self.target_offset_x = -norm_x * 120.0
        self.target_offset_y = -norm_y * 90.0

    def update(self, width: float, height: float) -> None:
        """Продвижение состояния симуляции на один анимационный кадр.

        Аргументы:
            width: Текущая ширина области просмотра.
            height: Текущая высота области просмотра.
        """
        if self.is_paused:
            return

        # Плавная интерполяция (lerp) к целевому смещению камеры
        self.offset_x += (self.target_offset_x - self.offset_x) * 0.1
        self.offset_y += (self.target_offset_y - self.offset_y) * 0.1

        spread_x = max(600.0, width)
        spread_y = max(500.0, height)

        center_x = width / 2.0 + self.offset_x
        center_y = height / 2.0 + self.offset_y

        for star in self.stars:
            star.update(self.speed, spread_x, spread_y)

            # Проверка выхода спроецированной звезды далеко за границы экрана и респавн
            sx, sy, _, _, _ = star.get_projection(center_x, center_y, self.fov_distance)
            margin = 150.0
            if (sx < -margin or sx > width + margin or
                    sy < -margin or sy > height + margin):
                star.respawn(spread_x, spread_y)

    def get_render_data(
        self,
        width: float,
        height: float
    ) -> List[Tuple[float, float, float, float, float, str]]:
        """Вычисление спроецированных геометрических данных для отрисовки всех звезд.

        Аргументы:
            width: Текущая ширина экрана.
            height: Текущая высота экрана.

        Возвращает:
            Список кортежей (curr_x, curr_y, radius, prev_x, prev_y, color).
        """
        center_x = width / 2.0 + self.offset_x
        center_y = height / 2.0 + self.offset_y

        render_list = []
        for star in self.stars:
            sx, sy, radius, px, py = star.get_projection(
                center_x, center_y, self.fov_distance
            )
            render_list.append((sx, sy, radius, px, py, star.color))

        return render_list
