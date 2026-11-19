---
date: 18 November 2026
subtitle: Technical briefing for the next project contributor and AI
  assistant
title: ASTRA Project Handoff
---

# ASTRA PROJECT HANDOFF

**Purpose:** Give a new team member or AI assistant enough reliable
context to understand the ASTRA project, its current Python
architecture, the chatbot work already completed, and the next
integration tasks.

## 1. How to use this document

Read this document before proposing code changes. Treat the checked-out
project files as the final authority for current implementation details.
The proposal and progress reports describe the intended design and
historical results; they do not always match the latest code version.

When assisting with ASTRA: - Explain the reasoning behind code changes.
The student is learning Python and wants to understand, not just copy
code. - Make small, testable changes and preserve the existing modular
architecture. - Do not claim a feature is implemented unless it exists
in the current source tree and has been tested. - If source documents
and code disagree, point out the discrepancy instead of silently
choosing one. - Ask for the current file or relevant code before
changing a module that has not been inspected.

## 2. Project overview

ASTRA is a two-dimensional Python rocket-flight simulator. Its main
purpose is to study how a constant external lateral force (used to
represent wind) deviates a rocket from an ideal trajectory, and to
evaluate trajectory-correction methods.

The proposed model represents a single-stage rocket operating within
Earth's atmosphere. The state includes horizontal and vertical position,
velocity and acceleration, total mass, remaining fuel, and rocket angle.
The angle is measured relative to the vertical.

The project models four principal force contributions: 1. Engine thrust.
2. Gravity. 3. Aerodynamic drag. 4. A constant external lateral force.

The controller does not directly move the rocket's position or edit its
plotted trajectory. It changes the rocket's angle. The physics engine
then recalculates thrust components and the resulting motion.

## 3. Physics model

### 3.1 Thrust and angle

For thrust magnitude `T` and rocket angle `theta` measured from the
vertical, the project uses:

-   `Tx = T * sin(theta)`
-   `Ty = T * cos(theta)`

The controller's correction is applied to `state.angle`; the force
components are then recalculated by the physics engine.

### 3.2 Gravity

The project rule is **g = 9.8 m/s²**. Do not change it to 9.81 m/s².
Gravity acts vertically downward, with `Fg_y = -m*g`; the horizontal
gravity component is zero.

### 3.3 Aerodynamic drag

Drag uses the classical aerodynamic model based on air density, drag
coefficient, reference area, and speed. The proposal and progress report
specify a constant reference area for this simplified model. Drag acts
opposite the velocity vector.

### 3.4 External force

The main test case applies a constant horizontal external force. In the
current `main.py`, the standard test value is `external_force_x = 200.0`
N. The simulator function also accepts `external_force_y`, whose default
is zero, but the documented project perturbation is lateral/horizontal.

### 3.5 Variable mass and numerical integration

The rocket's total mass decreases as fuel is consumed. The proposal
describes mass flow as `mdot = T / (Isp * g0)` while the engine is
operating.

The progress report describes semi-implicit Euler integration: 1.
Calculate forces and acceleration. 2. Update velocity using the current
acceleration. 3. Update position using the updated velocity. 4. Update
fuel and total mass. 5. Advance simulation time.

## 4. Existing project modules

The corrected Module 3 project archive contains the following structure
(some folders contain additional files):

``` text
Astra/
├── ai/
│   ├── dataset.py
│   ├── labeling.py
│   ├── model.py
│   ├── training.py
│   ├── prediction.py
│   ├── escalador.joblib
│   └── modelo_cohete.joblib
├── control/
│   └── ls_controller.py
├── physics/
│   ├── rocket.py
│   ├── gravity.py
│   ├── propulsion.py
│   ├── aerodynamics.py
│   ├── external_force.py
│   ├── dynamics.py
│   └── motion.py
├── simulation/
│   ├── state.py
│   ├── simulator.py
│   └── controlled_simulator.py
├── trajectory/
│   ├── least_squares.py
│   ├── segmentation.py
│   └── trajectory_error.py
├── validation/
│   ├── physics_tests.py
│   ├── metrics.py
│   └── ls_sweep.py
├── visualization/
│   └── plots.py
├── dataset_astra.csv
├── dataset_entrenamiento.csv
├── generate_dataset.py
├── main.py
├── main_modulo1.py
└── README_MODULO3.md
```

### Module 1: Physics engine and simulation

Main responsibilities: - Define the rocket parameters
(`physics/rocket.py`). - Store the rocket's state
(`simulation/state.py`). - Calculate gravity, thrust, drag, net
acceleration, velocity, position, and fuel consumption (`physics/`). -
Run an uncorrected simulation (`simulation/simulator.py`). - Record
telemetry histories, including position, velocity, acceleration, mass,
fuel, angle, and force components.

`run_simulation(...)` returns a dictionary of histories plus the final
`RocketState` object under the key `"state"`.

### Module 2: Neural-network controller

The neural-network controller is implemented in `ai/prediction.py` as
`RocketAIController`.

