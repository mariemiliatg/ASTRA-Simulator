# ASTRA - Modulo 3: correccion de trayectoria por minimos cuadrados

Corrector sin IA. Al terminar cada segmento (10 pasos = 1 s):

1. Ajusta x = a*y + b a la trayectoria ideal y a la real (trajectory/least_squares.py, sin cambios).
2. Calcula delta_a = a_ideal - a_real y el error de posicion con signo ex = x_real - x_ideal.
3. delta_theta = Ka*(atan(a_ideal) - atan(a_real)) - Ke*atan(ex / (vy*L)), limitado a +-5 grados.
4. state.angle += delta_theta. La fisica (physics/) no se modifica.

Ganancias por defecto (Ka=0.35, Ke=0.1, L=6 s): ajustadas con vientos de -500 a 500 N
y validadas con vientos distintos (+-25, +-75, ... +-475 N).

## Archivos nuevos
- control/ls_controller.py            LeastSquaresController
- simulation/controlled_simulator.py  simulacion con correccion (misma fisica)
- validation/metrics.py               RMSE, error maximo, error final
- validation/ls_sweep.py              barrido de viento y tabla de resultados
- main.py (modificado)                agrega el escenario LS, sus metricas y su curva en la grafica

## Ejecucion (desde la raiz del proyecto)
    python main.py
    python -m validation.ls_sweep

Los modulos de IA (ai/, main.py) no se tocaron.

## Proyecto completo (3 modulos)
- Modulo 1 (fisica): physics/, simulation/simulator.py, simulation/state.py, trajectory/, validation/physics_tests.py,
  visualization/. Su main original se conserva como main_modulo1.py (usa g = 9.8, regla del proyecto).
- Modulo 2 (IA): ai/, generate_dataset.py, datasets .csv. Se ejecuta dentro de main.py.
- Modulo 3 (minimos cuadrados): control/, simulation/controlled_simulator.py, validation/metrics.py, validation/ls_sweep.py.
- main.py corre los modulos 2 y 3 juntos. Pruebas de fisica: python -m validation.physics_tests
