G = 9.8


def calculate_gravity(state):

    state.gravity_force_x = 0.0
    state.gravity_force_y = -state.mass * G

    return state