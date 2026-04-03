# ==============================================================
# Proyecto : Atmosfera — Sistema de Clima con IA
# Project  : Atmosfera — AI-Powered Weather System
# Autor    : Jonathan
# Archivo  : atmosfera.py
# ==============================================================

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


# ==============================================================
# ACTIVIDAD 1 — VARIABLES GLOBALES / GLOBAL VARIABLES
# Estado del sistema con tipos declarados explícitamente.
# System state with explicitly declared types.
# ==============================================================

ciudad           = "Cucuta"          # str   — nombre de la ciudad / city name
pais             = "Colombia"        # str   — país / country
temperatura      = 32                # int   — °C actual / current °C
sensacion        = 34.7              # float — sensación térmica / feels like
humedad          = 78                # int   — humedad relativa / relative humidity
velocidad_viento = 14.4              # float — km/h
visibilidad      = 9.5               # float — km
nubosidad        = 20                # int   — porcentaje / percentage
descripcion      = "Cielo despejado" # str   — condición / condition
recomendacion    = "Usa ropa ligera y bebe suficiente agua hoy."
temperaturas_dia = [26, 28, 31, 32, 30, 27]  # list[int] — cada 4h / every 4h
horas_dia        = ["6am", "9am", "12pm", "3pm", "6pm", "9pm"]


# ==============================================================
# ACTIVIDAD 2 — OPERACIONES BÁSICAS / BASIC OPERATIONS
# Cálculos directos sobre variables globales.
# Direct calculations on global variables.
# ==============================================================

temperatura_fahrenheit = (temperatura * 9 / 5) + 32   # °C → °F
indice_calor           = temperatura + (humedad * 0.1) # índice de calor / heat index
diferencia_sensacion   = round(sensacion - temperatura, 1)


# ==============================================================
# ACTIVIDAD 3 — MÓDULOS / MODULES
# Funciones independientes con responsabilidad única.
# Independent functions with single responsibility.
# ==============================================================

def calcular_fahrenheit(celsius):
    """
    Convierte °C a °F. / Converts °C to °F.
    Variable local: celsius | Fórmula: (°C × 9/5) + 32
    """
    resultado = (celsius * 9 / 5) + 32
    return round(resultado, 1)

def calcular_indice_calor(temp, hum):
    """
    Calcula el índice de calor. / Calculates heat index.
    Variables locales: temp, hum
    """
    return round(temp + (hum * 0.1), 1)

def calcular_diferencia_sensacion(sens, temp):
    """
    Diferencia entre sensación y temperatura real.
    Difference between feels-like and real temperature.
    """
    return round(sens - temp, 1)

def calcular_probabilidad_lluvia(hum, nub):
    """
    Probabilidad de lluvia con promedio ponderado.
    Rain probability with weighted average.
    """
    prob  = (hum * 0.6) + (nub * 0.4)
    nivel = "Alta / High" if prob >= 70 else ("Media / Medium" if prob >= 40 else "Baja / Low")
    return round(prob, 1), nivel

def calcular_promedio_temperaturas(temps):
    """
    Promedio, máxima y mínima de una lista.
    Average, max and min of a list.
    """
    return round(sum(temps) / len(temps), 1), max(temps), min(temps)

def obtener_clima_actual():
    """
    Empaqueta variables globales en un diccionario.
    Packages global variables into a dictionary.
    """
    return {
        "ciudad": ciudad, "pais": pais,
        "temperatura": temperatura, "sensacion": sensacion,
        "humedad": humedad, "viento": velocidad_viento,
        "visibilidad": visibilidad, "nubosidad": nubosidad,
        "descripcion": descripcion, "recomendacion": recomendacion,
    }


# ==============================================================
# ACTIVIDAD 4 — TOP-DOWN + PASO DE PARÁMETROS
# Funciones que reciben datos por argumento y retornan resultados.
# Functions that receive data by argument and return results.
# Validación robusta: conversión de tipos antes de operar.
# Robust validation: type conversion before operating.
# ==============================================================

