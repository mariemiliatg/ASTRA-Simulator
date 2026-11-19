def update_velocity(state, dt):

    state.vx = (
        state.vx
        + state.ax * dt
    )

    state.vy = (
        state.vy
        + state.ay * dt
    )

    return state


def update_position(state, dt):

    state.x = (
        state.x
        + state.vx * dt
    )

    state.y = (
        state.y
        + state.vy * dt
    )

    return state