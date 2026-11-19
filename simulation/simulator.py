from simulation.state import RocketState
from physics.gravity import calculate_gravity
from physics.propulsion import calculate_thrust, update_fuel
from physics.aerodynamics import calculate_drag
from physics.dynamics import calculate_acceleration
from physics.motion import update_velocity, update_position


def run_simulation(
    rocket,
    external_force_x,
    external_force_y=0.0,
    initial_angle=0.0,
    simulation_time=5.0,
    dt=0.1
):

    # -----------------------------
    # ESTADO INICIAL
    # -----------------------------

    state = RocketState(
        time=0.0,

        x=0.0,
        y=0.0,

        vx=0.0,
        vy=0.0,

        ax=0.0,
        ay=0.0,

        mass=(
            rocket.dry_mass
            + rocket.initial_fuel_mass
        ),

        fuel_mass=rocket.initial_fuel_mass,

        angle=initial_angle,
        area=rocket.area,

        thrust=rocket.thrust
    )


    # -----------------------------
    # HISTORIA DEL MOVIMIENTO
    # -----------------------------

    time_history = []

    x_history = []
    y_history = []

    vx_history = []
    vy_history = []

    ax_history = []
    ay_history = []

    mass_history = []
    fuel_mass_history = []

    angle_history = []

    gravity_force_x_history = []
    gravity_force_y_history = []

    thrust_force_x_history = []
    thrust_force_y_history = []

    drag_force_x_history = []
    drag_force_y_history = []

    external_force_x_history = []
    external_force_y_history = []


    # -----------------------------
    # NUMERO DE PASOS
    # -----------------------------

    number_of_steps = int(
        simulation_time / dt
    )


    # -----------------------------
    # SIMULACION
    # -----------------------------

    for step in range(number_of_steps):

        # Fuerza externa constante
        state.external_force_x = external_force_x
        state.external_force_y = external_force_y

        # Gravedad
        state = calculate_gravity(state)

        # Empuje segun el angulo
        state = calculate_thrust(state)

        # Resistencia aerodinamica
        state = calculate_drag(
            state,
            rocket
        )

        # Aceleracion
        state = calculate_acceleration(state)


        # -----------------------------
        # GUARDAR ESTADO ACTUAL
        # -----------------------------

        time_history.append(state.time)

        x_history.append(state.x)
        y_history.append(state.y)

        vx_history.append(state.vx)
        vy_history.append(state.vy)

        ax_history.append(state.ax)
        ay_history.append(state.ay)

        mass_history.append(state.mass)
        fuel_mass_history.append(
            state.fuel_mass
        )

        angle_history.append(state.angle)

        gravity_force_x_history.append(
            state.gravity_force_x
        )

        gravity_force_y_history.append(
            state.gravity_force_y
        )

        thrust_force_x_history.append(
            state.thrust_force_x
        )

        thrust_force_y_history.append(
            state.thrust_force_y
        )

        drag_force_x_history.append(
            state.drag_force_x
        )

        drag_force_y_history.append(
            state.drag_force_y
        )

        external_force_x_history.append(
            state.external_force_x
        )

        external_force_y_history.append(
            state.external_force_y
        )


        # -----------------------------
        # ACTUALIZAR MOVIMIENTO
        # -----------------------------

        state = update_velocity(
            state,
            dt
        )

        state = update_position(
            state,
            dt
        )

        state = update_fuel(
            state,
            rocket,
            dt
        )

        state.time += dt


    # -----------------------------
    # RESULTADOS
    # -----------------------------

    results = {
        "state": state,

        "time": time_history,

        "x": x_history,
        "y": y_history,

        "vx": vx_history,
        "vy": vy_history,

        "ax": ax_history,
        "ay": ay_history,

        "mass": mass_history,
        "fuel_mass": fuel_mass_history,

        "angle": angle_history,

        "gravity_force_x": gravity_force_x_history,
        "gravity_force_y": gravity_force_y_history,

        "thrust_force_x": thrust_force_x_history,
        "thrust_force_y": thrust_force_y_history,

        "drag_force_x": drag_force_x_history,
        "drag_force_y": drag_force_y_history,

        "external_force_x": external_force_x_history,
        "external_force_y": external_force_y_history
    }

    return results