def modulo_ver_clima(ciudad, pais, temp, sens, hum, viento, visib, nub, desc):
    """
    Módulo Top-Down: recibe parámetros, no usa globales.
    Top-Down module: receives parameters, doesn't use globals.
    Retorna / Returns: lista de filas formateadas con f-strings alineados.
    """
    dif = calcular_diferencia_sensacion(float(sens), float(temp))
    f   = calcular_fahrenheit(float(temp))
    return [
        {"label": "Ciudad / City",         "valor": f"{ciudad}, {pais}"},
        {"label": "Temperatura / Temp",    "valor": f"{temp}°C  /  {f}°F"},
        {"label": "Sensación / Feels like","valor": f"{sens}°C  (+{dif}°C)"},
        {"label": "Condición / Condition", "valor": desc},
        {"label": "Humedad / Humidity",    "valor": f"{hum}%"},
        {"label": "Viento / Wind",         "valor": f"{viento} km/h"},
        {"label": "Visibilidad / Visibility","valor": f"{visib} km"},
        {"label": "Nubosidad / Cloudiness","valor": f"{nub}%"},
    ]

def modulo_conversion(temp):
    """
    Módulo Top-Down: recibe temp como parámetro float.
    Top-Down module: receives temp as float parameter.
    Validación: float(temp) antes de calcular.
    Validation: float(temp) before calculating.
    """
    temp = float(temp)
    f    = calcular_fahrenheit(temp)
    return [
        {"label": "Temperatura °C",   "valor": f"{temp}°C"},
        {"label": "Fórmula / Formula","valor": f"({temp} × 9 ÷ 5) + 32"},
        {"label": "Resultado °F",     "valor": f"{f}°F"},
    ]

def modulo_indice_calor(temp, hum, sens):
    """
    Módulo Top-Down: recibe temp, hum, sens por parámetro.
    Top-Down module: receives temp, hum, sens by parameter.
    """
    temp   = float(temp)
    hum    = float(hum)
    sens   = float(sens)
    indice = calcular_indice_calor(temp, hum)
    dif    = calcular_diferencia_sensacion(sens, temp)
    return [
        {"label": "Temperatura / Temp",      "valor": f"{temp}°C"},
        {"label": "Humedad / Humidity",      "valor": f"{hum}%"},
        {"label": "Fórmula / Formula",       "valor": f"{temp} + ({hum} × 0.1)"},
        {"label": "Índice / Heat Index",     "valor": str(indice)},
        {"label": "Diferencia / Difference", "valor": f"+{dif}°C"},
    ]

def modulo_lluvia(hum, nub):
    """
    Módulo Top-Down: recibe hum y nub como parámetros enteros.
    Top-Down module: receives hum and nub as integer parameters.
    """
    hum  = int(hum)
    nub  = int(nub)
    prob, nivel = calcular_probabilidad_lluvia(hum, nub)
    return [
        {"label": "Humedad / Humidity",    "valor": f"{hum}%"},
        {"label": "Nubosidad / Cloudiness","valor": f"{nub}%"},
        {"label": "Fórmula / Formula",     "valor": f"({hum}×0.6) + ({nub}×0.4)"},
        {"label": "Probabilidad / Prob.",  "valor": f"{prob}%"},
        {"label": "Nivel / Level",         "valor": nivel},
    ]

def modulo_promedio(temps, horas):
    """
    Módulo Top-Down: recibe listas como parámetros.
    Top-Down module: receives lists as parameters.
    """
    promedio, maxima, minima = calcular_promedio_temperaturas(temps)
    filas = [{"label": h, "valor": f"{t}°C"} for h, t in zip(horas, temps)]
    filas += [
        {"label": "──────────────────","valor": "──────"},
        {"label": "Fórmula / Formula", "valor": f"suma({sum(temps)}) ÷ {len(temps)}"},
        {"label": "Promedio / Average","valor": f"{promedio}°C"},
        {"label": "Máxima / Maximum", "valor": f"{maxima}°C"},
        {"label": "Mínima / Minimum", "valor": f"{minima}°C"},
    ]
    return filas


# ==============================================================
# ACTIVIDAD 5 — TRATAMIENTO DE CADENAS / STRING HANDLING
# .strip() limpia espacios / .strip() cleans whitespace
# .lower() estandariza búsquedas / .lower() standardizes searches
# .title() capitaliza nombres / .title() capitalizes names
# f-strings con modificadores de ancho para reportes alineados.
# f-strings with width modifiers for aligned reports.
# ==============================================================

