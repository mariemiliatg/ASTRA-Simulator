import csv
import random
from physics.rocket import Rocket
from simulation.simulator import run_simulation
from simulation.controlled_simulator import run_controlled_simulation
from control.ls_controller import LeastSquaresController

NUM_SIMULATIONS = 2000
SIMULATION_TIME = 5.0
DT = 0.1
SEGMENT_SIZE = 10

class NoisyLSController(LeastSquaresController):
    """
    Controlador modificado solo para generar datos. Añade ruido a las 
    correcciones para forzar al cohete a desestabilizarse, enseñando 
    a la IA cómo salir de estados problemáticos (ángulos != 0).
    """
    def compute_correction(self, real_segment, ideal_segment, state):
        delta_theta, info = super().compute_correction(real_segment, ideal_segment, state)
        
        # Etiqueta objetivo: La corrección pura de mínimos cuadrados
        info["label_delta_theta"] = delta_theta
        info["state_angle"] = state.angle 
        
        # Ruido para forzar exploración de estados
        noisy_delta_theta = delta_theta + random.uniform(-0.05, 0.05)
        noisy_delta_theta = max(-self.limit, min(self.limit, noisy_delta_theta))
        
        return noisy_delta_theta, info

def generate_dataset():
    rocket = Rocket(dry_mass=1000.0, initial_fuel_mass=500.0, thrust=20000.0, specific_impulse=250.0, cd=0.5, area=1.0)
    ideal_results = run_simulation(rocket, external_force_x=0.0, simulation_time=SIMULATION_TIME, dt=DT)
    
    print(f"Generando {NUM_SIMULATIONS} simulaciones de vuelo con Imitation Learning... Por favor espera.")
    all_data = []
    noisy_controller = NoisyLSController()

    for i in range(NUM_SIMULATIONS):
        random_wind = random.uniform(-500.0, 500.0)
        res = run_controlled_simulation(rocket, random_wind, ideal_results, noisy_controller, SIMULATION_TIME, DT, SEGMENT_SIZE)
        
        for corr in res["corrections"]:
            # Vector X y Etiqueta Y (delta_theta del LS_Controller)
            row = [
                corr["e"],
                corr["delta_a"],
                res["vx"][corr["step"]],
                res["vy"][corr["step"]],
                res["mass"][corr["step"]],
                corr["state_angle"], 
                corr["label_delta_theta"]
            ]
            all_data.append(row)

    csv_filename = "dataset_astra.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["error_pos", "error_pendiente", "vx", "vy", "masa", "angulo", "delta_theta"])
        writer.writerows(all_data)

    print(f"¡Dataset generado con éxito! Se guardaron {len(all_data)} filas en '{csv_filename}'.")

if __name__ == "__main__":
    generate_dataset()