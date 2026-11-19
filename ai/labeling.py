import shutil

def prepare_data():
    """
    Como generate_dataset.py ya calcula la corrección óptima usando 
    el motor de Mínimos Cuadrados, este archivo simplemente prepara 
    los datos manteniendo la compatibilidad de tu flujo de trabajo.
    """
    input_file = "dataset_astra.csv"
    output_file = "dataset_entrenamiento.csv"
    
    shutil.copyfile(input_file, output_file)
    print("¡Etiquetas matemáticas generadas por Mínimos Cuadrados clonadas con éxito!")
    print(f"Datos listos para la IA guardados en '{output_file}'.")

if __name__ == "__main__":
    prepare_data()