from dataclasses import dataclass


@dataclass
class Rocket:
    dry_mass: float
    initial_fuel_mass: float

    thrust: float
    specific_impulse: float

    cd: float
    area: float