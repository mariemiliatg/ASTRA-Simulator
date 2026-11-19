import math
import matplotlib.pyplot as plt
from physics.rocket import Rocket
from simulation.simulator import run_simulation
from simulation.controlled_simulator import run_controlled_simulation
from control.ls_controller import LeastSquaresController
from ai.prediction import RocketAIController

def compute_rmse(ideal, real):
    error_sum = 0
    for ix, iy, rx, ry in zip(ideal["x"], ideal["y"], real["x"], real["y"]):
        error_sum += (rx - ix)**2 + (ry - iy)**2
    return math.sqrt(error_sum / len(ideal["x"]))

def main():
    simulation_time = 5.0
    dt = 0.1
    segment_size = 10
    external_force_x = 200.0  # Viento de prueba estándar

    rocket = Rocket(dry_mass=1000.0, initial_fuel_mass=500.0, thrust=20000.0, specific_impulse=250.0, cd=0.5, area=1.0)
    print("Iniciando validación de Controladores ASTRA...\n")

    ideal_results = run_simulation(rocket, external_force_x=0.0, simulation_time=simulation_time, dt=dt)
    perturbed_results = run_simulation(rocket, external_force_x=external_force_x, simulation_time=simulation_time, dt=dt)

    ls_controller = LeastSquaresController()
    ls_results = run_controlled_simulation(rocket, external_force_x, ideal_results, ls_controller, simulation_time, dt, segment_size)

    ai_controller = RocketAIController()
    ai_results = run_controlled_simulation(rocket, external_force_x, ideal_results, ai_controller, simulation_time, dt, segment_size)

    # MÉTRICAS
    rmse_sin = compute_rmse(ideal_results, perturbed_results)
    rmse_ls = compute_rmse(ideal_results, ls_results)
    rmse_ai = compute_rmse(ideal_results, ai_results)

    final_sin = math.hypot(perturbed_results["x"][-1] - ideal_results["x"][-1], perturbed_results["y"][-1] - ideal_results["y"][-1])
    final_ls = math.hypot(ls_results["x"][-1] - ideal_results["x"][-1], ls_results["y"][-1] - ideal_results["y"][-1])
    final_ai = math.hypot(ai_results["x"][-1] - ideal_results["x"][-1], ai_results["y"][-1] - ideal_results["y"][-1])

    print("--------------------------------------------------")
    print(f"RESULTADOS DE VUELO (Fuerza Externa: {external_force_x} N)")
    print("--------------------------------------------------")
    print(f"1. SIN CORRECCIÓN:")
    print(f"   - RMSE: {rmse_sin:.4f} m")
    print(f"   - Error final: {final_sin:.4f} m\n")

    print(f"2. MÍNIMOS CUADRADOS (Fase 3):")
    print(f"   - RMSE: {rmse_ls:.4f} m")
    print(f"   - Error final: {final_ls:.4f} m\n")

    print(f"3. INTELIGENCIA ARTIFICIAL (Fase 4):")
    print(f"   - RMSE: {rmse_ai:.4f} m")
    print(f"   - Error final: {final_ai:.4f} m")
    
    if rmse_ai < rmse_sin:
        reduccion_ai = (1 - (rmse_ai / rmse_sin)) * 100
        print(f"\n¡Éxito! La IA estabilizó el vuelo y redujo el error global en un {reduccion_ai:.2f}%.")
    else:
        print("\nLa IA aún no logra superar la trayectoria perturbada.")

    # GRÁFICA COMPARATIVA
    plt.figure(figsize=(9, 10))
    plt.plot(ideal_results["x"], ideal_results["y"], label="Trayectoria Ideal (Centro)", color="green", linestyle="--")
    plt.plot(perturbed_results["x"], perturbed_results["y"], label="Perturbada (Sin Control)", color="red", alpha=0.5)
    plt.plot(ls_results["x"], ls_results["y"], label="Mínimos Cuadrados", color="orange", linewidth=2.5)
    plt.plot(ai_results["x"], ai_results["y"], label="Controlada (Inteligencia Artificial)", color="blue", linewidth=2)

    plt.xlabel("Posición x (m)")
    plt.ylabel("Posición y (m)")
    plt.title("Comparación Analítica de Controladores de Trayectoria")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()