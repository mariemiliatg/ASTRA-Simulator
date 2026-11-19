from chatbot.assistant import answer_question
from chatbot.knowledge import summarize_flight
from physics.rocket import Rocket
from simulation.simulator import run_simulation

rocket = Rocket(
    dry_mass=1000.0,
    initial_fuel_mass=500.0,
    thrust=20000.0,
    specific_impulse=250.0,
    cd=0.5,
    area=1.0
)

results = run_simulation(
    rocket,
    external_force_x=200.0,
    simulation_time=5.0,
    dt=0.1
)

summary = summarize_flight(results, "ASTRA Test Rocket")

print("\n===== Asistente conversacional de Astra =====")
print("\n=== Puedes preguntar datos del vuelo, como duracion, velocidad, posicion final del cohete,")
print("\n=== fuerzas de gravedad o resistencia de aire, fuerza de empuje, etc.")
while True:
    question = input("\nYou: ")

    if question.lower() in ["salir", "apagar", "adios", "chao", "gracias"]:
        print("ASTRA: Adios primo")
        break

    response = answer_question(question, summary)

    print("ASTRA:", response)