The Phase 2 continuity document describes: - `MLPRegressor` from
scikit-learn. - ReLU activation and Adam solver. - StandardScaler
preprocessing. - Six inputs: position error `e`, slope error `delta_a`,
`vx`, `vy`, current mass, and current angle. - One output: angular
correction `delta_theta` in radians. - A maximum correction magnitude of
±5 degrees per segment.

The controller loads the saved model and scaler from: -
`ai/modelo_cohete.joblib` - `ai/escalador.joblib`

The prediction code calculates the position error and slope difference,
scales the six inputs, predicts `delta_theta`, clamps it to ±5 degrees,
and returns the correction plus an information dictionary.

### Module 3: Least-squares trajectory controller

`control/ls_controller.py` implements `LeastSquaresController`.

At the end of each segment, it: 1. Fits a line `x = a*y + b` to the
ideal and real trajectory segments. 2. Calculates the difference between
ideal and real slopes. 3. Calculates signed horizontal position error
`ex` and total position error `e`. 4. Computes an angular correction. 5.
Limits the correction to ±5 degrees.

The corrected archive documents default gains: - `k_slope = 0.35` -
`k_pos = 0.10` - `lookahead = 6.0 s` - maximum correction = ±5 degrees

The current controller source is the authority for the exact implemented
formula and safeguards.

### Main program and comparison

`main.py` coordinates the four scenarios: - Ideal flight: no external
force. - Perturbed flight: external force, no controller. -
Least-squares-controlled flight. - AI-controlled flight.

It calculates trajectory RMSE and final position error relative to the
ideal trajectory, prints results, and plots the trajectory comparison
using Matplotlib.

`main_modulo1.py` preserves the earlier physics-only entry point.

## 5. Simulation data and interfaces

### Uncontrolled simulator output

`simulation/simulator.py` returns a dictionary containing: - `"state"`:
final `RocketState`. - Histories: `"time"`, `"x"`, `"y"`, `"vx"`,
`"vy"`, `"ax"`, `"ay"`, `"mass"`, `"fuel_mass"`, `"angle"`. - Force
histories: `"gravity_force_x/y"`, `"thrust_force_x/y"`,
`"drag_force_x/y"`, `"external_force_x/y"`.

### Controlled simulator output

`simulation/controlled_simulator.py` returns: - Histories: `"time"`,
`"x"`, `"y"`, `"vx"`, `"vy"`, `"mass"`, `"angle"`. - `"state"`: final
`RocketState`. - `"corrections"`: list of controller correction records.

Each correction record is enriched with `"step"`, `"time"`, and
`"angle"`. The information originally returned by each controller
differs: - Least-squares records include slope and position-error
information as well as `delta_theta`. - Neural-network records include
`e`, `delta_a`, and `delta_theta`.

The controlled simulator does not create the same full force-history
dictionary as the uncontrolled simulator. Code consuming results must
handle missing history keys and may inspect the final `"state"` object
where appropriate.

## 6. Reported validation results

The progress report records these results for a 200 N lateral-force
case: - No correction: RMSE = 0.749 m. - First neural-network version:
RMSE = 2.88 m (worse due to oscillations). - Retrained neural-network
version: RMSE = 0.325 m, reported as a 56.6% reduction relative to the
uncorrected case. - Least-squares controller: RMSE = 0.133 m, reported
as an 82.2% reduction relative to the uncorrected case.

The same report states that, across 20 wind cases, the least-squares
average RMSE decreased from 0.936 m to 0.167 m.

These are **reported results from the progress document**, not
guaranteed outputs for every code version or parameter set. Re-run the
current project before quoting them as fresh experimental results.

## 7. Chatbot module: current work and intended role

### Required role

The project continuity document specifies that the conversational
assistant must be a module separate from `ai/prediction.py`. Its job is
to read simulation results and explain them to the user. It must not
control the rocket, calculate or apply trajectory corrections, or modify
the physics engine.

### Current prototype created in the working project

A new `chatbot/` folder has been created with: - `chatbot/__init__.py` -
`chatbot/knowledge.py` - `chatbot/assistant.py`

The prototype is a **rule-based Python chatbot**. It does not use a
language model, external API, or internet connection.

`knowledge.py` currently provides: - `get_last_value(results, key)`:
retrieves a final value from the final state object when available,
otherwise from a history list. -
`summarize_flight(results, label="Flight")`: creates a compact summary
of duration, position, velocity, mass, fuel mass, angle, corrections,
and force components.

`assistant.py` currently provides: -
`answer_question(question, summary)`: uses keyword/substring matching to
select an answer. - Supported topic families include position, velocity,
fuel, mass, time/duration, angle/orientation, wind/external force,
deviation, thrust, drag, and gravity. - Answers combine values from the
simulation summary with fixed explanatory text.

A local test script named `test_knowledge.py` was created to run a
sample 5-second simulation with a 200 N horizontal force, summarize its
output, and open a terminal question/answer loop. This is a development
test, not the final application interface.

### Current limitations

