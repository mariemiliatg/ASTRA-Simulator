from trajectory.least_squares import calculate_least_squares
from trajectory.trajectory_error import calculate_position_error

def build_state_vectors(ideal_segments, perturbed_segments, perturbed_results, segment_size):
    """
    Construye la matriz de vectores de estado X para la IA.
    X = [e, Δa, vx, vy, m, θ]
    """
    dataset = []
    for index in range(len(ideal_segments)):
        ideal_slope, _ = calculate_least_squares(ideal_segments[index])
        perturbed_slope, _ = calculate_least_squares(perturbed_segments[index])
        slope_error = ideal_slope - perturbed_slope

        ideal_x = ideal_segments[index]["x"][-1]
        ideal_y = ideal_segments[index]["y"][-1]
        real_x = perturbed_segments[index]["x"][-1]
        real_y = perturbed_segments[index]["y"][-1]
        error_position = calculate_position_error(ideal_x, ideal_y, real_x, real_y)

        history_index = min((index + 1) * segment_size - 1, len(perturbed_results["time"]) - 1)
        vx = perturbed_results["vx"][history_index]
        vy = perturbed_results["vy"][history_index]
        mass = perturbed_results["mass"][history_index]
        angle = perturbed_results["angle"][history_index]

        # Vector de entrada X acordado
        state_vector = [error_position, slope_error, vx, vy, mass, angle]
        dataset.append(state_vector)

    return dataset