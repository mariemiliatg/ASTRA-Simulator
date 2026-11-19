import math

from trajectory.least_squares import calculate_least_squares

MAX_CORRECTION_DEG = 5.0  # mismo limite por segmento que el controlador de IA


class LeastSquaresController:
    """
    Correccion de trayectoria por minimos cuadrados (sin IA).

    Al terminar cada segmento:
      1. Ajusta x = a*y + b a la trayectoria ideal y a la real (minimos cuadrados).
      2. Delta_a = a_ideal - a_real  -> error de direccion del movimiento.
      3. Error de posicion con signo ex = x_real - x_ideal (el 'e' sin signo
         de la propuesta no indica hacia que lado corregir).
      4. Delta_theta = Ka * (atan(a_ideal) - atan(a_real)) - Ke * atan(ex / L)
         con L = vy * t_lookahead, limitado a +-5 grados.

    Solo modifica el angulo; la fisica no se toca.
    """

    def __init__(self, k_slope=0.35, k_pos=0.1, lookahead=6.0,
                 max_correction_deg=MAX_CORRECTION_DEG):
        self.k_slope = k_slope
        self.k_pos = k_pos
        self.lookahead = lookahead
        self.limit = math.radians(max_correction_deg)

    def analyze_segment(self, real_segment, ideal_segment):
        """Devuelve las magnitudes de la propuesta: a_r, a_i, delta_a, e, ex."""
        a_real, _ = calculate_least_squares(real_segment)
        a_ideal, _ = calculate_least_squares(ideal_segment)
        ex = real_segment["x"][-1] - ideal_segment["x"][-1]
        ey = real_segment["y"][-1] - ideal_segment["y"][-1]
        return {
            "slope_real": a_real,
            "slope_ideal": a_ideal,
            "delta_a": a_ideal - a_real,
            "ex": ex,
            "e": math.hypot(ex, ey),
        }

    def compute_correction(self, real_segment, ideal_segment, state):
        info = self.analyze_segment(real_segment, ideal_segment)

        heading_term = math.atan(info["slope_ideal"]) - math.atan(info["slope_real"])
        distance = max(abs(state.vy), 1.0) * self.lookahead
        position_term = -math.atan(info["ex"] / distance)

        delta_theta = self.k_slope * heading_term + self.k_pos * position_term
        delta_theta = max(-self.limit, min(self.limit, delta_theta))

        info["delta_theta"] = delta_theta
        return delta_theta, info
