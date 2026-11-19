
import math
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from physics.rocket import Rocket
from simulation.simulator import run_simulation
from simulation.state import RocketState
from simulation.controlled_simulator import (
    run_controlled_simulation as run_ls_simulation
)
from physics.gravity import calculate_gravity
from physics.propulsion import calculate_thrust, update_fuel
from physics.aerodynamics import calculate_drag
from physics.dynamics import calculate_acceleration
from physics.motion import update_velocity, update_position

from trajectory.least_squares import calculate_least_squares
from trajectory.trajectory_error import calculate_position_error
from control.ls_controller import LeastSquaresController
from ai.prediction import RocketAIController
from validation.metrics import trajectory_metrics


st.set_page_config(
    page_title="ASTRA | Flight Control",
    page_icon="🚀",
    layout="wide"
)


def run_ai_simulation(rocket, wind, ideal, controller, duration, dt, segment_size):

    state = RocketState(
        mass=rocket.dry_mass + rocket.initial_fuel_mass,
        fuel_mass=rocket.initial_fuel_mass,
        area=rocket.area,
        thrust=rocket.thrust
    )

    history = {
        "time": [], "x": [], "y": [],
        "vx": [], "vy": [], "mass": [],
        "angle": []
    }

    corrections = []

    for step in range(int(duration / dt)):

        state.external_force_x = wind
        state.external_force_y = 0.0

        if step > 0 and step % segment_size == 0:

            start = step - segment_size

            real_segment = {
                "x": history["x"][start:step],
                "y": history["y"][start:step]
            }

            ideal_segment = {
                "x": ideal["x"][start:step],
                "y": ideal["y"][start:step]
            }

            real_slope, _ = calculate_least_squares(real_segment)
            ideal_slope, _ = calculate_least_squares(ideal_segment)

            delta_a = ideal_slope - real_slope

            e = calculate_position_error(
                ideal_segment["x"][-1],
                ideal_segment["y"][-1],
                state.x,
                state.y
            )

            delta_theta, info = controller.compute_correction(
                real_segment,
                ideal_segment,
                state
            )   

            state.angle += delta_theta

            corrections.append({
                "Tiempo (s)": state.time,
                "Corrección (grados)": math.degrees(delta_theta),
                "Ángulo (grados)": math.degrees(state.angle)
            })

        state = calculate_gravity(state)
        state = calculate_thrust(state)
        state = calculate_drag(state, rocket)
        state = calculate_acceleration(state)

        history["time"].append(state.time)
        history["x"].append(state.x)
        history["y"].append(state.y)
        history["vx"].append(state.vx)
        history["vy"].append(state.vy)
        history["mass"].append(state.mass)
        history["angle"].append(state.angle)

        state = update_velocity(state, dt)
        state = update_position(state, dt)
        state = update_fuel(state, rocket, dt)
        state.time += dt

    history["state"] = state
    history["corrections"] = corrections

    return history


# ENCABEZADO

st.title("🚀 ASTRA")
st.subheader("Flight Control & Trajectory Analysis")
st.caption("Simulador de vuelo 2D | Ingeniería y análisis de trayectorias")

st.divider()


# PARAMETROS

st.sidebar.title("Configuración del vuelo")

duration = st.sidebar.slider(
    "Duración de simulación (s)", 2.0, 10.0, 5.0, 0.5
)

wind = st.sidebar.slider(
    "Fuerza externa horizontal (N)", 0.0, 500.0, 200.0, 10.0
)

dt = st.sidebar.select_slider(
    "Intervalo de tiempo (s)",
    options=[0.05, 0.1, 0.2],
    value=0.1
)

segment_size = st.sidebar.slider(
    "Pasos por segmento", 5, 20, 10
)

st.sidebar.divider()

st.sidebar.caption("Parámetros físicos del modelo")

dry_mass = st.sidebar.number_input(
    "Masa seca (kg)", value=1000.0, min_value=1.0
)

fuel_mass = st.sidebar.number_input(
    "Combustible inicial (kg)", value=500.0, min_value=1.0
)

thrust = st.sidebar.number_input(
    "Empuje (N)", value=20000.0, min_value=1.0
)

area = st.sidebar.number_input(
    "Área de referencia (m²)", value=1.0, min_value=0.01
)

cd = st.sidebar.number_input(
    "Coeficiente de arrastre", value=0.5, min_value=0.0
)

isp = st.sidebar.number_input(
    "Impulso específico (s)", value=250.0, min_value=1.0
)


# EJECUCION

if st.button("▶ EJECUTAR SIMULACIÓN", type="primary", use_container_width=True):

    try:
        rocket = Rocket(
            dry_mass=dry_mass,
            initial_fuel_mass=fuel_mass,
            thrust=thrust,
            specific_impulse=isp,
            cd=cd,
            area=area
        )

        with st.spinner("Ejecutando los cuatro escenarios..."):

            ideal = run_simulation(
                rocket, 0.0,
                simulation_time=duration, dt=dt
            )

            perturbed = run_simulation(
                rocket, wind,
                simulation_time=duration, dt=dt
            )

            ls_controller = LeastSquaresController()

            ls = run_ls_simulation(
                rocket, wind, ideal, ls_controller,
                simulation_time=duration,
                dt=dt,
                segment_size=segment_size
            )

            ai_controller = RocketAIController()

            ai = run_ai_simulation(
                rocket, wind, ideal, ai_controller,
                duration, dt, segment_size
            )

            metrics = {
                "Perturbada": trajectory_metrics(ideal, perturbed),
                "Mínimos cuadrados": trajectory_metrics(ideal, ls),
                "IA": trajectory_metrics(ideal, ai)
            }

            st.session_state["results"] = {
                "ideal": ideal,
                "perturbed": perturbed,
                "ls": ls,
                "ai": ai,
                "metrics": metrics
            }

        st.success("Simulación completada.")

    except Exception as error:
        st.error(f"No se pudo ejecutar la simulación: {error}")


