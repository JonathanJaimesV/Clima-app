# ==========================================================
# Proyecto: Atmosfera — Sistema de Clima con IA
# Autor: Jonathan
# Descripción: Sistema web que muestra el clima de una ciudad
#              y genera recomendaciones usando inteligencia artificial.
# ==========================================================

from flask import Flask, render_template, jsonify

app = Flask(__name__)


# ==========================================================
# ACTIVIDAD 1 — VARIABLES GLOBALES / GLOBAL VARIABLES
# Variables con valores de ejemplo para el clima
# Scope: globales — accesibles desde todas las funciones
# ==========================================================

# Datos de la ciudad / City data
ciudad           = "Cucuta"       # str   — nombre de la ciudad consultada
pais             = "Colombia"     # str   — país de la ciudad

# Datos del clima / Weather data
temperatura      = 32             # int   — temperatura actual en °C
sensacion        = 34.7           # float — sensación térmica en °C
humedad          = 78             # int   — humedad relativa en %
velocidad_viento = 14.4           # float — velocidad del viento en km/h
visibilidad      = 9.5            # float — visibilidad en km
nubosidad        = 20             # int   — porcentaje de nubosidad

# Datos de la IA / AI data
recomendacion    = "Usa ropa ligera y bebe suficiente agua hoy."


# ==========================================================
# ACTIVIDAD 2 — DATOS DEL SISTEMA / SYSTEM DATA
# Diccionario global que agrupa todas las variables del clima
# Scope: global — usado por todas las funciones de cálculo
# ==========================================================

clima_actual = {
    "ciudad":      ciudad,
    "pais":        pais,
    "temperatura": temperatura,
    "sensacion":   sensacion,
    "humedad":     humedad,
    "viento":      velocidad_viento,
    "visibilidad": visibilidad,
    "nubosidad":   nubosidad,
    "descripcion": "Cielo despejado",
}


# ==========================================================
# ACTIVIDAD 3 — MÓDULO 1: CÁLCULOS / CALCULATIONS
# Funciones independientes con lógica pesada separada del menú.
# Cada función recibe parámetros locales y retorna un resultado.
# Scope local: las variables dentro de cada función no afuera.
# ==========================================================

def calcular_fahrenheit(celsius):
    """
    Convierte temperatura de Celsius a Fahrenheit.
    Converts temperature from Celsius to Fahrenheit.
    Scope local: 'celsius' solo existe dentro de esta función.
    Fórmula / Formula: (°C × 9/5) + 32
    """
    resultado = round((celsius * 9 / 5) + 32, 1)   # variable local
    return resultado

def calcular_indice_calor(temperatura, humedad):
    """
    Calcula el índice de calor basado en temperatura y humedad.
    Calculates heat index based on temperature and humidity.
    Scope local: 'temperatura' y 'humedad' son parámetros locales.
    """
    resultado = round(temperatura + (humedad * 0.1), 1)   # variable local
    return resultado

def calcular_diferencia_sensacion(sensacion, temperatura):
    """
    Calcula diferencia entre sensación térmica y temperatura real.
    Calculates difference between feels-like and real temperature.
    Scope local: parámetros independientes de las variables globales.
    """
    resultado = round(sensacion - temperatura, 1)   # variable local
    return resultado

def calcular_promedio_temperaturas(lista_temps):
    """
    Calcula el promedio de una lista de temperaturas del día.
    Calculates the average of a list of daily temperatures.
    Scope local: 'lista_temps' solo existe dentro de esta función.
    Fórmula / Formula: suma / cantidad
    """
    if not lista_temps:
        return 0
    resultado = round(sum(lista_temps) / len(lista_temps), 1)   # variable local
    return resultado

def calcular_probabilidad_lluvia(humedad, nubosidad):
    """
    Estima la probabilidad de lluvia basada en humedad y nubosidad.
    Estimates rain probability based on humidity and cloudiness.
    Scope local: parámetros recibidos, no toca variables globales.
    Fórmula propia / Custom formula: promedio ponderado.
    """
    resultado = round((humedad * 0.6) + (nubosidad * 0.4), 1)   # variable local
    return resultado


# ==========================================================
# ACTIVIDAD 3 — MÓDULO 2: CONSTRUCCIÓN DE RESPUESTAS
# Funciones que llaman a los cálculos y construyen el resultado.
# El menú (rutas Flask) queda limpio — solo llama estas funciones.
# ==========================================================

def obtener_clima():
    """
    Retorna los datos del clima actual formateados.
    Returns current weather data formatted.
    Usa la variable global clima_actual / Uses global clima_actual.
    """
    c = clima_actual   # referencia a variable global
    return {
        "titulo": "Clima Actual",
        "datos": [
            {"label": "Ciudad",      "valor": f"{c['ciudad']}, {c['pais']}"},
            {"label": "Temperatura", "valor": f"{c['temperatura']}°C"},
            {"label": "Sensación",   "valor": f"{c['sensacion']}°C"},
            {"label": "Humedad",     "valor": f"{c['humedad']}%"},
            {"label": "Viento",      "valor": f"{c['viento']} km/h"},
            {"label": "Visibilidad", "valor": f"{c['visibilidad']} km"},
            {"label": "Nubosidad",   "valor": f"{c['nubosidad']}%"},
            {"label": "Descripción", "valor": c['descripcion']},
        ]
    }

