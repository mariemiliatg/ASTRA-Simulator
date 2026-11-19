from simulation.state import RocketState
from physics.gravity import calculate_gravity
from physics.propulsion import calculate_thrust, update_fuel
from physics.aerodynamics import calculate_drag
from physics.dynamics import calculate_acceleration
from physics.motion import update_velocity, update_position


def run_controlled_simulation(
    rocket,
    external_force_x,
    ideal_results,
    controller,
    simulation_time=5.0,
    dt=0.1,
    segment_size=10,
    initial_angle=0.0,
):
    """
    Misma fisica que run_simulation; al terminar cada segmento el controlador
    (LeastSquaresController) devuelve delta_theta, que se suma SOLO a state.angle.
    Devuelve un diccionario con el mismo formato que run_simulation, mas el
    registro de correcciones.
    """
    state = RocketState(
        mass=rocket.dry_mass + rocket.initial_fuel_mass,
        fuel_mass=rocket.initial_fuel_mass,
        area=rocket.area,
        thrust=rocket.thrust,
        angle=initial_angle,
    )

    keys = ["time", "x", "y", "vx", "vy", "mass", "angle"]
    res = {k: [] for k in keys}
    corrections = []

    for step in range(int(simulation_time / dt)):
        state.external_force_x = external_force_x
        state.external_force_y = 0.0

        if step > 0 and step % segment_size == 0:
            start = step - segment_size
            real_seg = {"x": res["x"][start:step], "y": res["y"][start:step]}
            ideal_seg = {"x": ideal_results["x"][start:step],
                         "y": ideal_results["y"][start:step]}
            delta_theta, info = controller.compute_correction(real_seg, ideal_seg, state)
            state.angle += delta_theta
            info["step"] = step
            info["time"] = state.time
            info["angle"] = state.angle
            corrections.append(info)

        state = calculate_gravity(state)
        state = calculate_thrust(state)
        state = calculate_drag(state, rocket)
        state = calculate_acceleration(state)

        res["time"].append(state.time)
        res["x"].append(state.x)
        res["y"].append(state.y)
        res["vx"].append(state.vx)
        res["vy"].append(state.vy)
        res["mass"].append(state.mass)
        res["angle"].append(state.angle)

        state = update_velocity(state, dt)
        state = update_position(state, dt)
        state = update_fuel(state, rocket, dt)
        state.time += dt

    res["state"] = state
    res["corrections"] = corrections
    return res
