def calculate_acceleration(state):

    total_force_x = (
        state.thrust_force_x
        + state.gravity_force_x
        + state.drag_force_x
        + state.external_force_x
    )

    total_force_y = (
        state.thrust_force_y
        + state.gravity_force_y
        + state.drag_force_y
        + state.external_force_y
    )

    state.ax = total_force_x / state.mass
    state.ay = total_force_y / state.mass

    return state