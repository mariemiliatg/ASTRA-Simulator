import csv
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from ai.model import create_model

def train_ai():
    X = []
    y = []

    with open("dataset_entrenamiento.csv", mode="r") as file:
        reader = csv.reader(file)
        next(reader) 
        for row in reader:
            X.append([float(val) for val in row[:6]])
            y.append(float(row[6]))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # El escalador normaliza las variables físicas para no confundir a la red neuronal
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Entrenando la IA (Clonación de Comportamiento LS)... Por favor espera.")
    model = create_model()
    model.fit(X_train_scaled, y_train)

    predictions = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print("\n------------------------------")
    print("RESULTADOS DEL ENTRENAMIENTO")
    print("------------------------------")
    print(f"Error Cuadrático Medio (MSE): {mse:.6f}")
    print(f"Precisión R^2 (1.00 es perfecto): {r2:.4f}")

    joblib.dump(model, "ai/modelo_cohete.joblib")
    joblib.dump(scaler, "ai/escalador.joblib")
    print("\n¡IA y escalador entrenados y guardados exitosamente!")

if __name__ == "__main__":
    train_ai()