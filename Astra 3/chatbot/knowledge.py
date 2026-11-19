

def get_last_value(results, key):
   
    state = results.get("state")

    if state is not None:
        value = getattr(state, key, None)

        if value is not None:
            return value

    history = results.get(key)

    if history is not None and len(history) > 0:
        return history[-1]

    return None


def summarize_flight(results, label="Flight"):

    summary = {
        "label": label,

        "duration": get_last_value(results, "time"),

        "position": {
            "x": get_last_value(results, "x"),
            "y": get_last_value(results, "y")
        },

        "velocity": {
            "vx": get_last_value(results, "vx"),
            "vy": get_last_value(results, "vy")
        },

        "mass": get_last_value(results, "mass"),

        "fuel_mass": get_last_value(results, "fuel_mass"),

        "angle": get_last_value(results, "angle"),

        "external_force": {
            "x": get_last_value(results, "external_force_x"),
            "y": get_last_value(results, "external_force_y")
        },

        "thrust_force": {
            "x": get_last_value(results, "thrust_force_x"),
            "y": get_last_value(results, "thrust_force_y")
        },

        "drag_force": {
            "x": get_last_value(results, "drag_force_x"),
            "y": get_last_value(results, "drag_force_y")
        },

        "gravity_force": {
            "x": get_last_value(results, "gravity_force_x"),
            "y": get_last_value(results, "gravity_force_y")
        },

        "corrections": results.get("corrections", [])
    }

    return summary
