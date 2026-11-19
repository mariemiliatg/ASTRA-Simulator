from physics.rocket import Rocket

from simulation.simulator import run_simulation

from visualization.plots import (
    plot_trajectories
)

from trajectory.segmentation import (
    divide_trajectory
)

from trajectory.least_squares import (
    calculate_least_squares
)

from trajectory.trajectory_error import (
    calculate_position_error
)


# --------------------------------
# DATOS DEL COHETE
# --------------------------------

rocket = Rocket(
    dry_mass=1000.0,
    initial_fuel_mass=500.0,
    thrust=20000.0,
    specific_impulse=250.0,
    cd=0.5,
    area=1.0
)


# --------------------------------
# CONFIGURACION DE LA SIMULACION
# --------------------------------

simulation_time = 5.0
dt = 0.1

external_force_x = 200.0
external_force_y = 0.0

segment_size = 10


# --------------------------------
# TRAYECTORIA IDEAL
# --------------------------------

ideal_results = run_simulation(
    rocket=rocket,

    external_force_x=0.0,
    external_force_y=0.0,

    initial_angle=0.0,

    simulation_time=simulation_time,
    dt=dt
)


# --------------------------------
# TRAYECTORIA PERTURBADA
# --------------------------------

perturbed_results = run_simulation(
    rocket=rocket,

    external_force_x=external_force_x,
    external_force_y=external_force_y,

    initial_angle=0.0,

    simulation_time=simulation_time,
    dt=dt
)


# --------------------------------
# ESTADOS FINALES
# --------------------------------

ideal_state = ideal_results["state"]

perturbed_state = (
    perturbed_results["state"]
)


# --------------------------------
# ERROR FINAL DE POSICION
# --------------------------------

final_position_error = (
    calculate_position_error(

        ideal_state.x,
        ideal_state.y,

        perturbed_state.x,
        perturbed_state.y
    )
)


# --------------------------------
# SEGMENTACION DE TRAYECTORIAS
# --------------------------------

ideal_segments = divide_trajectory(
    ideal_results,
    segment_size
)

perturbed_segments = divide_trajectory(
    perturbed_results,
    segment_size
)


# --------------------------------
# RESULTADOS GENERALES
# --------------------------------

print()
print("------------------------------")
print("RESULTADOS GENERALES DE ASTRA")
print("------------------------------")


print()
print("TRAYECTORIA IDEAL")

print(
    "Posicion final en x:",
    ideal_state.x,
    "m"
)

print(
    "Posicion final en y:",
    ideal_state.y,
    "m"
)


print()
print("TRAYECTORIA PERTURBADA")

print(
    "Posicion final en x:",
    perturbed_state.x,
    "m"
)

print(
    "Posicion final en y:",
    perturbed_state.y,
    "m"
)


print()

print(
    "Error final de posicion:",
    final_position_error,
    "m"
)

print(
    "Fuerza externa aplicada:",
    external_force_x,
    "N"
)

print(
    "Masa final:",
    perturbed_state.mass,
    "kg"
)

print(
    "Combustible restante:",
    perturbed_state.fuel_mass,
    "kg"
)


# --------------------------------
# ANALISIS POR SEGMENTOS
# --------------------------------

print()
print("------------------------------")
print("ANALISIS POR SEGMENTOS")
print("------------------------------")


for index in range(
    len(ideal_segments)
):

    # ----------------------------
    # MINIMOS CUADRADOS
    # ----------------------------

    ideal_slope, ideal_intercept = (
        calculate_least_squares(
            ideal_segments[index]
        )
    )

    perturbed_slope, perturbed_intercept = (
        calculate_least_squares(
            perturbed_segments[index]
        )
    )


    slope_error = (
        ideal_slope
        - perturbed_slope
    )


    # ----------------------------
    # ULTIMO PUNTO DEL SEGMENTO
    # ----------------------------

    ideal_x = (
        ideal_segments[index]["x"][-1]
    )

    ideal_y = (
        ideal_segments[index]["y"][-1]
    )

    real_x = (
        perturbed_segments[index]["x"][-1]
    )

    real_y = (
        perturbed_segments[index]["y"][-1]
    )


    # ----------------------------
    # ERROR DE POSICION
    # ----------------------------

    error_position = (
        calculate_position_error(

            ideal_x,
            ideal_y,

            real_x,
            real_y
        )
    )


    # ----------------------------
    # DATOS FISICOS DEL SEGMENTO
    # ----------------------------

    history_index = min(
        (index + 1) * segment_size - 1,
        len(
            perturbed_results["time"]
        ) - 1
    )


    vx = (
        perturbed_results["vx"]
        [history_index]
    )

    vy = (
        perturbed_results["vy"]
        [history_index]
    )

    mass = (
        perturbed_results["mass"]
        [history_index]
    )

    angle = (
        perturbed_results["angle"]
        [history_index]
    )


    # ----------------------------
    # RESULTADOS DEL SEGMENTO
    # ----------------------------

    print()

    print(
        "Segmento:",
        index + 1
    )

    print(
        "Pendiente ideal:",
        ideal_slope
    )

    print(
        "Pendiente perturbada:",
        perturbed_slope
    )

    print(
        "Error de pendiente:",
        slope_error
    )

    print(
        "Error de posicion:",
        error_position,
        "m"
    )

    print(
        "Velocidad en x:",
        vx,
        "m/s"
    )

    print(
        "Velocidad en y:",
        vy,
        "m/s"
    )

    print(
        "Masa:",
        mass,
        "kg"
    )

    print(
        "Angulo:",
        angle,
        "rad"
    )


# --------------------------------
# TELEMETRIA FINAL
# --------------------------------

print()
print("------------------------------")
print("TELEMETRIA FINAL")
print("------------------------------")


print(
    "Velocidad final en x:",
    perturbed_state.vx,
    "m/s"
)

print(
    "Velocidad final en y:",
    perturbed_state.vy,
    "m/s"
)

print(
    "Aceleracion final en x:",
    perturbed_state.ax,
    "m/s^2"
)

print(
    "Aceleracion final en y:",
    perturbed_state.ay,
    "m/s^2"
)

print(
    "Angulo final:",
    perturbed_state.angle,
    "rad"
)

print(
    "Numero de puntos guardados:",
    len(
        perturbed_results["time"]
    )
)


# --------------------------------
# GRAFICA
# --------------------------------

plot_trajectories(
    ideal_results,
    perturbed_results
)