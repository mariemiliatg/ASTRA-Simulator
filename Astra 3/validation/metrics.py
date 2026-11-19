import math


def position_errors(ideal, real):
    """Error e_j = distancia entre trayectoria ideal y real en cada instante."""
    return [
        math.hypot(xr - xi, yr - yi)
        for xi, yi, xr, yr in zip(ideal["x"], ideal["y"], real["x"], real["y"])
    ]


def trajectory_metrics(ideal, real):
    """RMSE, error maximo y error final (seccion 12 de la propuesta)."""
    errors = position_errors(ideal, real)
    n = len(errors)
    return {
        "rmse": math.sqrt(sum(e * e for e in errors) / n),
        "max": max(errors),
        "final": errors[-1],
    }
