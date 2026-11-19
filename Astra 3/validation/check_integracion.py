"""Verificación estructural no invasiva del proyecto ASTRA."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["app.py", "requirements.txt", "chatbot/assistant.py", "ai/prediction.py", "ai/modelo_cohete.joblib", "ai/escalador.joblib", "simulation/simulator.py", "simulation/controlled_simulator.py", "control/ls_controller.py"]

def main():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    errors = []
    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    if missing or errors:
        print("FALLO DE INTEGRACIÓN")
        for item in missing: print("Falta:", item)
        for item in errors: print("Sintaxis:", item)
        raise SystemExit(1)
    print("OK: estructura esencial y sintaxis Python verificadas.")
    print("Pendiente: ejecutar la página y evaluar el comportamiento de los controladores.")

if __name__ == "__main__":
    main()