def obtener_conversion():
    """
    Llama a calcular_fahrenheit() y construye la respuesta.
    Calls calcular_fahrenheit() and builds the response.
    Menú limpio: toda la lógica está en calcular_fahrenheit().
    """
    temp = clima_actual["temperatura"]          # lee variable global
    fahrenheit = calcular_fahrenheit(temp)      # llama función modular
    return {
        "titulo": "Conversión de Temperatura",
        "datos": [
            {"label": "Temperatura °C", "valor": f"{temp}°C"},
            {"label": "Fórmula",        "valor": f"({temp} × 9/5) + 32"},
            {"label": "Resultado °F",   "valor": f"{fahrenheit}°F"},
        ]
    }

def obtener_indice_calor():
    """
    Llama a calcular_indice_calor() y calcular_diferencia_sensacion().
    Calls calcular_indice_calor() and calcular_diferencia_sensacion().
    """
    temp    = clima_actual["temperatura"]
    hum     = clima_actual["humedad"]
    sen     = clima_actual["sensacion"]
    indice  = calcular_indice_calor(temp, hum)              # función modular
    dif     = calcular_diferencia_sensacion(sen, temp)      # función modular
    return {
        "titulo": "Índice de Calor",
        "datos": [
            {"label": "Temperatura real",    "valor": f"{temp}°C"},
            {"label": "Humedad",             "valor": f"{hum}%"},
            {"label": "Fórmula índice",      "valor": f"{temp} + ({hum} × 0.1)"},
            {"label": "Índice de calor",     "valor": f"{indice}"},
            {"label": "Diferencia sensación","valor": f"+{dif}°C sobre temp. real"},
        ]
    }

def obtener_probabilidad_lluvia():
    """
    Llama a calcular_probabilidad_lluvia() y evalúa el nivel de riesgo.
    Calls calcular_probabilidad_lluvia() and evaluates risk level.
    """
    hum   = clima_actual["humedad"]
    nub   = clima_actual["nubosidad"]
    prob  = calcular_probabilidad_lluvia(hum, nub)   # función modular
    nivel = "Alta" if prob >= 70 else ("Media" if prob >= 40 else "Baja")
    return {
        "titulo": "Probabilidad de Lluvia",
        "datos": [
            {"label": "Humedad",         "valor": f"{hum}%"},
            {"label": "Nubosidad",       "valor": f"{nub}%"},
            {"label": "Fórmula",         "valor": f"({hum} × 0.6) + ({nub} × 0.4)"},
            {"label": "Probabilidad",    "valor": f"{prob}%"},
            {"label": "Nivel de riesgo", "valor": nivel},
        ]
    }

def obtener_promedio_dia():
    """
    Llama a calcular_promedio_temperaturas() con datos del día.
    Calls calcular_promedio_temperaturas() with daily data.
    Scope local: 'temperaturas' y 'horas' son variables locales.
    """
    temperaturas = [26, 28, 31, 32, 30, 27]    # variable local
    horas        = ["6am", "9am", "12pm", "3pm", "6pm", "9pm"]  # variable local
    promedio     = calcular_promedio_temperaturas(temperaturas)   # función modular
    maxima       = max(temperaturas)
    minima       = min(temperaturas)
    return {
        "titulo": "Promedio de Temperaturas del Día",
        "datos": [
            {"label": hora, "valor": f"{temp}°C"}
            for hora, temp in zip(horas, temperaturas)
        ] + [
            {"label": "─────────────", "valor": "─────"},
            {"label": "Fórmula",  "valor": f"suma({sum(temperaturas)}) / {len(temperaturas)}"},
            {"label": "Promedio", "valor": f"{promedio}°C"},
            {"label": "Máxima",   "valor": f"{maxima}°C"},
            {"label": "Mínima",   "valor": f"{minima}°C"},
        ]
    }


# ==========================================================
# ACTIVIDAD 2 & 3 — RUTAS / ROUTES (MENÚ LIMPIO)
# El cuerpo de cada ruta solo llama funciones — sin lógica pesada.
# Equivalente al if/elif limpio del ejemplo de consola.
# ==========================================================

@app.route("/")
def index():
    """Página principal — muestra el menú y datos de Actividad 1."""
    return render_template("index.html",
        ciudad                 = ciudad,
        pais                   = pais,
        temperatura            = temperatura,
        temperatura_fahrenheit = calcular_fahrenheit(temperatura),
        sensacion              = sensacion,
        diferencia_sensacion   = calcular_diferencia_sensacion(sensacion, temperatura),
        indice_calor           = calcular_indice_calor(temperatura, humedad),
        humedad                = humedad,
        velocidad_viento       = velocidad_viento,
        visibilidad            = visibilidad,
        nubosidad              = nubosidad,
        recomendacion          = recomendacion,
    )

@app.route("/opcion/1")
def opcion_ver_clima():
    return jsonify(obtener_clima())             # menú limpio — llama función

@app.route("/opcion/2")
def opcion_conversion():
    return jsonify(obtener_conversion())        # menú limpio — llama función

@app.route("/opcion/3")
def opcion_indice_calor():
    return jsonify(obtener_indice_calor())      # menú limpio — llama función

@app.route("/opcion/4")
def opcion_probabilidad_lluvia():
    return jsonify(obtener_probabilidad_lluvia())  # menú limpio — llama función

@app.route("/opcion/5")
def opcion_promedio():
    return jsonify(obtener_promedio_dia())      # menú limpio — llama función


# ==========================================================
# PUNTO DE ENTRADA / ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
