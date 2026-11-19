import math


RHO = 1.225


def calculate_drag(state, rocket):

    speed = math.sqrt(
        state.vx**2
        + state.vy**2
    )

    state.drag_force_x = (
        -0.5
        * RHO
        * rocket.cd
        * rocket.area
        * speed
        * state.vx
    )

    state.drag_force_y = (
        -0.5
        * RHO
        * rocket.cd
        * rocket.area
        * speed
        * state.vy
    )

    return state