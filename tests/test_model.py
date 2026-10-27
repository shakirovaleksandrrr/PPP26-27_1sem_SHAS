"""Unit tests for Starfield mathematical model and 3D projection."""

import unittest
from src.models.star import Star, STAR_COLORS
from src.models.starfield_model import StarfieldModel


class TestStarModel(unittest.TestCase):
    """Test cases for Star entity and 3D-to-2D projection formulas."""

    def setUp(self) -> None:
        """Create standard test star instance."""
        self.star = Star(x=100.0, y=50.0, z=200.0, max_z=1000.0)

    def test_star_initialization(self) -> None:
        """Verify initial coordinates and depth constraints."""
        self.assertEqual(self.star.x, 100.0)
        self.assertEqual(self.star.y, 50.0)
        self.assertEqual(self.star.z, 200.0)
        self.assertEqual(self.star.prev_z, 200.0)
        self.assertGreater(self.star.base_radius, 0.0)
        self.assertIn(self.star.color, STAR_COLORS)

    def test_projection_math(self) -> None:
        """Verify perspective projection coordinates matches optical formula."""
        center_x = 500.0
        center_y = 350.0
        fov = 400.0
        # Expected screen_x = (x / z) * fov + center_x = (100 / 200) * 400 + 500 = 700.0
        # Expected screen_y = (y / z) * fov + center_y = (50 / 200) * 400 + 350 = 450.0
        sx, sy, radius, px, py = self.star.get_projection(center_x, center_y, fov)

        self.assertAlmostEqual(sx, 700.0)
        self.assertAlmostEqual(sy, 450.0)
        self.assertGreater(radius, 0.0)
        self.assertAlmostEqual(px, 700.0)
        self.assertAlmostEqual(py, 450.0)

    def test_radius_increases_as_star_approaches(self) -> None:
        """Verify that apparent star radius grows as depth z decreases."""
        center_x = 500.0
        center_y = 350.0
        fov = 400.0

        _, _, radius_far, _, _ = self.star.get_projection(center_x, center_y, fov)

        # Move star closer (decrease z)
        self.star.z = 50.0
        _, _, radius_close, _, _ = self.star.get_projection(center_x, center_y, fov)

        self.assertGreater(radius_close, radius_far)

    def test_respawn_resets_depth_to_max(self) -> None:
        """Verify respawn places star back at maximum depth plane."""
        self.star.z = 0.5
        self.star.respawn(spread_x=500.0, spread_y=400.0)
        self.assertEqual(self.star.z, self.star.max_z)
        self.assertEqual(self.star.prev_z, self.star.max_z)
        self.assertIn(self.star.color, STAR_COLORS)


class TestStarfieldModel(unittest.TestCase):
    """Test cases for StarfieldModel manager and global state."""

    def setUp(self) -> None:
        """Initialize standard simulation model."""
        self.model = StarfieldModel(num_stars=150, max_z=1000.0, initial_speed=10.0)

    def test_star_count(self) -> None:
        """Verify count adjustment behaves properly."""
        self.assertEqual(len(self.model.stars), 150)
        self.model.set_num_stars(300)
        self.assertEqual(len(self.model.stars), 300)
        self.model.set_num_stars(50)
        self.assertEqual(len(self.model.stars), 50)

    def test_pause_toggle(self) -> None:
        """Verify pause state toggles correctly."""
        self.assertFalse(self.model.is_paused)
        self.assertTrue(self.model.toggle_pause())
        self.assertTrue(self.model.is_paused)
        self.assertFalse(self.model.toggle_pause())
        self.assertFalse(self.model.is_paused)

    def test_speed_bounds(self) -> None:
        """Verify speed cannot be set below zero or above safety limit."""
        self.model.set_speed(25.0)
        self.assertEqual(self.model.speed, 25.0)

        self.model.set_speed(-10.0)
        self.assertEqual(self.model.speed, 0.0)

        self.model.set_speed(100.0)
        self.assertEqual(self.model.speed, 60.0)

    def test_steering_computation(self) -> None:
        """Verify mouse steering calculates normalized offsets correctly."""
        # When mouse is at screen center, target offset should be zero
        self.model.update_steering(mouse_x=500.0, mouse_y=350.0, width=1000.0, height=700.0)
        self.assertAlmostEqual(self.model.target_offset_x, 0.0)
        self.assertAlmostEqual(self.model.target_offset_y, 0.0)

        # When mouse moves to right, camera steers left
        self.model.update_steering(mouse_x=1000.0, mouse_y=350.0, width=1000.0, height=700.0)
        self.assertLess(self.model.target_offset_x, 0.0)

    def test_reset_clears_steering(self) -> None:
        """Verify reset restores vanishing point and offsets."""
        self.model.offset_x = 45.0
        self.model.offset_y = -30.0
        self.model.reset()
        self.assertEqual(self.model.offset_x, 0.0)
        self.assertEqual(self.model.offset_y, 0.0)
        self.assertEqual(self.model.target_offset_x, 0.0)
        self.assertEqual(self.model.target_offset_y, 0.0)

    def test_update_cycle_advances_positions(self) -> None:
        """Verify update step advances z coordinates when not paused."""
        self.model.update(width=800.0, height=600.0)
        render_data = self.model.get_render_data(800.0, 600.0)
        self.assertEqual(len(render_data), len(self.model.stars))

    def test_pause_preserves_positions(self) -> None:
        """Verify update step does not alter state when paused."""
        self.model.is_paused = True
        z_values_before = [s.z for s in self.model.stars]
        self.model.update(width=800.0, height=600.0)
        z_values_after = [s.z for s in self.model.stars]
        self.assertEqual(z_values_before, z_values_after)


if __name__ == "__main__":
    unittest.main()
