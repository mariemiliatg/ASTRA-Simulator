import joblib
import math
import numpy as np
from trajectory.least_squares import calculate_least_squares

class RocketAIController:
    def __init__(self, model_path="ai/modelo_cohete.joblib", scaler_path="ai/escalador.joblib"):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.limit = math.radians(5.0)

    def compute_correction(self, real_segment, ideal_segment, state):
        """
        Calcula las variables de estado usando la misma lógica que el controlador LS
        e invoca a la red neuronal manteniendo la firma de simulación.
        """
        a_real, _ = calculate_least_squares(real_segment)
        a_ideal, _ = calculate_least_squares(ideal_segment)
        delta_a = a_ideal - a_real
        
        ex = real_segment["x"][-1] - ideal_segment["x"][-1]
        ey = real_segment["y"][-1] - ideal_segment["y"][-1]
        e = math.hypot(ex, ey) # Error de distancia estricto
        
        # 1. Vector de entrada intacto: [e, Δa, vx, vy, m, θ]
        X_input = np.array([[e, delta_a, state.vx, state.vy, state.mass, state.angle]])
        X_scaled = self.scaler.transform(X_input)
        
        # 2. Predicción y límite físico de seguridad
        delta_theta = float(self.model.predict(X_scaled)[0])
        delta_theta = max(-self.limit, min(self.limit, delta_theta))
        
        info = {
            "e": e,
            "delta_a": delta_a,
            "delta_theta": delta_theta
        }
            
        return delta_theta, info