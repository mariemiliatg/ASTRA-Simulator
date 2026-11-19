def divide_trajectory(
    results,
    segment_size
):

    segments = []

    x_values = results["x"]
    y_values = results["y"]

    total_points = len(x_values)

    for start in range(
        0,
        total_points,
        segment_size
    ):

        end = start + segment_size

        segment_x = x_values[
            start:end
        ]

        segment_y = y_values[
            start:end
        ]

        if len(segment_x) >= 2:

            segment = {
                "x": segment_x,
                "y": segment_y
            }

            segments.append(segment)

    return segments