import math

from simulation.state import RocketState
from physics.rocket import Rocket
from physics.gravity import calculate_gravity
from physics.propulsion import calculate_thrust
from physics.aerodynamics import calculate_drag


G = 9.8
RHO = 1.225


# --------------------------------
# PRUEBA DE GRAVEDAD
# --------------------------------

def test_gravity():

    state = RocketState(
        mass=1500.0
    )

    state = calculate_gravity(state)

    theoretical_value = (
        -state.mass * G
    )

    calculated_value = (
        state.gravity_force_y
    )

    error = abs(
        theoretical_value
        - calculated_value
    )

    print()
    print("PRUEBA DE GRAVEDAD")

    print(
        "Valor teorico:",
        theoretical_value,
        "N"
    )

    print(
        "Valor calculado:",
        calculated_value,
        "N"
    )

    print(
        "Error:",
        error
    )


# --------------------------------
# PRUEBA DE EMPUJE
# --------------------------------

def test_thrust():

    state = RocketState(
        thrust=20000.0,
        fuel_mass=500.0,
        angle=math.radians(5.0)
    )

    state = calculate_thrust(state)

    theoretical_x = (
        state.thrust
        * math.sin(state.angle)
    )

    theoretical_y = (
        state.thrust
        * math.cos(state.angle)
    )

    error_x = abs(
        theoretical_x
        - state.thrust_force_x
    )

    error_y = abs(
        theoretical_y
        - state.thrust_force_y
    )

    print()
    print("PRUEBA DE EMPUJE")

    print(
        "Tx teorico:",
        theoretical_x,
        "N"
    )

    print(
        "Tx calculado:",
        state.thrust_force_x,
        "N"
    )

    print(
        "Error Tx:",
        error_x
    )

    print(
        "Ty teorico:",
        theoretical_y,
        "N"
    )

    print(
        "Ty calculado:",
        state.thrust_force_y,
        "N"
    )

    print(
        "Error Ty:",
        error_y
    )


# --------------------------------
# PRUEBA DE DRAG
# --------------------------------

def test_drag():

    rocket = Rocket(
        dry_mass=1000.0,
        initial_fuel_mass=500.0,
        thrust=20000.0,
        specific_impulse=250.0,
        cd=0.5,
        area=1.0
    )

    state = RocketState(
        vx=0.0,
        vy=20.0
    )

    state = calculate_drag(
        state,
        rocket
    )

    speed = math.sqrt(
        state.vx**2
        + state.vy**2
    )

    theoretical_drag_x = (
        -0.5
        * RHO
        * rocket.cd
        * rocket.area
        * speed
        * state.vx
    )

    theoretical_drag_y = (
        -0.5
        * RHO
        * rocket.cd
        * rocket.area
        * speed
        * state.vy
    )

    error_x = abs(
        theoretical_drag_x
        - state.drag_force_x
    )

    error_y = abs(
        theoretical_drag_y
        - state.drag_force_y
    )

    print()
    print("PRUEBA DE DRAG")

    print(
        "Drag teorico en x:",
        theoretical_drag_x,
        "N"
    )

    print(
        "Drag calculado en x:",
        state.drag_force_x,
        "N"
    )

    print(
        "Error drag x:",
        error_x
    )

    print(
        "Drag teorico en y:",
        theoretical_drag_y,
        "N"
    )

    print(
        "Drag calculado en y:",
        state.drag_force_y,
        "N"
    )

    print(
        "Error drag y:",
        error_y
    )


# --------------------------------
# PRUEBA DE FLUJO DE MASA
# --------------------------------

def test_mass_flow():

    rocket = Rocket(
        dry_mass=1000.0,
        initial_fuel_mass=500.0,
        thrust=20000.0,
        specific_impulse=250.0,
        cd=0.5,
        area=1.0
    )

    theoretical_mass_flow = (
        rocket.thrust
        / (
            rocket.specific_impulse
            * G
        )
    )

    print()
    print("PRUEBA DE FLUJO DE MASA")

    print(
        "Flujo teorico:",
        theoretical_mass_flow,
        "kg/s"
    )


# --------------------------------
# EJECUTAR TODAS LAS PRUEBAS
# --------------------------------

def run_physics_tests():

    print()
    print("--------------------------")
    print("VALIDACION DEL MOTOR FISICO")
    print("--------------------------")

    test_gravity()

    test_thrust()

    test_drag()

    test_mass_flow()

    print()
    print("--------------------------")
    print("FIN DE LAS PRUEBAS")
    print("--------------------------")