# MOSTRAR RESULTADOS

if "results" in st.session_state:

    results = st.session_state["results"]

    ideal = results["ideal"]
    perturbed = results["perturbed"]
    ls = results["ls"]
    ai = results["ai"]
    metrics = results["metrics"]

    st.header("Panel de resultados")

    # INDICADORES

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "RMSE perturbada",
        f"{metrics['Perturbada']['rmse']:.4f} m"
    )

    col2.metric(
        "RMSE mínimos cuadrados",
        f"{metrics['Mínimos cuadrados']['rmse']:.4f} m"
    )

    col3.metric(
        "RMSE inteligencia artificial",
        f"{metrics['IA']['rmse']:.4f} m"
    )

    st.divider()

    # TRAYECTORIAS

    st.header("Comparación de trayectorias")

    fig = go.Figure()

    scenarios = [
        (ideal, "Ideal", "green", "dash"),
        (perturbed, "Perturbada", "red", "solid"),
        (ls, "Mínimos cuadrados", "orange", "solid"),
        (ai, "Inteligencia artificial", "blue", "solid")
    ]

    for data, name, color, dash in scenarios:
        fig.add_trace(go.Scatter(
            x=data["x"],
            y=data["y"],
            mode="lines",
            name=name,
            line=dict(color=color, dash=dash, width=2)
        ))

    fig.update_layout(
        xaxis_title="Posición horizontal (m)",
        yaxis_title="Altura (m)",
        template="plotly_dark",
        height=600,
        legend_title="Escenarios"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # METRICAS

    st.header("Evaluación de controladores")

    metric_table = pd.DataFrame({
        name: {
            "RMSE (m)": values["rmse"],
            "Error máximo (m)": values["max"],
            "Error final (m)": values["final"]
        }
        for name, values in metrics.items()
    }).T

    st.dataframe(metric_table, use_container_width=True)

    base = metrics["Perturbada"]["rmse"]

    if base > 0:
        reduction = (
            1 - metrics["Mínimos cuadrados"]["rmse"] / base
        ) * 100

        st.metric(
            "Reducción de RMSE con mínimos cuadrados",
            f"{reduction:.2f}%"
        )

    ai_better = (
        metrics["IA"]["rmse"] < metrics["Perturbada"]["rmse"]
    )

    if ai_better:
        st.success("La IA redujo el RMSE respecto a la trayectoria perturbada.")
    else:
        st.warning("La IA no redujo el RMSE en este escenario.")

    st.divider()

    # TELEMETRIA

    st.header("Telemetría")

    selected = st.selectbox(
        "Selecciona el escenario",
        ["Ideal", "Perturbada", "Mínimos cuadrados", "IA"]
    )

    selected_data = {
        "Ideal": ideal,
        "Perturbada": perturbed,
        "Mínimos cuadrados": ls,
        "IA": ai
    }[selected]

    available = [
        key for key in ["x", "y", "vx", "vy", "mass", "fuel_mass", "angle", "ax", "ay"]
        if key in selected_data
    ]

    telemetry_labels = {
        "x": "Posición X (m)",
        "y": "Altura Y (m)",
        "vx": "Velocidad X (m/s)",
        "vy": "Velocidad Y (m/s)",
        "mass": "Masa (kg)",
        "fuel_mass": "Combustible (kg)",
        "angle": "Ángulo (rad)",
        "ax": "Aceleración X (m/s²)",
        "ay": "Aceleración Y (m/s²)"
    }

    variable = st.selectbox(
        "Variable",
        available,
        format_func=lambda key: telemetry_labels[key]
    )

    telemetry_fig = go.Figure()

    telemetry_fig.add_trace(go.Scatter(
        x=selected_data["time"],
        y=selected_data[variable],
        mode="lines",
        name=telemetry_labels[variable]
    ))

    telemetry_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Tiempo (s)",
        yaxis_title=telemetry_labels[variable],
        height=350
    )

    st.plotly_chart(telemetry_fig, use_container_width=True)

    st.divider()

    # CORRECCIONES

    st.header("Historial de correcciones")

    correction_type = st.selectbox(
        "Controlador",
        ["Mínimos cuadrados", "Inteligencia artificial"]
    )

    if correction_type == "Mínimos cuadrados":
        corrections = ls["corrections"]

        if corrections:
            correction_df = pd.DataFrame(corrections)
            correction_df["delta_theta_deg"] = correction_df["delta_theta"].apply(
                math.degrees
            )
            correction_df["angle_deg"] = correction_df["angle"].apply(
                math.degrees
            )

            st.dataframe(
                correction_df,
                use_container_width=True
            )
        else:
            st.info("No hubo correcciones en esta simulación.")

    else:
        corrections = ai["corrections"]

        if corrections:
            st.dataframe(
                pd.DataFrame(corrections),
                use_container_width=True
            )
        else:
            st.info("No hubo correcciones en esta simulación.")

else:
    st.info("Configura los parámetros y pulsa EJECUTAR SIMULACIÓN para comenzar.")
