from sklearn.neural_network import MLPRegressor

def create_model():
    """
    Crea una red neuronal (Multilayer Perceptron).
    Se amplió la capacidad a (64, 32) para absorber la dinámica
    no lineal de vuelo.
    """
    model = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation='relu',
        solver='adam',
        max_iter=1500,
        random_state=42
    )
    return model