def estandarizar_texto(texto_entrada):
    """
    Limpia espacios y convierte a minúsculas para comparaciones.
    Cleans whitespace and converts to lowercase for comparisons.
    Ej / Ex: "  Cucuta  " → "cucuta"
    """
    return texto_entrada.strip().lower()   # .strip() + .lower()

def formatear_nombre(texto_entrada):
    """
    Limpia espacios y capitaliza correctamente para mostrar al usuario.
    Cleans whitespace and title-cases for display to the user.
    Ej / Ex: "  cielo despejado  " → "Cielo Despejado"
    """
    return texto_entrada.strip().title()   # .strip() + .title()

def buscar_ciudad(termino, catalogo):
    """
    Busca una ciudad en el catálogo ignorando mayúsculas y espacios.
    Searches a city in the catalog ignoring case and whitespace.
    Implementa .strip().lower() para comparación insensible a mayúsculas.
    Implements .strip().lower() for case-insensitive comparison.
    Retorna / Returns: dict de ciudad o None.
    """
    termino_limpio = estandarizar_texto(termino)   # estandarizar búsqueda
    for ciudad_item in catalogo:
        if termino_limpio in estandarizar_texto(ciudad_item["nombre"]):
            return ciudad_item
    return None

def generar_reporte_clima(c):
    """
    Genera un reporte de clima con f-strings alineados profesionalmente.
    Generates a weather report with professionally aligned f-strings.
    Usa modificadores de ancho / Uses width modifiers: {var:<20} {var:>10}
    """
    ancho_etiqueta = 28   # ancho columna etiqueta / label column width
    ancho_valor    = 14   # ancho columna valor / value column width

    # f-strings con modificadores de ancho para alineación perfecta
    # f-strings with width modifiers for perfect alignment
    lineas = [
        f"{'─' * (ancho_etiqueta + ancho_valor + 4)}",
        f"  {'REPORTE DE CLIMA / WEATHER REPORT':^{ancho_etiqueta + ancho_valor}}",
        f"{'─' * (ancho_etiqueta + ancho_valor + 4)}",
        f"  {'Ciudad / City':<{ancho_etiqueta}} {c['ciudad'] + ', ' + c['pais']:>{ancho_valor}}",
        f"  {'Temperatura / Temperature':<{ancho_etiqueta}} {str(c['temperatura']) + '°C':>{ancho_valor}}",
        f"  {'Sensación / Feels Like':<{ancho_etiqueta}} {str(c['sensacion']) + '°C':>{ancho_valor}}",
        f"  {'Humedad / Humidity':<{ancho_etiqueta}} {str(c['humedad']) + '%':>{ancho_valor}}",
        f"  {'Viento / Wind':<{ancho_etiqueta}} {str(c['viento']) + ' km/h':>{ancho_valor}}",
        f"  {'Visibilidad / Visibility':<{ancho_etiqueta}} {str(c['visibilidad']) + ' km':>{ancho_valor}}",
        f"  {'Nubosidad / Cloudiness':<{ancho_etiqueta}} {str(c['nubosidad']) + '%':>{ancho_valor}}",
        f"  {'Condición / Condition':<{ancho_etiqueta}} {c['descripcion']:>{ancho_valor}}",
        f"{'─' * (ancho_etiqueta + ancho_valor + 4)}",
    ]
    return lineas

# Catálogo de ciudades para búsqueda / City catalog for search
CATALOGO_CIUDADES = [
    {"nombre": "Cucuta",      "temp": 32, "hum": 78},
    {"nombre": "Bogota",      "temp": 14, "hum": 85},
    {"nombre": "Medellin",    "temp": 22, "hum": 72},
    {"nombre": "Cali",        "temp": 27, "hum": 68},
    {"nombre": "Barranquilla","temp": 33, "hum": 80},
    {"nombre": "Cartagena",   "temp": 34, "hum": 82},
]


# ==============================================================
# RUTAS / COORDINADOR TOP-DOWN / TOP-DOWN COORDINATOR
# Cada ruta solo coordina: obtiene → pasa parámetros → recibe retorno.
# Each route only coordinates: gets → passes params → receives return.
# ==============================================================