-   Keyword matching is basic; phrasing and synonyms are limited.
-   It currently summarizes one simulation result at a time.
-   It does not yet compare the ideal, perturbed, least-squares, and
    AI-controlled runs in a single answer.
-   It does not yet explain correction history in depth.
-   It is not yet integrated into the graphical interface or the main
    application flow.
-   The test script is not the final GUI.

### Recommended next chatbot tasks

1.  Keep the chatbot isolated from the control code.
2.  Define a stable function interface for the GUI, such as
    `answer_question(question, summary) -> str`.
3.  Pass simulation summaries from the main application or GUI to the
    chatbot; do not make the chatbot rerun or alter the simulation.
4.  Expand the knowledge layer to build summaries for all four
    scenarios.
5.  Add comparison metrics (RMSE, maximum error, final error) from
    `validation/metrics.py` or the calculations already in `main.py`.
6.  Add correction-history explanations using each controlled run's
    `"corrections"` list.
7.  Add tests for known questions, missing data, unknown questions, and
    controlled versus uncontrolled result dictionaries.

## 8. Visual interface / final integration work

The Phase 2 continuity document identifies two next milestones: - A
visual interface, potentially animated in 2D, showing ideal and real
trajectories, live telemetry, and parameter controls. - A separate
conversational assistant that explains simulation results.

The current project archive contains static Matplotlib visualization
code. The documentation does not establish that the proposed animated
interface is already implemented.

For integration, the interface should: 1. Run or receive the simulation
results. 2. Build/pass the relevant summaries to the chatbot. 3. Send
the user's text question to the chatbot function. 4. Display the
returned text answer.

Agree on the interface contract with the person developing the GUI
before changing either module. The chatbot should remain usable
independently of the GUI.

## 9. Non-negotiable project constraints

1.  **Gravity:** use `g = 9.8 m/s²`, not 9.81.
2.  **Physics integrity:** do not change the base acceleration or motion
    equations in `physics/dynamics.py` or `physics/motion.py` as part of
    chatbot or interface work.
3.  **Controller action:** controller corrections are applied to
    `state.angle` only; the physics engine determines the resulting
    movement.
4.  **Module separation:** chatbot code must remain separate from
    `ai/prediction.py`.
5.  **Chatbot responsibility:** read and explain results; never control
    the rocket.
6.  **Data honesty:** if a requested value is missing, say it is
    unavailable. Do not invent telemetry or claim a controller succeeded
    without checking metrics.

## 10. Version discrepancies to keep visible

The supplied documents and code archives contain a few version
differences: - The first progress report mentions `g = 9.81 m/s²` in an
early description, but later project instructions, the corrected physics
source, and the continuity document specify `g = 9.8 m/s²`. Follow
`9.8`. - The Phase 2 continuity document describes hidden-layer sizes
`(32, 16)`, while `ai/model.py` in the corrected Module 3 archive
creates an MLPRegressor with `(64, 32)`. Inspect the current checked-out
`ai/model.py` and saved model before stating which model is active. -
The progress report contains historical neural-network versions and
results. Do not mix the first model's RMSE with the retrained model's
RMSE. - The proposal describes the intended assistant as a possible
local AI assistant, while the current implementation is a simpler
rule-based chatbot. This is acceptable unless the group later specifies
an actual language-model requirement.

## 11. Useful commands

Run commands from the project root (the directory containing `main.py`):

``` bash
python main.py
python main_modulo1.py
python -m validation.physics_tests
python -m validation.ls_sweep
python test_knowledge.py
```

The last command is the local chatbot development test and may not exist
in another teammate's checkout unless the chatbot files have been
shared.

## 12. Source documents and code inspected

This handoff is based on the supplied project materials: -
`Propuesta proyecto fisica.docx` --- project objective, physical model,
trajectory correction concept, validation plan, and proposed local
assistant. - `Avance 1 proyecto ASTRA.pdf` --- physics implementation,
neural-network development, and reported validation results. -
`ASTRA_Continuidad_Fase2.docx` --- AI architecture, training
description, project constraints, and next milestones. -
`README_MODULO3.md` from the corrected Module 3 archive --- module
breakdown, least-squares controller, and run commands. - Current source
files inspected: `main.py`, `simulation/simulator.py`,
`simulation/controlled_simulator.py`, `simulation/state.py`,
`control/ls_controller.py`, `ai/prediction.py`, `ai/model.py`,
`physics/gravity.py`, and `validation/metrics.py`. - Chatbot prototype
files developed during the current work: `chatbot/knowledge.py`,
`chatbot/assistant.py`, and `test_knowledge.py`.

------------------------------------------------------------------------

## Message to the next AI assistant

You are joining an existing engineering project, not starting a new one.
First inspect the current repository and compare it with this handoff.
Preserve the established physics and module boundaries. The immediate
integration goal is to connect the existing chatbot prototype to the
final user interface so that it can explain actual ASTRA simulation
results. Before adding features, confirm what the group has assigned as
the final module and agree on the GUI/chatbot function interface with
the teammate responsible for the interface.
