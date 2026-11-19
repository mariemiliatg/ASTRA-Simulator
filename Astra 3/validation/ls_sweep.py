"""
Barrido de viento (-500 N a 500 N) para evaluar el corrector por minimos
cuadrados contra el caso perturbado sin correccion.
Ejecutar desde la raiz del proyecto:
    python -m validation.ls_sweep          (angulo inicial 0 grados)
    python -m validation.ls_sweep 10       (angulo inicial de 10 grados)
"""
import itertools
import math
import sys

from physics.rocket import Rocket
from simulation.simulator import run_simulation
from simulation.controlled_simulator import run_controlled_simulation
from control.ls_controller import LeastSquaresController
from control.ls_controller_experimental import LeastSquaresController as ExperimentalController
from validation.metrics import trajectory_metrics

SIM_TIME, DT, SEG = 5.0, 0.1, 10
WINDS = [w for w in range(-500, 501, 50) if w != 0]


def make_rocket():
    return Rocket(dry_mass=1000.0, initial_fuel_mass=500.0, thrust=20000.0,
                  specific_impulse=250.0, cd=0.5, area=1.0)


def evaluate(controller, winds=WINDS, seg=SEG, initial_angle_deg=0.0):
    rocket = make_rocket()
    theta0 = math.radians(initial_angle_deg)  # el misil despega con este angulo en los 3 casos
    ideal = run_simulation(rocket, external_force_x=0.0, initial_angle=theta0,
                           simulation_time=SIM_TIME, dt=DT)
    rows = []
    for w in winds:
        pert = run_simulation(rocket, external_force_x=float(w), initial_angle=theta0,
                              simulation_time=SIM_TIME, dt=DT)
        corr = run_controlled_simulation(rocket, float(w), ideal, controller,
                                         simulation_time=SIM_TIME, dt=DT, segment_size=seg,
                                         initial_angle=theta0)
        rows.append((w, trajectory_metrics(ideal, pert), trajectory_metrics(ideal, corr)))
    return rows


def mean_rmse(rows):
    return sum(r[2]["rmse"] for r in rows) / len(rows)


def tune():
    best = None
    for ks, kp, la in itertools.product(
        [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0],
        [0.0, 0.25, 0.5, 1.0, 1.5, 2.0],
        [0.5, 1.0, 2.0, 4.0],
    ):
        rows = evaluate(LeastSquaresController(ks, kp, la))
        score = mean_rmse(rows)
        if best is None or score < best[0]:
            best = (score, ks, kp, la)
    return best


def report(controller, seg=SEG, initial_angle_deg=0.0):
    rows = evaluate(controller, seg=seg, initial_angle_deg=initial_angle_deg)
    print(f"{'Fext (N)':>9} {'RMSE sin':>9} {'RMSE LS':>9} {'Final sin':>10} {'Final LS':>9} {'Mejora RMSE':>12}")
    for w, m0, m1 in rows:
        print(f"{w:9d} {m0['rmse']:9.3f} {m1['rmse']:9.3f} {m0['final']:10.3f} "
              f"{m1['final']:9.3f} {(1 - m1['rmse'] / m0['rmse']) * 100:11.1f}%")
    n_better = sum(1 for _, m0, m1 in rows if m1["rmse"] < m0["rmse"])
    print(f"\nMejora en {n_better}/{len(rows)} vientos. RMSE medio: "
          f"{sum(r[1]['rmse'] for r in rows)/len(rows):.3f} -> {mean_rmse(rows):.3f} m")


if __name__ == "__main__":
    angle = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    print(f"Barrido con ganancias por defecto de LeastSquaresController() | Angulo inicial: {angle}")
    report(LeastSquaresController(), initial_angle_deg=angle)
    print("\n=== CONTROLADOR EXPERIMENTAL ===")
    report(ExperimentalController(), initial_angle_deg=angle)
