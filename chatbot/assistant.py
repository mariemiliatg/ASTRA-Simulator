

import unicodedata
def answer_question(question, summary):

    question = unicodedata.normalize("NFD", question.lower())
    question = "".join(
        caracter for caracter in question
        if unicodedata.category(caracter) != "Mn"
    )

    if "posicion" in question or "donde" in question:
        x = summary["position"]["x"]
        y = summary["position"]["y"]

        return (
            f"El cohete termino su recorrido en X = {x:.2f} m "
            f"e Y = {y:.2f} m."
        )

    elif "velocidad" in question or "rapidez" in question:
        vx = summary["velocity"]["vx"]
        vy = summary["velocity"]["vy"]

        return (
            f"Velocidad horizontal: {vx:.2f} m/s. "
            f"Velocidad vertical: {vy:.2f} m/s."
        )

    elif "combustible" in question:
        fuel = summary["fuel_mass"]

        if fuel is None:
            return "Informacion de combustible no disponible"

        return f"Al cohete le quedan {fuel:.2f}kg de combustible."

    elif "masa" in question or "peso" in question:
        mass = summary["mass"]

        return f"La masa final del cohete fue de {mass:.2f} kg."

    elif "tiempo" in question or "duracion" in question or "duro" in question:
        duration = summary["duration"]

        return f"La simulacion duro {duration:.2f} segundos."

    elif "anuglo" in question or "orientacion" in question:
        angle = summary["angle"]

        return f"El angulo final del cohete fue de {angle:.2f} radianes."

    elif "viendo" in question or "fuerza externa" in question:
        force = summary["external_force"]["x"]

        if force is None:
            return "La informacion de fuerzas externas no esta disponible."

        return (
            f"La fuerza externa fue de {force:.2f} N. "
            "Esta fuerza actua horizontalmente y puede causar"
            "que el cohete se desvie de su trayectoria ideal."
        )

    elif "desvio" in question or "de lado" in question or "desviacion" in question:
        force = summary["external_force"]["x"]

        if force is None:
            return "La informacion disponible no es suficiente para explicar la desviacion "

        return (
            f"El cohete experimento una fuerza externa lateral "
            f" de {force:.2f} N. Esta fuerza contribuye a "
            "la aceleracion horizontal, y puede mover al cohete "
            "alejandolo de su trayectoria ideal."
        )

    elif "empuje" in question:
        force = summary["thrust_force"]

        if force["x"] is None or force["y"] is None:
            return "La informacion de la fuerza de empuje no esta disponible."

        return (
            f"Las componentes de la fuerza de empuje son "
            f"X = {force['x']:.2f} N y "
            f"Y = {force['y']:.2f} N. "
            "El empuje es la fuerza generada por el motor del cohete."
        )

    elif "resistencia al aire" in question or "resistencia de aire" in question or "resistencia aerodinamica" in question:
        force = summary["drag_force"]

        if force["x"] is None or force["y"] is None:
            return "La informacion de la resistencia de aire no esta disponible. Intente con otra pregunta"

        return (
            f"Las componentes de la resistencia aerodinamica son "
            f"X = {force['x']:.2f} N y "
            f"Y = {force['y']:.2f} N. "
            "La resistencia aerodinamica se opone al movimiento del cohete relativo al aire."
        )

    elif "gravedad" in question or "fuerza de gravedad" in question:
        force = summary["gravity_force"]

        if force["x"] is None or force["y"] is None:
            return "La informacion de la fuerza gravitacional no esta disponible."

        return (
            f"Las componentes de la fuerza gravitacional son "
            f"X = {force['x']:.2f} N y "
            f"Y = {force['y']:.2f} N. "
            "La gravedad actua verticalmente, oponiendose "
            "al ascenso vertical del cohete."
        )
    else:
        return (
            "Lo siento, no he entendido tu pregunta "
            "Puedes preguntar por posición, velocidad, combustible, masa, "
            "duración, ángulo, resistencia al aire, empuje, o gravedad."
        )
