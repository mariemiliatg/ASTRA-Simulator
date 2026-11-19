def calculate_least_squares(
    segment
):

    x_values = segment["x"]
    y_values = segment["y"]

    n = len(x_values)

    sum_y = sum(y_values)

    sum_x = sum(x_values)

    sum_yx = sum(
        y * x
        for y, x in zip(
            y_values,
            x_values
        )
    )

    sum_y_squared = sum(
        y**2
        for y in y_values
    )

    denominator = (
        n * sum_y_squared
        - sum_y**2
    )

    if denominator == 0:

        slope = 0.0

    else:

        slope = (
            n * sum_yx
            - sum_y * sum_x
        ) / denominator

    intercept = (
        sum_x
        - slope * sum_y
    ) / n

    return slope, intercept