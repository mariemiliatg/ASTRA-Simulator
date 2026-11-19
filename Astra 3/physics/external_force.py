EXTERNAL_FORCE_X = 200.0
EXTERNAL_FORCE_Y = 0.0


def apply_external_force(state):

    state.external_force_x = EXTERNAL_FORCE_X
    state.external_force_y = EXTERNAL_FORCE_Y

    return state