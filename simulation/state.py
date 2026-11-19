from dataclasses import dataclass


@dataclass
class RocketState:
    time: float = 0.0

    x: float = 0.0
    y: float = 0.0

    vx: float = 0.0
    vy: float = 0.0

    ax: float = 0.0
    ay: float = 0.0

    mass: float = 0.0
    fuel_mass: float = 0.0

    angle: float = 0.0
    area: float = 0.0

    thrust: float = 0.0

    drag_force_x: float = 0.0
    drag_force_y: float = 0.0

    external_force_x: float = 0.0
    external_force_y: float = 0.0

    gravity_force_x: float = 0.0
    gravity_force_y: float = 0.0

    thrust_force_x: float = 0.0
    thrust_force_y: float = 0.0

    error_position: float = 0.0
    slope_error: float = 0.0

    angle_correction: float = 0.0