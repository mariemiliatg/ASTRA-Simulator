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
from chatbot.assistant import answer_question
from chatbot.knowledge import summarize_flight


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



# ASTRA MISSION CONTROL — Interfaz de presentación
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans',sans-serif;}
[data-testid="stApp"] {background: radial-gradient(ellipse at 82% 0%, #152747 0%, #090f20 43%, #070b17 100%);color:#eaf2ff;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#111b32,#0b1122);border-right:1px solid #263551;}
[data-testid="stSidebar"] * {color:#e4ecff;}
.block-container {padding-top:1.8rem;padding-bottom:4rem;max-width:1900px;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.025em;}
[data-testid="stMetric"] {background:linear-gradient(145deg,rgba(26,43,73,.95),rgba(12,22,42,.96));border:1px solid #2c4265;border-radius:16px;padding:18px 20px;box-shadow:0 12px 32px #00000020;}
[data-testid="stMetricLabel"] {color:#9fb2d3;}
[data-testid="stMetricValue"] {color:#f3f7ff;font-family:'Space Grotesk',sans-serif;}
.stButton>button[kind="primary"] {background:linear-gradient(90deg,#18c7e6,#6d73ff);color:#061021;border:0;border-radius:12px;font-weight:800;letter-spacing:.035em;min-height:48px;box-shadow:0 5px 24px #18c7e633;}
.stButton>button[kind="primary"]:hover {background:linear-gradient(90deg,#58e4f7,#9b9dff);color:#061021;}
[data-baseweb="tab-list"] {gap:12px;border-bottom:1px solid #283a59;}
button[data-baseweb="tab"] {background:#121e35;border-radius:11px 11px 0 0;padding:10px 17px;color:#b8c9e5;}
button[aria-selected="true"][data-baseweb="tab"] {color:#6fe9fa;border-bottom:2px solid #4bdcf3;}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {border:1px solid #263753;border-radius:14px;overflow:hidden;}
.astra-kicker {font-size:.75rem;letter-spacing:.22em;font-weight:800;color:#6de2f5;margin-bottom:.55rem;}
.astra-hero {padding:22px 26px;background:linear-gradient(105deg,rgba(26,48,82,.92),rgba(14,24,47,.82));border:1px solid #2a4265;border-radius:22px;margin-bottom:16px;position:relative;}
.astra-hero h1 {font-size:clamp(1.7rem,2.5vw,2.5rem);margin:0;color:#fff;line-height:1.1;}
.astra-hero p {color:#afc1df;margin:12px 0 0;max-width:650px;}
.astra-pill {display:inline-block;border:1px solid #287c8d;color:#75e8ed;background:#123846;border-radius:99px;padding:5px 12px;font-size:.76rem;font-weight:700;margin-top:15px;}
.astra-section {font-size:.79rem;letter-spacing:.13em;color:#8ea7c9;font-weight:800;margin:18px 0 8px;}
.astra-note {border-left:3px solid #4ad7ee;background:#101d33;padding:14px 18px;border-radius:0 12px 12px 0;color:#c4d7f1;margin:12px 0;}
.assistant-heading {background:linear-gradient(125deg,#172a49,#101a31);border:1px solid #315172;border-radius:18px;padding:19px 17px;margin-bottom:12px;}
.assistant-heading h3 {margin:0;color:#e8f7ff;font-size:1.45rem;}
.assistant-heading p {color:#a8c1e1;font-size:.84rem;margin:8px 0 0;}
.assistant-tip {background:#12213b;border:1px solid #263c60;border-radius:12px;padding:12px;color:#bcd3f2;font-size:.85rem;margin:12px 0;}
</style>
""", unsafe_allow_html=True)

COLORS = {"Ideal":"#64e4d2", "Perturbada":"#ff6b83", "Mínimos cuadrados":"#ffbf69", "IA":"#8f8cff"}
PLOT_BG = "#0e192c"

def style_plot(fig, height=460):
    fig.update_layout(
        template="plotly_dark", height=height,
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(color="#bdcce5", family="DM Sans"),
        margin=dict(l=35,r=25,t=32,b=35),
        legend=dict(orientation="h", y=1.12, x=0, bgcolor="rgba(0,0,0,0)"),
        hovermode="closest"
    )
    fig.update_xaxes(gridcolor="#253750", zerolinecolor="#40536c")
    fig.update_yaxes(gridcolor="#253750", zerolinecolor="#40536c")
    return fig

with st.sidebar:
    st.markdown("### ◈ ASTRA CONTROL")
    st.caption("CONFIGURACIÓN DE MISIÓN")
    with st.expander("01 · Escenario", expanded=True):
        duration = st.slider("Duración (s)", 2.0, 10.0, 5.0, 0.5)
        wind = st.slider("Fuerza horizontal (N)", 0.0, 500.0, 200.0, 10.0)
        dt = st.select_slider("Intervalo temporal (s)", options=[0.05,0.1,0.2], value=0.1)
        segment_size = st.slider("Pasos por segmento", 5, 20, 10)
    with st.expander("02 · Parámetros del modelo", expanded=False):
        dry_mass = st.number_input("Masa seca (kg)", value=1000.0, min_value=1.0)
        fuel_mass = st.number_input("Combustible inicial (kg)", value=500.0, min_value=1.0)
        thrust = st.number_input("Empuje (N)", value=20000.0, min_value=1.0)
        area = st.number_input("Área de referencia (m²)", value=1.0, min_value=0.01)
        cd = st.number_input("Coeficiente de arrastre", value=0.5, min_value=0.0)
        isp = st.number_input("Impulso específico (s)", value=250.0, min_value=1.0)
    st.caption("Los parámetros afectan únicamente a la simulación educativa.")
    st.divider()
    with st.expander("◈ ASTRA Assistant", expanded=True):
        st.markdown('''<div class="assistant-heading"><div class="astra-kicker">COPILOTO DE ANÁLISIS</div><h3>◈ ASTRA Assistant</h3><p>Consulta los datos del vuelo sin salir del panel de misión.</p></div>''', unsafe_allow_html=True)
        st.markdown("**Preguntas disponibles**")
        st.caption("Posición, velocidad, combustible, masa, duración, ángulo, fuerza externa, desviación, empuje, resistencia al aire y gravedad.")
        st.caption("Selecciona una sugerencia o escribe una pregunta usando esas palabras.")

        if "results" in st.session_state:
            r_assistant = st.session_state["results"]
            scenario_assistant = st.selectbox(
                "Escenario de consulta", ["Ideal", "Perturbada"],
                key="astra_assistant_scenario"
            )
            data_assistant = r_assistant["ideal"] if scenario_assistant == "Ideal" else r_assistant["perturbed"]
            suggested_questions = [
                "Selecciona una pregunta...",
                "¿Cuál es la posición final?",
                "¿Cuál es la velocidad final?",
                "¿Cuánto combustible queda?",
                "¿Cuál es la masa final?",
                "¿Cuánto duró la simulación?",
                "¿Cuál es el ángulo final?",
                "¿Cuál fue la fuerza externa?",
                "¿Por qué hay desviación?",
                "¿Cuál es el empuje?",
                "¿Cuál es la resistencia al aire?",
                "¿Cuál es la fuerza de gravedad?",
            ]
            suggestion = st.selectbox("Preguntas sugeridas", suggested_questions, key="astra_assistant_suggestion")
            custom_question = st.text_input(
                "O escribe tu pregunta", placeholder="Ej.: ¿Cuál es la velocidad final?",
                key="astra_assistant_custom"
            )
            if st.button("Consultar ASTRA Assistant", type="primary", width="stretch", key="astra_assistant_send"):
                question = custom_question.strip() or (suggestion if suggestion != suggested_questions[0] else "")
                if not question:
                    st.warning("Escribe una pregunta o elige una sugerencia.")
                else:
                    summary = summarize_flight(data_assistant, label=scenario_assistant)
                    try:
                        response = answer_question(question, summary)
                    except (KeyError, TypeError, ValueError, IndexError):
                        response = "No hay datos suficientes para responder esa pregunta en este escenario."
                    st.session_state["astra_assistant_last_answer"] = (scenario_assistant, question, response)
            if "astra_assistant_last_answer" in st.session_state:
                scen, question, response = st.session_state["astra_assistant_last_answer"]
                st.markdown("**Última consulta**")
                st.caption(f"{scen} · {question}")
                st.info(response)
            st.markdown('''<div class="assistant-tip">Consejo: las respuestas usan datos del escenario seleccionado. El asistente actual es de preguntas guiadas; no controla el simulador.</div>''', unsafe_allow_html=True)
        else:
            st.info("Ejecuta una simulación para activar las consultas.")




st.markdown("""<div class="astra-hero"><div class="astra-kicker">ASTRA / MISSION CONTROL</div>
<h1>Flight Intelligence <span style="color:#67dff1">Dashboard</span></h1>
<p>Laboratorio virtual de vuelo 2D · Comparación de controladores · Análisis de trayectorias y telemetría</p>
<span class="astra-pill">● SISTEMA DE SIMULACIÓN LISTO</span> </div>""", unsafe_allow_html=True)

st.markdown('<div class="astra-section">CENTRO DE OPERACIONES</div>', unsafe_allow_html=True)
run_clicked = st.button("▶  INICIAR SIMULACIÓN", type="primary", width="stretch")
if run_clicked:
    try:
        rocket = Rocket(dry_mass=dry_mass, initial_fuel_mass=fuel_mass,
                        thrust=thrust, specific_impulse=isp, cd=cd, area=area)
        with st.spinner("Procesando los cuatro escenarios..."):
            ideal = run_simulation(rocket, 0.0, simulation_time=duration, dt=dt)
            perturbed = run_simulation(rocket, wind, simulation_time=duration, dt=dt)
            ls_controller = LeastSquaresController()
            ls = run_ls_simulation(rocket, wind, ideal, ls_controller,
                                   simulation_time=duration, dt=dt, segment_size=segment_size)
            ai_controller = RocketAIController()
            ai = run_ai_simulation(rocket, wind, ideal, ai_controller, duration, dt, segment_size)
            metrics = {
                "Perturbada": trajectory_metrics(ideal, perturbed),
                "Mínimos cuadrados": trajectory_metrics(ideal, ls),
                "IA": trajectory_metrics(ideal, ai)
            }
            st.session_state["results"] = dict(ideal=ideal, perturbed=perturbed,
                                                ls=ls, ai=ai, metrics=metrics)
        st.success("Simulación completada. Resultados actualizados.")
        st.rerun()
    except Exception as error:
        st.error(f"No se pudo ejecutar la simulación: {error}")

if "results" not in st.session_state:
    st.markdown("""<div class="astra-note">Configura los parámetros en el panel izquierdo y pulsa
    <b>INICIAR SIMULACIÓN</b> para activar el panel de resultados. </div>""", unsafe_allow_html=True)
else:
    r = st.session_state["results"]
    ideal, perturbed, ls, ai, metrics = r["ideal"],r["perturbed"],r["ls"],r["ai"],r["metrics"]
    st.markdown('<div class="astra-section">INDICADORES DE PRECISIÓN · RMSE</div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    a.metric("Trayectoria perturbada",f"{metrics['Perturbada']['rmse']:.4f} m")
    b.metric("Mínimos cuadrados",f"{metrics['Mínimos cuadrados']['rmse']:.4f} m")
    c.metric("Inteligencia artificial",f"{metrics['IA']['rmse']:.4f} m")
    base = metrics["Perturbada"]["rmse"]
    reduction = 100*(1-metrics["Mínimos cuadrados"]["rmse"]/base) if base>0 else 0.0
    d.metric("Mejora LS vs. perturbada",f"{reduction:.1f}%" if base>0 else "N/D")

    st.markdown('<div class="astra-section">VISUALIZACIÓN Y ANÁLISIS</div>', unsafe_allow_html=True)
    left_chart, right_chart = st.columns([1.75, 1], gap="medium")
    with left_chart:
        st.subheader("Visualización del vuelo")
        tab_trayectorias, tab_animacion = st.tabs(["📈 Trayectorias", "▶ Vuelo animado"])
        with tab_trayectorias:
            visible = st.multiselect("Escenarios visibles", ["Ideal", "Perturbada", "Mínimos cuadrados", "IA"],
                                     default=["Ideal", "Perturbada", "Mínimos cuadrados", "IA"],
                                     key="dashboard_visible")
            fig = go.Figure()
            for name, data in [("Ideal", ideal), ("Perturbada", perturbed),
                               ("Mínimos cuadrados", ls), ("IA", ai)]:
                if name in visible:
                    fig.add_trace(go.Scatter(
                        x=data["x"], y=data["y"], mode="lines", name=name,
                        line=dict(color=COLORS[name], width=3,
                                  dash="dash" if name == "Ideal" else "solid")
                    ))
            fig.update_layout(xaxis_title="Posición horizontal (m)", yaxis_title="Altura (m)")
            # Evitar que la gráfica se mueva o desaparezca
            fig.update_layout(
                dragmode=False,
                xaxis=dict(fixedrange=True, autorange=True),
                yaxis=dict(fixedrange=True, autorange=True)
            )   
            st.plotly_chart(
                style_plot(fig, 465),
                width="stretch",
                key="astra_dashboard_trajectory"
            )

        with tab_animacion:
            st.caption("Animación de datos simulados previamente; no es telemetría en tiempo real.")
            animation_scenarios = [
                ("Ideal", ideal),
                ("Perturbada", perturbed),
                ("Mínimos cuadrados", ls),
                ("IA", ai),
            ]
            # Se reproducen muestras calculadas previamente: no se alteran las ecuaciones.
            count = min(len(data["x"]) for _, data in animation_scenarios)
            if count < 2:
                st.info("La simulación necesita al menos dos puntos para animarse.")
            else:
                # Para mantener fluidez, limitamos el número de fotogramas visuales.
                indices = list(range(0, count, max(1, math.ceil(count / 90))))
                if indices[-1] != count - 1:
                    indices.append(count - 1)
                animated_fig = go.Figure()
                all_x = [v for _, d in animation_scenarios for v in d["x"][:count]]
                all_y = [v for _, d in animation_scenarios for v in d["y"][:count]]
                xmin, xmax = min(all_x), max(all_x)
                ymin, ymax = min(all_y), max(all_y)
                xpad = max((xmax - xmin) * .1, .15)
                ypad = max((ymax - ymin) * .08, 1.0)
                for name, data in animation_scenarios:
                    animated_fig.add_trace(go.Scatter(
                        x=data["x"][:1], y=data["y"][:1], mode="lines",
                        name=name, legendgroup=name,
                        line=dict(color=COLORS[name], width=3,
                                  dash="dash" if name == "Ideal" else "solid")
                    ))
                    animated_fig.add_trace(go.Scatter(
                        x=[data["x"][0]], y=[data["y"][0]], mode="markers",
                        name=f"{name} · posición", legendgroup=name, showlegend=False,
                        marker=dict(color=COLORS[name], size=12,
                                    line=dict(color="#e8f5ff", width=1.5))
                    ))
                frames = []
                slider_steps = []
                for i in indices:
                    frame_traces = []
                    for name, data in animation_scenarios:
                        frame_traces.append(go.Scatter(x=data["x"][:i+1], y=data["y"][:i+1]))
                        frame_traces.append(go.Scatter(x=[data["x"][i]], y=[data["y"][i]]))
                    timestamp = float(ideal["time"][i])
                    frame_name = str(i)
                    frames.append(go.Frame(name=frame_name, data=frame_traces,
                                           traces=list(range(len(frame_traces)))))
                    slider_steps.append(dict(
                        label=f"{timestamp:.1f}", method="animate",
                        args=[[frame_name], {"mode":"immediate", "frame":{"duration":0, "redraw":True},
                                              "transition":{"duration":0}}]
                    ))
                animated_fig.frames = frames
                animated_fig.update_layout(
                    xaxis=dict(title="Posición horizontal (m)", range=[xmin-xpad, xmax+xpad], autorange=False, fixedrange=True),
                    yaxis=dict(title="Altura (m)", range=[ymin-ypad, ymax+ypad], autorange=False, fixedrange=True),
                    updatemenus=[dict(type="buttons", direction="left", showactive=False,
                        x=0, y=-.19, xanchor="left", yanchor="top",
                        buttons=[
                            dict(label="▶ Reproducir", method="animate",
                                 args=[None, {"frame":{"duration":90, "redraw":True},
                                              "transition":{"duration":0}, "fromcurrent":True,
                                              "mode":"immediate"}]),
                            dict(label="⏸ Pausar", method="animate",
                                 args=[[None], {"frame":{"duration":0, "redraw":False},
                                                 "transition":{"duration":0}, "mode":"immediate"}])
                        ])],
                    sliders=[dict(active=0, x=.02, y=-.09, len=.96,
                                  currentvalue=dict(prefix="Tiempo simulado (s): ",
                                                    font=dict(color="#72e6f4")),
                                  steps=slider_steps, pad=dict(t=35, b=10))],
                    margin=dict(l=35, r=25, t=50, b=135)
                )
                animated_fig = style_plot(animated_fig, 570)
                animated_fig.update_layout(margin=dict(l=35,r=25,t=50,b=135))
                st.plotly_chart(animated_fig, width="stretch", key="astra_flight_animation")
                st.caption("La reproducción muestra datos ya calculados; no representa un vuelo en tiempo real.")
    with right_chart:
        st.subheader("Precisión de control")
        names = ["Perturbada", "Mínimos cuadrados", "IA"]
        bars = go.Figure(go.Bar(
            x=names, y=[metrics[n]["rmse"] for n in names],
            marker_color=[COLORS[n] for n in names],
            text=[f"{metrics[n]['rmse']:.4f}" for n in names], textposition="outside"
        ))
        bars.update_layout(yaxis_title="RMSE (m)", showlegend=False)
        st.plotly_chart(style_plot(bars, 330), width="stretch", key="astra_dashboard_rmse")
        winner = min(metrics, key=lambda n: metrics[n]["rmse"])
        st.info(f"Menor RMSE en esta ejecución: **{winner}**. El resultado puede variar con otros parámetros.")

    st.markdown('<div class="astra-section">MONITOREO DE LA MISIÓN · TELEMETRÍA</div>', unsafe_allow_html=True)
    st.subheader("Estado del vuelo")
    scenarios = {"Ideal": ideal, "Perturbada": perturbed, "Mínimos cuadrados": ls, "IA": ai}
    selected = st.selectbox("Escenario de telemetría", list(scenarios), key="dashboard_telemetry_scenario")
    data = scenarios[selected]

    # Las series históricas registran el estado al inicio de cada paso.
    # Para mostrar el estado final se prioriza el objeto 'state' cuando existe.
    final_state = data.get("state")
    def final_value(key):
        value = getattr(final_state, key, None) if final_state is not None else None
        if value is None:
            series = data.get(key, [])
            value = series[-1] if len(series) else None
        return value

    altitude = final_value("y")
    vx_final = final_value("vx")
    vy_final = final_value("vy")
    mass_final = final_value("mass")
    time_final = final_value("time")
    speed_final = math.hypot(vx_final, vy_final) if vx_final is not None and vy_final is not None else None

    def metric_text(value, unit, digits=2):
        return f"{value:,.{digits}f} {unit}" if value is not None else "N/D"

    m1, m2, m3, m4 = st.columns(4, gap="small")
    m1.metric("Altura final", metric_text(altitude, "m"))
    m2.metric("Rapidez final", metric_text(speed_final, "m/s"))
    m3.metric("Masa final", metric_text(mass_final, "kg"))
    m4.metric("Tiempo simulado", metric_text(time_final, "s"))
    st.caption("Indicadores calculados a partir del estado final disponible del escenario seleccionado.")

    tele_left, tele_right = st.columns(2, gap="medium")
    with tele_left:
        st.subheader("Altura en el tiempo")
        fig_alt = go.Figure()
        for name, scenario in scenarios.items():
            if len(scenario.get("time", [])) == len(scenario.get("y", [])):
                fig_alt.add_trace(go.Scatter(
                    x=scenario["time"], y=scenario["y"], name=name, mode="lines",
                    line=dict(color=COLORS[name], width=3,
                              dash="dash" if name == "Ideal" else "solid")
                ))
        fig_alt.update_layout(xaxis_title="Tiempo (s)", yaxis_title="Altura (m)", dragmode=False)
        fig_alt.update_xaxes(fixedrange=True)
        fig_alt.update_yaxes(fixedrange=True)
        st.plotly_chart(style_plot(fig_alt, 340), width="stretch", key="astra_height_history")

    with tele_right:
        st.subheader("Rapidez en el tiempo")
        fig_speed = go.Figure()
        for name, scenario in scenarios.items():
            if all(len(scenario.get(k, [])) == len(scenario.get("time", [])) for k in ("vx", "vy")):
                speeds = [math.hypot(vx, vy) for vx, vy in zip(scenario["vx"], scenario["vy"])]
                fig_speed.add_trace(go.Scatter(
                    x=scenario["time"], y=speeds, name=name, mode="lines",
                    line=dict(color=COLORS[name], width=3,
                              dash="dash" if name == "Ideal" else "solid")
                ))
        fig_speed.update_layout(xaxis_title="Tiempo (s)", yaxis_title="Rapidez (m/s)", dragmode=False)
        fig_speed.update_xaxes(fixedrange=True)
        fig_speed.update_yaxes(fixedrange=True)
        st.plotly_chart(style_plot(fig_speed, 340), width="stretch", key="astra_speed_history")

    st.markdown('<div class="astra-section">ANÁLISIS DETALLADO</div>', unsafe_allow_html=True)
    detail_left, detail_right = st.columns([1.2, 1], gap="medium")
    with detail_left:
        st.subheader("Explorador de telemetría")
        labels = {"x": "Posición X (m)", "y": "Altura Y (m)",
                  "vx": "Velocidad X (m/s)", "vy": "Velocidad Y (m/s)",
                  "mass": "Masa (kg)", "fuel_mass": "Combustible (kg)",
                  "angle": "Ángulo (rad)", "ax": "Aceleración X (m/s²)",
                  "ay": "Aceleración Y (m/s²)"}
        available = [key for key in labels if key in data and len(data[key]) == len(data["time"])]
        if available:
            variable = st.selectbox("Variable", available, format_func=lambda k: labels[k],
                                    key="dashboard_telemetry_variable")
            telemetry = go.Figure(go.Scatter(
                x=data["time"], y=data[variable], mode="lines",
                line=dict(color=COLORS[selected], width=3),
                fill="tozeroy", fillcolor="rgba(91,198,239,0.08)"
            ))
            telemetry.update_layout(xaxis_title="Tiempo (s)", yaxis_title=labels[variable], dragmode=False)
            telemetry.update_xaxes(fixedrange=True)
            telemetry.update_yaxes(fixedrange=True)
            st.plotly_chart(style_plot(telemetry, 340), width="stretch", key="astra_dashboard_telemetry")
        else:
            st.info("Este escenario no tiene series de telemetría disponibles.")
    with detail_right:
        st.subheader("Evaluación de controladores")
        table = pd.DataFrame({name: {"RMSE (m)": val["rmse"],
                                     "Error máximo (m)": val["max"],
                                     "Error final (m)": val["final"]}
                              for name, val in metrics.items()}).T
        st.dataframe(table.style.format("{:.4f}"), width="stretch")
        st.caption("Los errores se comparan con la trayectoria ideal.")
        st.metric("Reducción RMSE · LS", f"{reduction:.1f}%" if base > 0 else "N/D")

    st.markdown('<div class="astra-section">REGISTRO DE CONTROL</div>', unsafe_allow_html=True)
    st.subheader("Historial de correcciones")
    st.caption("Cambios angulares calculados por los controladores en cada actualización registrada.")

    def correction_dataframe(result, controller_name):
        raw = result.get("corrections", [])
        if not raw:
            return pd.DataFrame(columns=["Tiempo (s)", "Corrección (grados)", "Controlador"])
        df = pd.DataFrame(raw).copy()
        if "Tiempo (s)" not in df.columns:
            if "time" in df.columns:
                df["Tiempo (s)"] = df["time"]
            elif "time_s" in df.columns:
                df["Tiempo (s)"] = df["time_s"]
        if "Corrección (grados)" not in df.columns and "delta_theta" in df.columns:
            df["Corrección (grados)"] = pd.to_numeric(df["delta_theta"], errors="coerce").apply(
                lambda v: math.degrees(v) if pd.notna(v) else float("nan"))
        if "Ángulo (grados)" not in df.columns and "angle" in df.columns:
            df["Ángulo (grados)"] = pd.to_numeric(df["angle"], errors="coerce").apply(
                lambda v: math.degrees(v) if pd.notna(v) else float("nan"))
        df["Controlador"] = controller_name
        return df

    ls_corrections = correction_dataframe(ls, "Mínimos cuadrados")
    ai_corrections = correction_dataframe(ai, "IA")
    correction_data = pd.concat([ls_corrections, ai_corrections], ignore_index=True)
    valid_corrections = correction_data.dropna(subset=["Tiempo (s)", "Corrección (grados)"])

    if not valid_corrections.empty:
        correction_chart = go.Figure()
        for controller_name in ("Mínimos cuadrados", "IA"):
            subset = valid_corrections[valid_corrections["Controlador"] == controller_name]
            if not subset.empty:
                correction_chart.add_trace(go.Scatter(
                    x=subset["Tiempo (s)"], y=subset["Corrección (grados)"],
                    mode="lines+markers", name=controller_name,
                    line=dict(color=COLORS[controller_name], width=3), marker=dict(size=8)
                ))
        correction_chart.add_hline(y=0, line_dash="dot", line_color="#8295b6")
        correction_chart.update_layout(xaxis_title="Tiempo (s)",
                                       yaxis_title="Corrección angular (°)", dragmode=False)
        correction_chart.update_xaxes(fixedrange=True)
        correction_chart.update_yaxes(fixedrange=True)
        st.plotly_chart(style_plot(correction_chart, 355), width="stretch", key="astra_correction_history")
        with st.expander("Ver tabla detallada de correcciones", expanded=False):
            st.dataframe(correction_data, width="stretch")
    else:
        st.info("No se registraron correcciones para los parámetros de esta simulación.")

st.divider()
st.caption("ASTRA · Entorno de simulación y análisis académico")
