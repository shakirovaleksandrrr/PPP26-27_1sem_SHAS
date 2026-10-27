"""Starfield mathematical model managing star coordinates, motion, and projection."""

import random
from typing import List, Tuple
from src.models.star import Star


class StarfieldModel:
    """Mathematical and physical model for 3D starfield simulation."""

    def __init__(
        self,
        num_stars: int = 500,
        max_z: float = 1000.0,
        fov_distance: float = 400.0,
        initial_speed: float = 12.0
    ) -> None:
        """Initialize simulation parameters and populate star collection.

        Args:
            num_stars: Initial number of active stars.
            max_z: Maximum depth plane in coordinate space.
            fov_distance: Camera focal length for perspective projection.
            initial_speed: Initial flight speed along Z axis.
        """
        self.max_z = max_z
        self.fov_distance = fov_distance
        self.speed = initial_speed
        self.is_paused = False
        self.warp_trails = True

        # Vanishing point offset (controlled by mouse)
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.target_offset_x = 0.0
        self.target_offset_y = 0.0

        # Star collection
        self.stars: List[Star] = []
        self.set_num_stars(num_stars)

    def set_num_stars(self, count: int) -> None:
        """Set the active number of stars, generating or truncating as needed.

        Args:
            count: Desired total number of stars.
        """
        count = max(10, count)
        current = len(self.stars)
        if count > current:
            # Add new stars distributed randomly across full volume
            for _ in range(count - current):
                x = random.uniform(-1000.0, 1000.0)
                y = random.uniform(-800.0, 800.0)
                z = random.uniform(10.0, self.max_z)
                self.stars.append(Star(x, y, z, self.max_z))
        elif count < current:
            self.stars = self.stars[:count]

    def reset(self) -> None:
        """Reset all stars to random spatial positions and clear steering offsets."""
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
        """Toggle simulation pause state.

        Returns:
            Current pause state after toggle.
        """
        self.is_paused = not self.is_paused
        return self.is_paused

    def set_speed(self, new_speed: float) -> None:
        """Set flight velocity.

        Args:
            new_speed: New speed value (clamped between 0 and 60).
        """
        self.speed = max(0.0, min(60.0, new_speed))

    def update_steering(self, mouse_x: float, mouse_y: float, width: float, height: float) -> None:
        """Update target vanishing point offset based on mouse position.

        Args:
            mouse_x: Current mouse X coordinate.
            mouse_y: Current mouse Y coordinate.
            width: Viewport width.
            height: Viewport height.
        """
        # Calculate offset from screen center, scaled to gentle steering
        norm_x = (mouse_x - width / 2.0) / (width / 2.0)
        norm_y = (mouse_y - height / 2.0) / (height / 2.0)
        self.target_offset_x = -norm_x * 120.0
        self.target_offset_y = -norm_y * 90.0

    def update(self, width: float, height: float) -> None:
        """Advance simulation state by one frame.

        Args:
            width: Current viewport width.
            height: Current viewport height.
        """
        if self.is_paused:
            return

        # Smooth interpolation (lerp) toward target steering offset
        self.offset_x += (self.target_offset_x - self.offset_x) * 0.1
        self.offset_y += (self.target_offset_y - self.offset_y) * 0.1

        spread_x = max(600.0, width)
        spread_y = max(500.0, height)

        center_x = width / 2.0 + self.offset_x
        center_y = height / 2.0 + self.offset_y

        for star in self.stars:
            star.update(self.speed, spread_x, spread_y)

            # Check if projected star is way outside visible viewport and respawn
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
        """Compute projected rendering data for all active stars.

        Args:
            width: Current viewport width.
            height: Current viewport height.

        Returns:
            List of tuples (curr_x, curr_y, radius, prev_x, prev_y, color).
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
