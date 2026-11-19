import math


G0 = 9.8


def calculate_thrust(state):

    if state.fuel_mass <= 0.0:
        state.thrust = 0.0

    state.thrust_force_x = (
        state.thrust * math.sin(state.angle)
    )

    state.thrust_force_y = (
        state.thrust * math.cos(state.angle)
    )

    return state


def update_fuel(state, rocket, dt):

    if state.fuel_mass <= 0.0:
        state.fuel_mass = 0.0
        state.thrust = 0.0
        state.mass = rocket.dry_mass
        return state

    mass_flow_rate = (
        state.thrust
        / (rocket.specific_impulse * G0)
    )

    fuel_used = mass_flow_rate * dt

    state.fuel_mass = (
        state.fuel_mass
        - fuel_used
    )

    if state.fuel_mass < 0.0:
        state.fuel_mass = 0.0

    state.mass = (
        rocket.dry_mass
        + state.fuel_mass
    )

    return state