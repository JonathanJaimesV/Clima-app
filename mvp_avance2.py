# ==========================================================
# Archivo: mvp_avance2.py
# Proyecto: Atmosfera — Sistema de Clima con IA
# Autor: Jonathan
# Actividad 2: Menú personalizado con cálculos y validación
# ==========================================================

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ==========================================================
# ACTIVIDAD 2 — DATOS DEL SISTEMA
# Variables con valores de ejemplo para el clima
# ==========================================================

# Datos del clima actuales (valores de ejemplo)
clima_actual = {
    "ciudad":          "Cucuta",
    "pais":            "Colombia",
    "temperatura":     32,        # int   — °C
    "sensacion":       34.7,      # float — °C
    "humedad":         78,        # int   — %
    "viento":          14.4,      # float — km/h
    "visibilidad":     9.5,       # float — km
    "nubosidad":       20,        # int   — %
    "descripcion":     "Cielo despejado",
}


# ==========================================================
# ACTIVIDAD 2 — CÁLCULOS DEL SISTEMA
# Funciones con cálculos matemáticos reales del proyecto
# ==========================================================

def calcular_fahrenheit(celsius):
    """
    Convierte temperatura de Celsius a Fahrenheit.
    Converts temperature from Celsius to Fahrenheit.
    Fórmula / Formula: (°C × 9/5) + 32
    """
    return round((celsius * 9 / 5) + 32, 1)

def calcular_indice_calor(temperatura, humedad):
    """
    Calcula el índice de calor (sensación por temperatura + humedad).
    Calculates the heat index (sensation from temperature + humidity).
    Fórmula simplificada / Simplified formula.
    """
    return round(temperatura + (humedad * 0.1), 1)

def calcular_diferencia_sensacion(sensacion, temperatura):
    """
    Calcula cuánto más caliente o frío se siente respecto a la temperatura real.
    Calculates how much hotter or colder it feels vs real temperature.
    """
    return round(sensacion - temperatura, 1)

def calcular_promedio_temperaturas(temps):
    """
    Calcula el promedio de una lista de temperaturas.
    Calculates the average of a list of temperatures.
    Fórmula / Formula: suma / cantidad
    """
    if not temps:
        return 0
    return round(sum(temps) / len(temps), 1)

def calcular_probabilidad_lluvia(humedad, nubosidad):
    """
    Estima la probabilidad de lluvia basada en humedad y nubosidad.
    Estimates rain probability based on humidity and cloudiness.
    Fórmula propia / Custom formula: promedio ponderado
    """
    return round((humedad * 0.6) + (nubosidad * 0.4), 1)


# ==========================================================
# ACTIVIDAD 2 — RUTAS / ROUTES
# Cada opción del menú es una ruta Flask
# ==========================================================

@app.route("/")
def index():
    """Página principal con el menú del sistema."""
    return render_template("avance2.html", clima=clima_actual)


@app.route("/opcion/1")
def opcion_ver_clima():
    """Opción 1: Ver clima actual con todos sus datos."""
    c = clima_actual
    resultado = {
        "titulo": "Clima Actual",
        "datos": [
            {"label": "Ciudad",       "valor": f"{c['ciudad']}, {c['pais']}"},
            {"label": "Temperatura",  "valor": f"{c['temperatura']}°C"},
            {"label": "Sensación",    "valor": f"{c['sensacion']}°C"},
            {"label": "Humedad",      "valor": f"{c['humedad']}%"},
            {"label": "Viento",       "valor": f"{c['viento']} km/h"},
            {"label": "Visibilidad",  "valor": f"{c['visibilidad']} km"},
            {"label": "Nubosidad",    "valor": f"{c['nubosidad']}%"},
            {"label": "Descripción",  "valor": c['descripcion']},
        ]
    }
    return jsonify(resultado)


@app.route("/opcion/2")
def opcion_conversion():
    """Opción 2: Convertir temperatura °C → °F."""
    c = clima_actual
    fahrenheit = calcular_fahrenheit(c['temperatura'])
    resultado = {
        "titulo": "Conversión de Temperatura",
        "datos": [
            {"label": "Temperatura °C",  "valor": f"{c['temperatura']}°C"},
            {"label": "Fórmula",         "valor": f"({c['temperatura']} × 9/5) + 32"},
            {"label": "Resultado °F",    "valor": f"{fahrenheit}°F"},
        ]
    }
    return jsonify(resultado)


@app.route("/opcion/3")
def opcion_indice_calor():
    """Opción 3: Calcular índice de calor."""
    c = clima_actual
    indice   = calcular_indice_calor(c['temperatura'], c['humedad'])
    dif      = calcular_diferencia_sensacion(c['sensacion'], c['temperatura'])
    resultado = {
        "titulo": "Índice de Calor",
        "datos": [
            {"label": "Temperatura real",   "valor": f"{c['temperatura']}°C"},
            {"label": "Humedad",            "valor": f"{c['humedad']}%"},
            {"label": "Fórmula índice",     "valor": f"{c['temperatura']} + ({c['humedad']} × 0.1)"},
            {"label": "Índice de calor",    "valor": f"{indice}"},
            {"label": "Diferencia sensación","valor": f"+{dif}°C sobre temperatura real"},
        ]
    }
    return jsonify(resultado)


@app.route("/opcion/4")
def opcion_probabilidad_lluvia():
    """Opción 4: Calcular probabilidad de lluvia."""
    c = clima_actual
    prob = calcular_probabilidad_lluvia(c['humedad'], c['nubosidad'])
    nivel = "Alta" if prob >= 70 else ("Media" if prob >= 40 else "Baja")
    resultado = {
        "titulo": "Probabilidad de Lluvia",
        "datos": [
            {"label": "Humedad",          "valor": f"{c['humedad']}%"},
            {"label": "Nubosidad",        "valor": f"{c['nubosidad']}%"},
            {"label": "Fórmula",          "valor": f"({c['humedad']} × 0.6) + ({c['nubosidad']} × 0.4)"},
            {"label": "Probabilidad",     "valor": f"{prob}%"},
            {"label": "Nivel de riesgo",  "valor": nivel},
        ]
    }
    return jsonify(resultado)


@app.route("/opcion/5")
def opcion_promedio():
    """Opción 5: Calcular promedio de temperaturas del día."""
    # Temperaturas simuladas cada 4 horas / Simulated temperatures every 4 hours
    temperaturas = [26, 28, 31, 32, 30, 27]
    horas        = ["6am", "9am", "12pm", "3pm", "6pm", "9pm"]
    promedio     = calcular_promedio_temperaturas(temperaturas)
    maxima       = max(temperaturas)
    minima       = min(temperaturas)

    resultado = {
        "titulo": "Promedio de Temperaturas del Día",
        "datos": [
            {"label": hora, "valor": f"{temp}°C"}
            for hora, temp in zip(horas, temperaturas)
        ] + [
            {"label": "─────────────", "valor": "─────"},
            {"label": "Fórmula",   "valor": f"suma({sum(temperaturas)}) / {len(temperaturas)}"},
            {"label": "Promedio",  "valor": f"{promedio}°C"},
            {"label": "Máxima",    "valor": f"{maxima}°C"},
            {"label": "Mínima",    "valor": f"{minima}°C"},
        ]
    }
    return jsonify(resultado)


# ==========================================================
# PUNTO DE ENTRADA / ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
