import math


def calculate_position_error(
    ideal_x,
    ideal_y,
    real_x,
    real_y
):

    error_x = real_x - ideal_x
    error_y = real_y - ideal_y

    error_position = math.sqrt(
        error_x**2
        + error_y**2
    )

    return error_position