# ==============================================================
# Proyecto : Atmosfera — Sistema de Clima con IA
# Autor    : Jonathan
# Archivo  : atmosfera.py
# ==============================================================

from flask import Flask, render_template, jsonify

app = Flask(__name__)


# ==============================================================
# ACTIVIDAD 1 — VARIABLES GLOBALES
# Datos del clima con sus tipos declarados explícitamente.
# Estas variables son el "estado" del sistema.
# ==============================================================

ciudad           = "Cucuta"
pais             = "Colombia"
temperatura      = 32          # int   — °C
sensacion        = 34.7        # float — °C
humedad          = 78          # int   — %
velocidad_viento = 14.4        # float — km/h
visibilidad      = 9.5         # float — km
nubosidad        = 20          # int   — %
descripcion      = "Cielo despejado"
recomendacion    = "Usa ropa ligera y bebe suficiente agua hoy."
temperaturas_dia = [26, 28, 31, 32, 30, 27]
horas_dia        = ["6am", "9am", "12pm", "3pm", "6pm", "9pm"]


# ==============================================================
# ACTIVIDAD 2 — OPERACIONES BÁSICAS
# Cálculos directos sobre las variables globales.
# ==============================================================

temperatura_fahrenheit = (temperatura * 9 / 5) + 32
indice_calor           = temperatura + (humedad * 0.1)
diferencia_sensacion   = round(sensacion - temperatura, 1)


# ==============================================================
# ACTIVIDAD 3 — MÓDULOS (FUNCIONES INDEPENDIENTES)
# Cada función encapsula un proceso lógico específico.
# El menú principal solo las llama — no contiene lógica pesada.
# ==============================================================

def calcular_fahrenheit(celsius):
    """Convierte °C a °F. Variable local: celsius."""
    # Fórmula: (°C × 9/5) + 32
    resultado = (celsius * 9 / 5) + 32
    return round(resultado, 1)

def calcular_indice_calor(temp, hum):
    """Calcula el índice de calor. Variables locales: temp, hum."""
    indice = temp + (hum * 0.1)
    return round(indice, 1)

def calcular_diferencia_sensacion(sens, temp):
    """Diferencia entre sensación térmica y temperatura real."""
    return round(sens - temp, 1)

def calcular_probabilidad_lluvia(hum, nub):
    """Estima probabilidad de lluvia con promedio ponderado."""
    prob  = (hum * 0.6) + (nub * 0.4)
    nivel = "Alta" if prob >= 70 else ("Media" if prob >= 40 else "Baja")
    return round(prob, 1), nivel

def calcular_promedio_temperaturas(temps):
    """Promedio, máxima y mínima de una lista de temperaturas."""
    promedio = sum(temps) / len(temps)
    return round(promedio, 1), max(temps), min(temps)

def obtener_clima_actual():
    """Empaqueta las variables globales en un diccionario limpio."""
    return {
        "ciudad": ciudad, "pais": pais,
        "temperatura": temperatura, "sensacion": sensacion,
        "humedad": humedad, "viento": velocidad_viento,
        "visibilidad": visibilidad, "nubosidad": nubosidad,
        "descripcion": descripcion, "recomendacion": recomendacion,
    }


# ==============================================================
# ACTIVIDAD 4 — TOP-DOWN + PASO DE PARÁMETROS
# Las funciones NO usan variables globales directamente.
# Reciben datos como argumentos y retornan resultados con return.
# El coordinador (ruta Flask) solo pasa parámetros y recoge retornos.
# ==============================================================

def modulo_ver_clima(ciudad, pais, temp, sens, hum, viento, visib, nub, desc):
    """
    Módulo Top-Down: recibe todos los parámetros por argumento.
    No accede a variables globales. Retorna lista de datos formateados.
    """
    dif = calcular_diferencia_sensacion(sens, temp)   # retorno recibido
    f   = calcular_fahrenheit(temp)                   # retorno recibido
    return [
        {"label": "Ciudad",            "valor": f"{ciudad}, {pais}"},
        {"label": "Temperatura",       "valor": f"{temp}°C  /  {f}°F"},
        {"label": "Sensación térmica", "valor": f"{sens}°C  (+{dif}°C)"},
        {"label": "Condición",         "valor": desc},
        {"label": "Humedad",           "valor": f"{hum}%"},
        {"label": "Viento",            "valor": f"{viento} km/h"},
        {"label": "Visibilidad",       "valor": f"{visib} km"},
        {"label": "Nubosidad",         "valor": f"{nub}%"},
    ]

def modulo_conversion(temp):
    """
    Módulo Top-Down: recibe temp (float) por parámetro.
    Validación: temp debe ser numérico. Retorna lista de pasos.
    """
    # Validación robusta: convertir a float antes de operar
    temp = float(temp)
    f    = calcular_fahrenheit(temp)   # retorno recibido
    return [
        {"label": "Temperatura °C", "valor": f"{temp}°C"},
        {"label": "Fórmula",        "valor": f"({temp} × 9 ÷ 5) + 32"},
        {"label": "Resultado °F",   "valor": f"{f}°F"},
    ]

