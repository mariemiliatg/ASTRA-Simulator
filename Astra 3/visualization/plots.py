import matplotlib.pyplot as plt


def plot_trajectories(
    ideal_results,
    perturbed_results
):

    plt.figure()

    plt.plot(
        ideal_results["x"],
        ideal_results["y"],
        label="Trayectoria ideal"
    )

    plt.plot(
        perturbed_results["x"],
        perturbed_results["y"],
        label="Trayectoria perturbada"
    )

    plt.xlabel("Posicion x (m)")
    plt.ylabel("Posicion y (m)")

    plt.title(
        "Comparacion de trayectorias"
    )

    plt.legend()
    plt.grid()

    plt.show()