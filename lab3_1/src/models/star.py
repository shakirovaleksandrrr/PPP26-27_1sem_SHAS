"""Star model representing a single celestial body in 3D space."""

import random
from typing import Tuple

# Natural stellar spectral colors
STAR_COLORS = [
    "#ffffff",  # White (Class A)
    "#e0f7fa",  # Light Cyan (Class B)
    "#80d8ff",  # Blue (Class O)
    "#fff9c4",  # Yellow-White (Class F/G)
    "#ffe0b2",  # Light Orange (Class K)
]


class Star:
    """Represents a 3D star with spatial coordinates, color, and depth history."""

    def __init__(self, x: float, y: float, z: float, max_z: float) -> None:
        """Initialize star coordinates and visual properties.

        Args:
            x: Initial X coordinate relative to projection center.
            y: Initial Y coordinate relative to projection center.
            z: Depth coordinate along camera axis (z > 0).
            max_z: Maximum depth plane for respawning.
        """
        self.x = x
        self.y = y
        self.z = max(1.0, z)
        self.prev_z = self.z
        self.max_z = max_z
        self.base_radius = random.uniform(1.2, 2.8)
        self.color = random.choice(STAR_COLORS)

    def respawn(self, spread_x: float, spread_y: float) -> None:
        """Respawn the star on the farthest plane when it leaves the field of view.

        Args:
            spread_x: Half-width of coordinate distribution.
            spread_y: Half-height of coordinate distribution.
        """
        self.x = random.uniform(-spread_x, spread_x)
        self.y = random.uniform(-spread_y, spread_y)
        self.z = self.max_z
        self.prev_z = self.z
        self.base_radius = random.uniform(1.2, 2.8)
        self.color = random.choice(STAR_COLORS)

    def update(self, speed: float, spread_x: float, spread_y: float) -> None:
        """Update star depth according to flight speed, respawning if behind camera.

        Args:
            speed: Velocity along the Z axis toward the viewer.
            spread_x: Half-width of field for respawning.
            spread_y: Half-height of field for respawning.
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
        """Compute 2D perspective projection for current and previous positions.

        Args:
            center_x: Horizontal screen center (vanishing point).
            center_y: Vertical screen center (vanishing point).
            fov_distance: Camera focal length / field of view multiplier.

        Returns:
            Tuple of (curr_screen_x, curr_screen_y, radius, prev_screen_x, prev_screen_y).
        """
        # Perspective projection formula: screen_x = (x / z) * fov + center_x
        scale = fov_distance / self.z
        screen_x = self.x * scale + center_x
        screen_y = self.y * scale + center_y

        # Apparent radius increases inversely with distance z
        radius = max(0.5, self.base_radius * (fov_distance / (self.z * 1.5)))

        # Previous position for drawing warp trails
        prev_scale = fov_distance / max(1.0, self.prev_z)
        prev_screen_x = self.x * prev_scale + center_x
        prev_screen_y = self.y * prev_scale + center_y

        return screen_x, screen_y, radius, prev_screen_x, prev_screen_y
