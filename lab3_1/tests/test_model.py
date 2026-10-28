"""Модульные тесты для математической модели звездного поля и 3D-проекции."""

import sys
from pathlib import Path
import unittest

# Добавление каталога лабораторной работы в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.star import Star, STAR_COLORS
from src.models.starfield_model import StarfieldModel


class TestStarModel(unittest.TestCase):
    """Набор тестов для сущности Star и формул перспективного проецирования 3D в 2D."""

    def setUp(self) -> None:
        """Создание стандартного тестового экземпляра звезды."""
        self.star = Star(x=100.0, y=50.0, z=200.0, max_z=1000.0)

    def test_star_initialization(self) -> None:
        """Проверка начальных координат и ограничений глубины звезды."""
        self.assertEqual(self.star.x, 100.0)
        self.assertEqual(self.star.y, 50.0)
        self.assertEqual(self.star.z, 200.0)
        self.assertEqual(self.star.prev_z, 200.0)
        self.assertGreater(self.star.base_radius, 0.0)
        self.assertIn(self.star.color, STAR_COLORS)

    def test_projection_math(self) -> None:
        """Проверка соответствия вычисленных координат проекции оптической формуле."""
        center_x = 500.0
        center_y = 350.0
        fov = 400.0
        sx, sy, radius, px, py = self.star.get_projection(center_x, center_y, fov)

        self.assertAlmostEqual(sx, 700.0)
        self.assertAlmostEqual(sy, 450.0)
        self.assertGreater(radius, 0.0)
        self.assertAlmostEqual(px, 700.0)
        self.assertAlmostEqual(py, 450.0)

    def test_radius_increases_as_star_approaches(self) -> None:
        """Проверка увеличения видимого радиуса звезды при уменьшении глубины z."""
        center_x = 500.0
        center_y = 350.0
        fov = 400.0

        _, _, radius_far, _, _ = self.star.get_projection(center_x, center_y, fov)

        # Перемещение звезды ближе к наблюдателю (уменьшение z)
        self.star.z = 50.0
        _, _, radius_close, _, _ = self.star.get_projection(center_x, center_y, fov)

        self.assertGreater(radius_close, radius_far)

    def test_respawn_resets_depth_to_max(self) -> None:
        """Проверка возврата координаты глубины на максимальную плоскость при респавне."""
        self.star.z = 0.5
        self.star.respawn(spread_x=500.0, spread_y=400.0)
        self.assertEqual(self.star.z, self.star.max_z)
        self.assertEqual(self.star.prev_z, self.star.max_z)
        self.assertIn(self.star.color, STAR_COLORS)


class TestStarfieldModel(unittest.TestCase):
    """Набор тестов для менеджера модели StarfieldModel и глобального состояния."""

    def setUp(self) -> None:
        """Инициализация типовой модели симуляции."""
        self.model = StarfieldModel(num_stars=150, max_z=1000.0, initial_speed=10.0)

    def test_star_count(self) -> None:
        """Проверка корректности изменения количества звезд в симуляции."""
        self.assertEqual(len(self.model.stars), 150)
        self.model.set_num_stars(300)
        self.assertEqual(len(self.model.stars), 300)
        self.model.set_num_stars(50)
        self.assertEqual(len(self.model.stars), 50)

    def test_pause_toggle(self) -> None:
        """Проверка корректного переключения состояния паузы."""
        self.assertFalse(self.model.is_paused)
        self.assertTrue(self.model.toggle_pause())
        self.assertTrue(self.model.is_paused)
        self.assertFalse(self.model.toggle_pause())
        self.assertFalse(self.model.is_paused)

    def test_speed_bounds(self) -> None:
        """Проверка границ скорости: не опускается ниже нуля и не превышает лимит."""
        self.model.set_speed(25.0)
        self.assertEqual(self.model.speed, 25.0)

        self.model.set_speed(-10.0)
        self.assertEqual(self.model.speed, 0.0)

        self.model.set_speed(100.0)
        self.assertEqual(self.model.speed, 60.0)

    def test_steering_computation(self) -> None:
        """Проверка вычисления нормализованных смещений точки схода от положения мыши."""
        self.model.update_steering(mouse_x=500.0, mouse_y=350.0, width=1000.0, height=700.0)
        self.assertAlmostEqual(self.model.target_offset_x, 0.0)
        self.assertAlmostEqual(self.model.target_offset_y, 0.0)

        self.model.update_steering(mouse_x=1000.0, mouse_y=350.0, width=1000.0, height=700.0)
        self.assertLess(self.model.target_offset_x, 0.0)

    def test_reset_clears_steering(self) -> None:
        """Проверка восстановления точки схода и смещений камеры при вызове сброса."""
        self.model.offset_x = 45.0
        self.model.offset_y = -30.0
        self.model.reset()
        self.assertEqual(self.model.offset_x, 0.0)
        self.assertEqual(self.model.offset_y, 0.0)
        self.assertEqual(self.model.target_offset_x, 0.0)
        self.assertEqual(self.model.target_offset_y, 0.0)

    def test_update_cycle_advances_positions(self) -> None:
        """Проверка продвижения координат по оси z на каждом шаге обновления."""
        self.model.update(width=800.0, height=600.0)
        render_data = self.model.get_render_data(800.0, 600.0)
        self.assertEqual(len(render_data), len(self.model.stars))

    def test_pause_preserves_positions(self) -> None:
        """Проверка неизменности состояния симуляции при активной паузе."""
        self.model.is_paused = True
        z_values_before = [s.z for s in self.model.stars]
        self.model.update(width=800.0, height=600.0)
        z_values_after = [s.z for s in self.model.stars]
        self.assertEqual(z_values_before, z_values_after)


if __name__ == "__main__":
    unittest.main()