def modulo_indice_calor(temp, hum, sens):
    """
    Módulo Top-Down: recibe temp, hum, sens como parámetros.
    Retorna lista con resultados de dos funciones independientes.
    """
    temp = float(temp)
    hum  = float(hum)
    sens = float(sens)
    indice = calcular_indice_calor(temp, hum)              # retorno recibido
    dif    = calcular_diferencia_sensacion(sens, temp)     # retorno recibido
    return [
        {"label": "Temperatura real",     "valor": f"{temp}°C"},
        {"label": "Humedad",              "valor": f"{hum}%"},
        {"label": "Fórmula",              "valor": f"{temp} + ({hum} × 0.1)"},
        {"label": "Índice de calor",      "valor": str(indice)},
        {"label": "Diferencia sensación", "valor": f"+{dif}°C sobre temp. real"},
    ]

def modulo_lluvia(hum, nub):
    """
    Módulo Top-Down: recibe hum y nub como parámetros enteros.
    Retorna resultado de calcular_probabilidad_lluvia().
    """
    hum  = int(hum)
    nub  = int(nub)
    prob, nivel = calcular_probabilidad_lluvia(hum, nub)   # retorno recibido
    return [
        {"label": "Humedad",         "valor": f"{hum}%"},
        {"label": "Nubosidad",       "valor": f"{nub}%"},
        {"label": "Fórmula",         "valor": f"({hum}×0.6) + ({nub}×0.4)"},
        {"label": "Probabilidad",    "valor": f"{prob}%"},
        {"label": "Nivel de riesgo", "valor": nivel},
    ]

def modulo_promedio(temps, horas):
    """
    Módulo Top-Down: recibe lista de temps y horas como parámetros.
    Retorna resultados de calcular_promedio_temperaturas().
    """
    promedio, maxima, minima = calcular_promedio_temperaturas(temps)  # retorno
    filas = [{"label": h, "valor": f"{t}°C"} for h, t in zip(horas, temps)]
    filas += [
        {"label": "──────────", "valor": "──────"},
        {"label": "Fórmula",   "valor": f"suma({sum(temps)}) ÷ {len(temps)}"},
        {"label": "Promedio",  "valor": f"{promedio}°C"},
        {"label": "Máxima",    "valor": f"{maxima}°C"},
        {"label": "Mínima",    "valor": f"{minima}°C"},
    ]
    return filas


# ==============================================================
# RUTAS / COORDINADOR TOP-DOWN
# Cada ruta solo: obtiene datos → pasa parámetros → recibe retorno.
# No contiene lógica de negocio.
# ==============================================================

@app.route("/")
def index():
    c = obtener_clima_actual()
    return render_template("index.html",
        ciudad     = c["ciudad"],
        pais       = c["pais"],
        temperatura= c["temperatura"],
        sensacion  = c["sensacion"],
        humedad    = c["humedad"],
        viento     = c["viento"],
        visibilidad= c["visibilidad"],
        nubosidad  = c["nubosidad"],
        descripcion= c["descripcion"],
        recomendacion = c["recomendacion"],
        temp_f     = calcular_fahrenheit(c["temperatura"]),
        indice     = calcular_indice_calor(c["temperatura"], c["humedad"]),
        dif_sens   = calcular_diferencia_sensacion(c["sensacion"], c["temperatura"]),
    )

@app.route("/opcion/1")
def opcion_1():
    """Coordinador: pasa parámetros a modulo_ver_clima() y retorna resultado."""
    c    = obtener_clima_actual()
    data = modulo_ver_clima(
        c["ciudad"], c["pais"], c["temperatura"], c["sensacion"],
        c["humedad"], c["viento"], c["visibilidad"], c["nubosidad"], c["descripcion"]
    )
    return jsonify({"titulo": "Clima Actual", "datos": data})

@app.route("/opcion/2")
def opcion_2():
    """Coordinador: pasa temperatura a modulo_conversion() y retorna resultado."""
    data = modulo_conversion(temperatura)
    return jsonify({"titulo": "Conversión °C → °F", "datos": data})

@app.route("/opcion/3")
def opcion_3():
    """Coordinador: pasa temp, hum, sens a modulo_indice_calor() y retorna."""
    data = modulo_indice_calor(temperatura, humedad, sensacion)
    return jsonify({"titulo": "Índice de Calor", "datos": data})

@app.route("/opcion/4")
def opcion_4():
    """Coordinador: pasa hum y nub a modulo_lluvia() y retorna resultado."""
    data = modulo_lluvia(humedad, nubosidad)
    return jsonify({"titulo": "Probabilidad de Lluvia", "datos": data})

@app.route("/opcion/5")
def opcion_5():
    """Coordinador: pasa lista de temps y horas a modulo_promedio() y retorna."""
    data = modulo_promedio(temperaturas_dia, horas_dia)
    return jsonify({"titulo": "Promedio de Temperaturas", "datos": data})


# ==============================================================
# PUNTO DE ENTRADA / ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