@app.route("/")
def index():
    """Página principal / Main page."""
    c = obtener_clima_actual()
    return render_template("index.html",
        ciudad      = c["ciudad"],
        pais        = c["pais"],
        temperatura = c["temperatura"],
        sensacion   = c["sensacion"],
        humedad     = c["humedad"],
        viento      = c["viento"],
        visibilidad = c["visibilidad"],
        nubosidad   = c["nubosidad"],
        descripcion = c["descripcion"],
        recomendacion = c["recomendacion"],
        temp_f      = calcular_fahrenheit(c["temperatura"]),
        indice      = calcular_indice_calor(c["temperatura"], c["humedad"]),
        dif_sens    = calcular_diferencia_sensacion(c["sensacion"], c["temperatura"]),
    )

@app.route("/opcion/1")
def opcion_1():
    c    = obtener_clima_actual()
    data = modulo_ver_clima(
        c["ciudad"], c["pais"], c["temperatura"], c["sensacion"],
        c["humedad"], c["viento"], c["visibilidad"], c["nubosidad"], c["descripcion"]
    )
    return jsonify({"titulo": "Clima Actual / Current Weather", "datos": data})

@app.route("/opcion/2")
def opcion_2():
    data = modulo_conversion(temperatura)
    return jsonify({"titulo": "Conversión °C → °F / Conversion", "datos": data})

@app.route("/opcion/3")
def opcion_3():
    data = modulo_indice_calor(temperatura, humedad, sensacion)
    return jsonify({"titulo": "Índice de Calor / Heat Index", "datos": data})

@app.route("/opcion/4")
def opcion_4():
    data = modulo_lluvia(humedad, nubosidad)
    return jsonify({"titulo": "Probabilidad de Lluvia / Rain Probability", "datos": data})

@app.route("/opcion/5")
def opcion_5():
    data = modulo_promedio(temperaturas_dia, horas_dia)
    return jsonify({"titulo": "Promedio del Día / Daily Average", "datos": data})

@app.route("/opcion/6")
def opcion_6():
    """
    ACTIVIDAD 5 — Búsqueda de ciudad con estandarizar_texto().
    Busca ignorando mayúsculas y espacios / Searches ignoring case and whitespace.
    """
    # Obtener término de búsqueda y aplicar .strip().lower()
    # Get search term and apply .strip().lower()
    termino = request.args.get("q", "").strip()

    if not termino:
        return jsonify({"titulo": "Búsqueda / Search", "datos": [
            {"label": "Estado / Status", "valor": "Ingresa una ciudad / Enter a city"}
        ]})

    resultado = buscar_ciudad(termino, CATALOGO_CIUDADES)

    if resultado:
        # formatear_nombre() aplica .title() para mostrar correctamente
        # formatear_nombre() applies .title() for proper display
        nombre_display = formatear_nombre(resultado["nombre"])
        datos = [
            {"label": "Búsqueda / Search",     "valor": f'"{termino}"  →  "{nombre_display}"'},
            {"label": "Ciudad / City",          "valor": nombre_display},
            {"label": "Temperatura / Temp",     "valor": f"{resultado['temp']}°C"},
            {"label": "Humedad / Humidity",     "valor": f"{resultado['hum']}%"},
            {"label": "Estado / Status",        "valor": "✔ Encontrada / Found"},
        ]
    else:
        nombre_display = formatear_nombre(termino)
        datos = [
            {"label": "Búsqueda / Search",  "valor": f'"{termino}"'},
            {"label": "Estado / Status",    "valor": f"✘ '{nombre_display}' no encontrada / not found"},
        ]

    return jsonify({"titulo": "Búsqueda de Ciudad / City Search", "datos": datos})

@app.route("/reporte")
def reporte():
    """
    ACTIVIDAD 5 — Reporte con f-strings alineados.
    Report with aligned f-strings using width modifiers.
    """
    c      = obtener_clima_actual()
    lineas = generar_reporte_clima(c)
    return jsonify({"titulo": "Reporte Profesional / Professional Report", "lineas": lineas})


# ==============================================================
# PUNTO DE ENTRADA / ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
