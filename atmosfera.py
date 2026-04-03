# ==============================================================
# Proyecto : Atmosfera — Sistema de Clima con IA
# Project  : Atmosfera — AI-Powered Weather System
# Autor    : Jonathan
# Archivo  : atmosfera.py
# ==============================================================
# Arquitectura : Top-Down | Modular | Validación Robusta
# Architecture : Top-Down | Modular | Robust Validation
# APIs         : OpenWeatherMap (clima) + Groq/LLaMA3 (IA)
# ==============================================================

import os               # Acceso a variables de entorno / Access to env vars
import requests         # Peticiones HTTP a APIs externas / HTTP requests to external APIs
from dotenv import load_dotenv          # Carga el archivo .env / Loads .env file
from flask import Flask, render_template, jsonify, request

# load_dotenv() lee el archivo .env y carga OPENWEATHER_API_KEY y GROQ_API_KEY
# load_dotenv() reads .env file and loads OPENWEATHER_API_KEY and GROQ_API_KEY
load_dotenv()

app = Flask(__name__)


# ==============================================================
# ACTIVIDAD 1 — CONFIGURACIÓN GLOBAL / GLOBAL CONFIGURATION
# ==============================================================
# Este bloque define las constantes y claves de API que todo
# el sistema necesita. Son globales porque no cambian durante
# la ejecución y deben ser accesibles desde cualquier función.
#
# This block defines constants and API keys that the entire
# system needs. They are global because they don't change
# during execution and must be accessible from any function.
# ==============================================================

# Claves de API leídas desde variables de entorno (archivo .env)
# API keys read from environment variables (.env file)
OPENWEATHER_API_KEY  = os.environ.get("OPENWEATHER_API_KEY", "575c46598b508807e6ade44a63bb71a7")
GROQ_API_KEY         = os.environ.get("GROQ_API_KEY", "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")

# URLs base de las APIs externas / Base URLs for external APIs
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
GROQ_BASE_URL        = "https://api.groq.com/openai/v1/chat/completions"

# Días de la semana para el pronóstico / Weekdays for forecast
DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

# Temperaturas simuladas del día (cada 4 horas) / Simulated day temps (every 4h)
# Se usan cuando la API no está disponible / Used when API is not available
HORAS_DIA        = ["6am", "9am", "12pm", "3pm", "6pm", "9pm"]
TEMPERATURAS_DIA = [26, 28, 31, 32, 30, 27]   # list[int]


# ==============================================================
# ACTIVIDAD 1 — DICCIONARIO DE CIUDADES PRECARGADAS
# ACTIVITY 1 — PRELOADED CITIES DICTIONARY
# ==============================================================
# Este diccionario cumple dos funciones:
# 1. Datos de respaldo cuando la API no está disponible.
# 2. Alias de ciudades que OpenWeatherMap no reconoce por nombre.
#
# This dictionary serves two purposes:
# 1. Fallback data when the API is unavailable.
# 2. Aliases for cities OpenWeatherMap doesn't recognize by name.
#
# Estructura de cada entrada / Structure of each entry:
#   "clave_busqueda": {
#       "nombre"     : str   — nombre para mostrar / display name
#       "pais"       : str   — código de país ISO / ISO country code
#       "lat"        : float — latitud GPS / GPS latitude
#       "lon"        : float — longitud GPS / GPS longitude
#       "temp"       : int   — temperatura precargada °C / preloaded temp °C
#       "sensacion"  : float — sensación térmica / feels like
#       "humedad"    : int   — humedad % / humidity %
#       "viento"     : float — viento km/h / wind km/h
#       "visibilidad": float — visibilidad km / visibility km
#       "nubosidad"  : int   — nubosidad % / cloudiness %
#       "descripcion": str   — condición del cielo / sky condition
#       "icono"      : str   — código de icono OpenWeatherMap / icon code
#   }
# ==============================================================

CIUDADES = {
    # ── Colombia ──────────────────────────────────────────────
    "cucuta": {
        "nombre": "Cúcuta", "pais": "CO",
        "lat": 7.8939, "lon": -72.5078,
        "temp": 32, "sensacion": 34.7, "humedad": 78,
        "viento": 14.4, "visibilidad": 9.5, "nubosidad": 20,
        "descripcion": "Cielo despejado", "icono": "01d",
    },
    "bogota": {
        "nombre": "Bogotá", "pais": "CO",
        "lat": 4.7110, "lon": -74.0721,
        "temp": 14, "sensacion": 12.0, "humedad": 85,
        "viento": 10.8, "visibilidad": 7.0, "nubosidad": 75,
        "descripcion": "Parcialmente nublado", "icono": "02d",
    },
    "medellin": {
        "nombre": "Medellín", "pais": "CO",
        "lat": 6.2442, "lon": -75.5812,
        "temp": 22, "sensacion": 23.5, "humedad": 72,
        "viento": 9.0, "visibilidad": 10.0, "nubosidad": 40,
        "descripcion": "Cielo despejado", "icono": "01d",
    },
    "cali": {
        "nombre": "Cali", "pais": "CO",
        "lat": 3.4516, "lon": -76.5320,
        "temp": 27, "sensacion": 29.0, "humedad": 68,
        "viento": 12.6, "visibilidad": 10.0, "nubosidad": 30,
        "descripcion": "Cielo despejado", "icono": "01d",
    },
    "barranquilla": {
        "nombre": "Barranquilla", "pais": "CO",
        "lat": 10.9685, "lon": -74.7813,
        "temp": 33, "sensacion": 36.0, "humedad": 80,
        "viento": 18.0, "visibilidad": 9.0, "nubosidad": 25,
        "descripcion": "Caluroso y húmedo", "icono": "01d",
    },
    "cartagena": {
        "nombre": "Cartagena", "pais": "CO",
        "lat": 10.3910, "lon": -75.4794,
        "temp": 34, "sensacion": 37.5, "humedad": 82,
        "viento": 20.0, "visibilidad": 9.5, "nubosidad": 20,
        "descripcion": "Soleado", "icono": "01d",
    },
    "bucaramanga": {
        "nombre": "Bucaramanga", "pais": "CO",
        "lat": 7.1254, "lon": -73.1198,
        "temp": 28, "sensacion": 30.0, "humedad": 65,
        "viento": 11.0, "visibilidad": 10.0, "nubosidad": 35,
        "descripcion": "Parcialmente nublado", "icono": "02d",
    },
    "manizales": {
        "nombre": "Manizales", "pais": "CO",
        "lat": 5.0703, "lon": -75.5138,
        "temp": 17, "sensacion": 15.5, "humedad": 88,
        "viento": 8.0, "visibilidad": 5.0, "nubosidad": 90,
        "descripcion": "Nublado con lluvia", "icono": "10d",
    },
    # ── Latinoamérica / Latin America ─────────────────────────
    "mexico": {
        "nombre": "Ciudad de México", "pais": "MX",
        "lat": 19.4326, "lon": -99.1332,
        "temp": 20, "sensacion": 19.0, "humedad": 60,
        "viento": 15.0, "visibilidad": 10.0, "nubosidad": 50,
        "descripcion": "Nublado", "icono": "03d",
    },
    "buenos aires": {
        "nombre": "Buenos Aires", "pais": "AR",
        "lat": -34.6037, "lon": -58.3816,
        "temp": 18, "sensacion": 17.0, "humedad": 70,
        "viento": 22.0, "visibilidad": 10.0, "nubosidad": 45,
        "descripcion": "Viento moderado", "icono": "02d",
    },
}


# ==============================================================
# ACTIVIDAD 2 — OPERACIONES BÁSICAS / BASIC OPERATIONS
# ==============================================================
# Estas variables se calculan una sola vez al iniciar el sistema
# usando los datos precargados de Cúcuta como ciudad por defecto.
# Los resultados se muestran en el sidebar de la interfaz.
#
# These variables are calculated once at system startup using
# Cúcuta's preloaded data as the default city. Results are
# shown in the interface sidebar.
# ==============================================================

_ciudad_default    = CIUDADES["cucuta"]                            # dict — ciudad inicial
temperatura_default = _ciudad_default["temp"]                      # int
humedad_default     = _ciudad_default["humedad"]                   # int
sensacion_default   = _ciudad_default["sensacion"]                 # float

# Operaciones básicas sobre los datos precargados
# Basic operations on preloaded data
temperatura_fahrenheit = (_ciudad_default["temp"] * 9 / 5) + 32   # °C → °F
indice_calor_default   = _ciudad_default["temp"] + (_ciudad_default["humedad"] * 0.1)
diferencia_default     = round(_ciudad_default["sensacion"] - _ciudad_default["temp"], 1)


# ==============================================================
# ACTIVIDAD 3 — MÓDULOS DE CÁLCULO / CALCULATION MODULES
# ==============================================================
# Cada función tiene una responsabilidad única y bien definida.
# Reciben parámetros → procesan → retornan resultado.
# No acceden a variables globales directamente (scope local).
#
# Each function has a single, well-defined responsibility.
# They receive parameters → process → return result.
# They don't access global variables directly (local scope).
# ==============================================================

def calcular_fahrenheit(celsius):
    """
    Convierte temperatura de Celsius a Fahrenheit.
    Converts temperature from Celsius to Fahrenheit.
    Parámetro / Parameter: celsius (float) — temperatura en °C
    Retorna    / Returns  : float — temperatura en °F
    Fórmula    / Formula  : (°C × 9/5) + 32
    """
    # Variable local: resultado — no afecta ninguna variable global
    # Local variable: resultado — doesn't affect any global variable
    resultado = (celsius * 9 / 5) + 32
    return round(resultado, 1)

def calcular_indice_calor(temp, hum):
    """
    Calcula el índice de calor combinando temperatura y humedad.
    Calculates heat index combining temperature and humidity.
    Parámetros / Parameters: temp (float), hum (float)
    Retorna    / Returns   : float — índice de calor / heat index
    """
    # El índice de calor sube cuando la humedad es alta
    # Heat index rises when humidity is high
    return round(temp + (hum * 0.1), 1)

def calcular_diferencia_sensacion(sens, temp):
    """
    Calcula la diferencia entre sensación térmica y temperatura real.
    Calculates the difference between feels-like and real temperature.
    Parámetros / Parameters: sens (float), temp (float)
    Retorna    / Returns   : float — diferencia en °C / difference in °C
    """
    return round(sens - temp, 1)

def calcular_probabilidad_lluvia(hum, nub):
    """
    Estima la probabilidad de lluvia usando un promedio ponderado.
    Estimates rain probability using a weighted average.
    Parámetros / Parameters: hum (int) humedad, nub (int) nubosidad
    Retorna    / Returns   : tuple (float probabilidad, str nivel)
    Fórmula    / Formula   : (humedad × 0.6) + (nubosidad × 0.4)
    """
    prob  = (hum * 0.6) + (nub * 0.4)
    # Clasificación del nivel de riesgo / Risk level classification
    nivel = "Alta / High" if prob >= 70 else ("Media / Medium" if prob >= 40 else "Baja / Low")
    return round(prob, 1), nivel

def calcular_promedio_temperaturas(temps):
    """
    Calcula promedio, máxima y mínima de una lista de temperaturas.
    Calculates average, max and min of a temperature list.
    Parámetro / Parameter: temps (list[int]) — lista de temperaturas
    Retorna   / Returns  : tuple (float promedio, int max, int min)
    Validación / Validation: verifica que la lista no esté vacía
    """
    # Validación: lista no puede estar vacía / Validation: list cannot be empty
    if not temps:
        return 0.0, 0, 0
    return round(sum(temps) / len(temps), 1), max(temps), min(temps)


# ==============================================================
# ACTIVIDAD 3 — MÓDULOS DE CONEXIÓN / CONNECTION MODULES
# ==============================================================
# Estas funciones manejan la comunicación con APIs externas.
# Cada una tiene manejo de errores con try/except para que
# el sistema nunca se caiga si la API falla.
#
# These functions handle communication with external APIs.
# Each one has try/except error handling so the system never
# crashes if the API fails.
# ==============================================================

def obtener_clima_api(lat, lon):
    """
    Consulta el clima actual en OpenWeatherMap por coordenadas GPS.
    Queries current weather on OpenWeatherMap by GPS coordinates.
    Parámetros / Parameters: lat (float), lon (float)
    Retorna    / Returns   : dict con datos del clima o None si falla
                             dict with weather data or None if fails
    Validación / Validation: verifica clave API, timeout y status HTTP
    """
    # Validación: verificar que existe la clave de API antes de llamar
    # Validation: verify API key exists before calling
    if not OPENWEATHER_API_KEY:
        return None

    params = {
        "lat":   lat,
        "lon":   lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",   # Celsius / Celsius
        "lang":  "es",       # Descripciones en español / Descriptions in Spanish
    }

    try:
        # timeout=8 evita que la app se congele si la API no responde
        # timeout=8 prevents the app from freezing if API doesn't respond
        resp = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=8)
        resp.raise_for_status()   # Lanza excepción si status >= 400
        return resp.json()
    except requests.exceptions.RequestException:
        # Si falla la API, retornamos None para usar datos precargados
        # If API fails, we return None to use preloaded data
        return None

def parsear_clima_api(data):
    """
    Transforma el JSON crudo de OpenWeatherMap en un diccionario limpio.
    Transforms raw OpenWeatherMap JSON into a clean dictionary.
    Parámetro / Parameter: data (dict) — respuesta cruda de la API
    Retorna   / Returns  : dict con campos normalizados / normalized fields
    """
    return {
        "ciudad":      data.get("name", "Desconocida"),
        "pais":        data.get("sys", {}).get("country", ""),
        "temp":        round(data["main"]["temp"]),
        "sensacion":   round(data["main"]["feels_like"], 1),
        "humedad":     data["main"]["humidity"],
        "viento":      round(data["wind"]["speed"] * 3.6, 1),   # m/s → km/h
        "visibilidad": round(data.get("visibility", 10000) / 1000, 1),
        "nubosidad":   data["clouds"]["all"],
        "descripcion": formatear_nombre(data["weather"][0]["description"]),
        "icono":       data["weather"][0]["icon"],
        "condition_id": data["weather"][0]["id"],
    }

def generar_recomendaciones_ia(weather):
    """
    Llama a Groq (LLaMA 3) para generar recomendaciones cotidianas con IA.
    Calls Groq (LLaMA 3) to generate daily recommendations with AI.
    Parámetro / Parameter: weather (dict) — datos del clima
    Retorna   / Returns  : list[str] — 6 recomendaciones / 6 recommendations
    Validación / Validation: verifica clave API, maneja errores de red
    """
    # Validación: sin clave de Groq, retornamos recomendaciones locales
    # Validation: without Groq key, return local recommendations
    if not GROQ_API_KEY:
        return generar_recomendaciones_locales(weather)

    # Construcción del prompt con f-string e inyección de datos del clima
    # Prompt construction with f-string and weather data injection
    prompt = f"""Eres un asistente de clima amigable y práctico. Con base en los siguientes datos meteorológicos,
genera exactamente 6 recomendaciones cotidianas concretas y útiles para el usuario.

DATOS DEL CLIMA:
- Ciudad: {weather['ciudad']}, {weather['pais']}
- Temperatura actual: {weather['temp']}°C (sensación térmica {weather['sensacion']}°C)
- Condición: {weather['descripcion']}
- Humedad: {weather['humedad']}%
- Viento: {weather['viento']} km/h
- Visibilidad: {weather['visibilidad']} km
- Nubosidad: {weather['nubosidad']}%

INSTRUCCIONES:
- Genera exactamente 6 recomendaciones, una por línea, sin numeración ni viñetas.
- Cubre: vestimenta, lluvia/paraguas, ejercicio al aire libre, transporte, salud/hidratación y consejo general.
- Tono: amigable, directo y práctico. Máximo 20 palabras por recomendación.
- Responde SOLO con las 6 recomendaciones, sin introducción ni cierre."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    body = {
        "model":       "llama-3.3-70b-versatile",
        "messages":    [{"role": "user", "content": prompt}],
        "max_tokens":  400,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(GROQ_BASE_URL, headers=headers, json=body, timeout=15)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        # Separar por líneas y filtrar las vacías con list comprehension
        # Split by lines and filter empty ones with list comprehension
        recs = [l.strip() for l in raw.splitlines() if l.strip()]
        return recs[:6]
    except Exception:
        # Si Groq falla, usamos recomendaciones locales como respaldo
        # If Groq fails, use local recommendations as fallback
        return generar_recomendaciones_locales(weather)

def generar_recomendaciones_locales(weather):
    """
    Genera recomendaciones sin IA usando reglas lógicas locales.
    Generates recommendations without AI using local logical rules.
    Se usa como respaldo cuando Groq no está disponible.
    Used as fallback when Groq is not available.
    Parámetro / Parameter: weather (dict)
    Retorna   / Returns  : list[str] — 6 recomendaciones locales
    """
    temp   = weather.get("temp", 25)
    hum    = weather.get("humedad", 60)
    viento = weather.get("viento", 10)
    nub    = weather.get("nubosidad", 30)
    recs   = []

    # Regla 1: Vestimenta según temperatura / Clothing rule based on temperature
    if temp >= 30:
        recs.append(f"Con {temp}°C usa ropa muy ligera y de colores claros.")
    elif temp >= 22:
        recs.append(f"Con {temp}°C una camiseta y pantalón ligero es suficiente.")
    elif temp >= 15:
        recs.append(f"Con {temp}°C lleva una chaqueta ligera por si refresca.")
    else:
        recs.append(f"Con {temp}°C abrígate bien con abrigo y bufanda.")

    # Regla 2: Paraguas según nubosidad y humedad / Umbrella based on cloudiness
    if nub >= 80 or hum >= 85:
        recs.append("Alto riesgo de lluvia: lleva paraguas o impermeable.")
    else:
        recs.append("No se esperan lluvias, puedes salir sin paraguas.")

    # Regla 3: Ejercicio al aire libre / Outdoor exercise
    if temp >= 33:
        recs.append(f"Con {temp}°C evita ejercicio intenso; sal muy temprano o al anochecer.")
    elif viento >= 40:
        recs.append(f"Viento de {viento} km/h dificulta el ejercicio afuera.")
    else:
        recs.append(f"Buenas condiciones para ejercitarte al aire libre con {temp}°C.")

    # Regla 4: Transporte / Transportation
    if viento >= 50:
        recs.append(f"Viento fuerte ({viento} km/h): precaución al conducir.")
    elif nub >= 80:
        recs.append("Posibles calzadas mojadas: mantén distancia de seguridad.")
    else:
        recs.append("Buenas condiciones viales hoy.")

    # Regla 5: Hidratación / Hydration
    if temp >= 28 and hum >= 70:
        recs.append(f"Calor y humedad alta: hidratación constante, mínimo 2 litros.")
    elif temp >= 28:
        recs.append(f"Con {temp}°C bebe bastante agua y usa protector solar.")
    else:
        recs.append(f"Mantén buena hidratación con {hum}% de humedad ambiental.")

    # Regla 6: Consejo general / General advice
    if 18 <= temp <= 26 and nub < 50:
        recs.append(f"¡Día ideal en {weather.get('ciudad','tu ciudad')}! Aprovecha el buen tiempo.")
    elif temp >= 32:
        recs.append("Busca sombra o espacios con aire acondicionado al mediodía.")
    else:
        recs.append(f"Disfruta el día con precaución según las condiciones actuales.")

    return recs


# ==============================================================
# ACTIVIDAD 4 — TOP-DOWN + PASO DE PARÁMETROS
# ==============================================================
# Módulos que reciben TODOS sus datos por parámetro.
# No dependen de variables globales: scope local garantizado.
# El coordinador (ruta Flask) les pasa los datos y recoge retornos.
#
# Modules that receive ALL their data by parameter.
# They don't depend on global variables: guaranteed local scope.
# The coordinator (Flask route) passes data and collects returns.
# ==============================================================

def modulo_ver_clima(ciudad, pais, temp, sens, hum, viento, visib, nub, desc, icono="01d"):
    """
    Módulo Top-Down: empaqueta todos los datos del clima para mostrar.
    Top-Down module: packages all weather data for display.
    Parámetros: recibe 10 valores, no usa ninguna variable global.
    Parameters: receives 10 values, uses no global variables.
    Retorna / Returns: list[dict] con filas label/valor para la UI.
    """
    # Conversiones locales usando funciones del Módulo 3
    # Local conversions using Module 3 functions
    dif = calcular_diferencia_sensacion(float(sens), float(temp))
    f   = calcular_fahrenheit(float(temp))
    return [
        {"label": "Ciudad / City",             "valor": f"{ciudad}, {pais}"},
        {"label": "Temperatura / Temperature", "valor": f"{temp}°C  /  {f}°F"},
        {"label": "Sensación / Feels Like",    "valor": f"{sens}°C  (+{dif}°C)"},
        {"label": "Condición / Condition",     "valor": desc},
        {"label": "Humedad / Humidity",        "valor": f"{hum}%"},
        {"label": "Viento / Wind",             "valor": f"{viento} km/h"},
        {"label": "Visibilidad / Visibility",  "valor": f"{visib} km"},
        {"label": "Nubosidad / Cloudiness",    "valor": f"{nub}%"},
    ]

def modulo_conversion(temp):
    """
    Módulo Top-Down: convierte temperatura °C → °F mostrando la fórmula.
    Top-Down module: converts temperature °C → °F showing the formula.
    Validación robusta: convierte a float antes de operar.
    Robust validation: converts to float before operating.
    """
    temp = float(temp)                    # Validación de tipo / Type validation
    f    = calcular_fahrenheit(temp)      # Llama al módulo 3 / Calls module 3
    return [
        {"label": "Temperatura °C",    "valor": f"{temp}°C"},
        {"label": "Fórmula / Formula", "valor": f"({temp} × 9 ÷ 5) + 32"},
        {"label": "Resultado °F",      "valor": f"{f}°F"},
    ]

def modulo_indice_calor(temp, hum, sens):
    """
    Módulo Top-Down: calcula índice de calor y diferencia de sensación.
    Top-Down module: calculates heat index and feels-like difference.
    Validación robusta: convierte temp, hum, sens a float.
    Robust validation: converts temp, hum, sens to float.
    """
    temp   = float(temp)
    hum    = float(hum)
    sens   = float(sens)
    indice = calcular_indice_calor(temp, hum)
    dif    = calcular_diferencia_sensacion(sens, temp)
    return [
        {"label": "Temperatura / Temp",       "valor": f"{temp}°C"},
        {"label": "Humedad / Humidity",       "valor": f"{hum}%"},
        {"label": "Fórmula / Formula",        "valor": f"{temp} + ({hum} × 0.1)"},
        {"label": "Índice / Heat Index",      "valor": str(indice)},
        {"label": "Diferencia / Difference",  "valor": f"+{dif}°C"},
    ]

def modulo_lluvia(hum, nub):
    """
    Módulo Top-Down: calcula probabilidad de lluvia.
    Top-Down module: calculates rain probability.
    Validación robusta: convierte hum y nub a int, verifica rango 0-100.
    Robust validation: converts hum and nub to int, checks range 0-100.
    """
    hum  = max(0, min(100, int(hum)))   # Clamp entre 0-100 / Clamp between 0-100
    nub  = max(0, min(100, int(nub)))
    prob, nivel = calcular_probabilidad_lluvia(hum, nub)
    return [
        {"label": "Humedad / Humidity",      "valor": f"{hum}%"},
        {"label": "Nubosidad / Cloudiness",  "valor": f"{nub}%"},
        {"label": "Fórmula / Formula",       "valor": f"({hum}×0.6) + ({nub}×0.4)"},
        {"label": "Probabilidad / Prob.",    "valor": f"{prob}%"},
        {"label": "Nivel / Level",           "valor": nivel},
    ]

def modulo_promedio(temps, horas):
    """
    Módulo Top-Down: calcula estadísticas de temperaturas del día.
    Top-Down module: calculates day temperature statistics.
    Validación: verifica que ambas listas tengan el mismo tamaño.
    Validation: verifies both lists have the same size.
    """
    # Validación de longitudes / Length validation
    if len(temps) != len(horas):
        return [{"label": "Error / Error", "valor": "Listas de distinto tamaño / Lists of different size"}]
    promedio, maxima, minima = calcular_promedio_temperaturas(temps)
    filas = [{"label": h, "valor": f"{t}°C"} for h, t in zip(horas, temps)]
    filas += [
        {"label": "─────────────────────","valor": "──────"},
        {"label": "Fórmula / Formula",   "valor": f"suma({sum(temps)}) ÷ {len(temps)}"},
        {"label": "Promedio / Average",  "valor": f"{promedio}°C"},
        {"label": "Máxima / Maximum",    "valor": f"{maxima}°C"},
        {"label": "Mínima / Minimum",    "valor": f"{minima}°C"},
    ]
    return filas


# ==============================================================
# ACTIVIDAD 5 — TRATAMIENTO DE CADENAS / STRING HANDLING
# ==============================================================
# .strip()  → elimina espacios al inicio y final / removes leading/trailing spaces
# .lower()  → convierte a minúsculas para comparaciones / lowercases for comparisons
# .title()  → capitaliza cada palabra para mostrar / title-cases for display
# f-strings → modificadores de ancho para reportes alineados
#             width modifiers for aligned reports
# ==============================================================

def estandarizar_texto(texto_entrada):
    """
    Limpia espacios y convierte a minúsculas para comparaciones internas.
    Cleans whitespace and lowercases for internal comparisons.
    Ej / Ex: "  CUCUTA  " → "cucuta"
    Validación: verifica que la entrada sea string, no None.
    Validation: verifies input is string, not None.
    """
    # Validación: si no es string, convertir primero / Validate: if not string, convert first
    if not isinstance(texto_entrada, str):
        texto_entrada = str(texto_entrada)
    return texto_entrada.strip().lower()   # .strip() elimina espacios, .lower() estandariza

def formatear_nombre(texto_entrada):
    """
    Limpia espacios y capitaliza para mostrar al usuario.
    Cleans whitespace and capitalizes for display to the user.
    Ej / Ex: "  cielo despejado  " → "Cielo Despejado"
    """
    if not isinstance(texto_entrada, str):
        texto_entrada = str(texto_entrada)
    return texto_entrada.strip().capitalize()   # .strip() + .capitalize()

def buscar_ciudad_catalogo(termino, catalogo):
    """
    Busca una ciudad en el diccionario CIUDADES ignorando mayúsculas y espacios.
    Searches a city in the CIUDADES dictionary ignoring case and whitespace.
    Implementa .strip().lower() para comparación insensible a capitalización.
    Implements .strip().lower() for case-insensitive comparison.
    Parámetro / Parameter : termino (str) — texto ingresado por el usuario
    Retorna   / Returns   : dict de ciudad o None si no se encuentra
    """
    # Validación: termino no puede estar vacío / Validation: termino cannot be empty
    if not termino or not termino.strip():
        return None

    termino_limpio = estandarizar_texto(termino)   # "  Cucuta  " → "cucuta"

    # Búsqueda directa por clave del diccionario / Direct search by dictionary key
    if termino_limpio in catalogo:
        return catalogo[termino_limpio]

    # Búsqueda parcial: busca el término dentro del nombre de la ciudad
    # Partial search: searches the term within the city name
    for clave, datos in catalogo.items():
        nombre_estandarizado = estandarizar_texto(datos["nombre"])
        if termino_limpio in nombre_estandarizado or nombre_estandarizado in termino_limpio:
            return datos

    return None   # No encontrada / Not found

def generar_reporte_clima(c):
    """
    Genera un reporte de clima con f-strings alineados profesionalmente.
    Generates a weather report with professionally aligned f-strings.
    Usa modificadores de ancho / Uses width modifiers: {var:<28} {var:>14}
    Parámetro / Parameter: c (dict) — datos del clima
    Retorna   / Returns  : list[str] — líneas del reporte alineado
    """
    # Constantes de ancho para alineación perfecta / Width constants for perfect alignment
    EW = 28   # ancho columna etiqueta / label column width
    VW = 14   # ancho columna valor / value column width

    # Precompute formatted values to avoid nesting f-strings
    ciudad_val = f"{c['ciudad']}, {c['pais']}"
    temp_val = f"{c['temp']}°C"
    sens_val = f"{c['sensacion']}°C"
    hum_val = f"{c['humedad']}%"
    viento_val = f"{c['viento']} km/h"
    visib_val = f"{c['visibilidad']} km"
    nub_val = f"{c['nubosidad']}%"
    desc_val = c['descripcion']

    # f-strings con modificadores de ancho :<EW (alinea izquierda) y :>VW (alinea derecha)
    # f-strings with width modifiers :<EW (left-align) and :>VW (right-align)
    lineas = [
        f"{'─' * (EW + VW + 4)}",
        f"  {'REPORTE DE CLIMA / WEATHER REPORT':^{EW + VW}}",
        f"{'─' * (EW + VW + 4)}",
        f"  {'Ciudad / City':<{EW}} {ciudad_val:>{VW}}",
        f"  {'Temperatura / Temperature':<{EW}} {temp_val:>{VW}}",
        f"  {'Sensación / Feels Like':<{EW}} {sens_val:>{VW}}",
        f"  {'Humedad / Humidity':<{EW}} {hum_val:>{VW}}",
        f"  {'Viento / Wind':<{EW}} {viento_val:>{VW}}",
        f"  {'Visibilidad / Visibility':<{EW}} {visib_val:>{VW}}",
        f"  {'Nubosidad / Cloudiness':<{EW}} {nub_val:>{VW}}",
        f"  {'Condición / Condition':<{EW}} {desc_val:>{VW}}",
        f"{'─' * (EW + VW + 4)}",
    ]
    return lineas


# ==============================================================
# FUNCIÓN PRINCIPAL DE BÚSQUEDA / MAIN SEARCH FUNCTION
# ==============================================================
# Esta función es el corazón del sistema:
# 1. Intenta obtener datos reales de OpenWeatherMap via API
# 2. Si falla, cae al diccionario CIUDADES precargado
# 3. Si tampoco está en el diccionario, retorna error claro
# 4. Genera recomendaciones con IA (Groq) o locales como respaldo
#
# This function is the heart of the system:
# 1. Tries to get real data from OpenWeatherMap via API
# 2. If it fails, falls back to the preloaded CIUDADES dictionary
# 3. If not in dictionary either, returns a clear error
# 4. Generates recommendations with AI (Groq) or local fallback
# ==============================================================

def buscar_y_obtener_clima(termino):
    """
    Busca el clima de una ciudad usando API + diccionario como respaldo.
    Searches weather for a city using API + dictionary as fallback.
    Parámetro / Parameter: termino (str) — nombre de ciudad ingresado
    Retorna   / Returns  : tuple (dict weather, list recs, str error)
    """
    # Paso 1: Validación de entrada / Step 1: Input validation
    termino = estandarizar_texto(termino)   # .strip().lower()
    if not termino:
        return None, [], "Ingresa el nombre de una ciudad. / Enter a city name."

    weather = None

    # Paso 2: Buscar en diccionario precargado para obtener coordenadas
    # Step 2: Search preloaded dictionary to get coordinates
    ciudad_dict = buscar_ciudad_catalogo(termino, CIUDADES)

    # Paso 3: Intentar con API de OpenWeatherMap
    # Step 3: Try OpenWeatherMap API
    if ciudad_dict and OPENWEATHER_API_KEY:
        # Usar coordenadas del diccionario para llamar a la API
        # Use dictionary coordinates to call the API
        raw_api = obtener_clima_api(ciudad_dict["lat"], ciudad_dict["lon"])
        if raw_api:
            weather = parsear_clima_api(raw_api)

    # Paso 4: Si la API falló o no hay clave, usar datos del diccionario
    # Step 4: If API failed or no key, use dictionary data
    if not weather and ciudad_dict:
        weather = {
            "ciudad":      ciudad_dict["nombre"],
            "pais":        ciudad_dict["pais"],
            "temp":        ciudad_dict["temp"],
            "sensacion":   ciudad_dict["sensacion"],
            "humedad":     ciudad_dict["humedad"],
            "viento":      ciudad_dict["viento"],
            "visibilidad": ciudad_dict["visibilidad"],
            "nubosidad":   ciudad_dict["nubosidad"],
            "descripcion": ciudad_dict["descripcion"],
            "icono":       ciudad_dict["icono"],
            "condition_id": 800,
            "fuente":      "diccionario",   # Indica origen de los datos / Indicates data source
        }

    # Paso 5: Si no se encontró en ninguna fuente, retornar error
    # Step 5: If not found in any source, return error
    if not weather:
        nombre_display = formatear_nombre(termino)
        return None, [], f"Ciudad '{nombre_display}' no encontrada. / City '{nombre_display}' not found."

    # Paso 6: Generar recomendaciones con IA o locales
    # Step 6: Generate recommendations with AI or local fallback
    recomendaciones = generar_recomendaciones_ia(weather)

    return weather, recomendaciones, None   # None = sin error / None = no error


# ==============================================================
# RUTAS FLASK — COORDINADOR TOP-DOWN / FLASK ROUTES — TOP-DOWN COORDINATOR
# ==============================================================
# Cada ruta actúa solo como coordinador:
# obtiene datos → llama módulos → recibe retornos → responde JSON/HTML
# No contiene lógica de negocio — toda está en los módulos anteriores.
#
# Each route acts only as coordinator:
# gets data → calls modules → receives returns → responds JSON/HTML
# Contains no business logic — all is in the modules above.
# ==============================================================

@app.route("/")
def index():
    """
    Ruta principal: carga la página con datos de Cúcuta por defecto.
    Main route: loads the page with Cúcuta's data by default.
    """
    # Ciudad por defecto del diccionario / Default city from dictionary
    c = CIUDADES["cucuta"]
    return render_template("index.html",
        ciudad        = c["nombre"],
        pais          = c["pais"],
        temperatura   = c["temp"],
        sensacion     = c["sensacion"],
        humedad       = c["humedad"],
        viento        = c["viento"],
        visibilidad   = c["visibilidad"],
        nubosidad     = c["nubosidad"],
        descripcion   = c["descripcion"],
        icono         = c["icono"],
        recomendacion = "Busca una ciudad para obtener recomendaciones con IA.",
        temp_f        = calcular_fahrenheit(c["temp"]),
        indice        = calcular_indice_calor(c["temp"], c["humedad"]),
        dif_sens      = calcular_diferencia_sensacion(c["sensacion"], c["temp"]),
        ciudades_lista = list(CIUDADES.values()),   # Para el selector / For the selector
    )

@app.route("/api/buscar")
def api_buscar():
    """
    Endpoint principal: busca el clima de una ciudad con API + IA.
    Main endpoint: searches weather for a city with API + AI.
    Parámetro URL / URL Parameter: ?ciudad=nombre
    Retorna / Returns: JSON con weather, recommendations, error
    """
    termino = request.args.get("ciudad", "").strip()

    # Validación de entrada / Input validation
    if not termino:
        return jsonify({"error": "Ingresa el nombre de una ciudad. / Enter a city name."}), 400

    weather, recs, error = buscar_y_obtener_clima(termino)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({
        "weather":        weather,
        "recomendaciones": recs,
        "fuente":         weather.get("fuente", "api"),
    })

@app.route("/opcion/1")
def opcion_1():
    """Opción 1: Ver clima de Cúcuta (ciudad por defecto del diccionario)."""
    c    = CIUDADES["cucuta"]
    data = modulo_ver_clima(
        c["nombre"], c["pais"], c["temp"], c["sensacion"],
        c["humedad"], c["viento"], c["visibilidad"], c["nubosidad"],
        c["descripcion"], c["icono"]
    )
    return jsonify({"titulo": "Clima Actual / Current Weather", "datos": data})

@app.route("/opcion/2")
def opcion_2():
    """Opción 2: Convertir temperatura de la ciudad por defecto."""
    data = modulo_conversion(CIUDADES["cucuta"]["temp"])
    return jsonify({"titulo": "Conversión °C → °F / Conversion", "datos": data})

@app.route("/opcion/3")
def opcion_3():
    """Opción 3: Índice de calor de la ciudad por defecto."""
    c    = CIUDADES["cucuta"]
    data = modulo_indice_calor(c["temp"], c["humedad"], c["sensacion"])
    return jsonify({"titulo": "Índice de Calor / Heat Index", "datos": data})

@app.route("/opcion/4")
def opcion_4():
    """Opción 4: Probabilidad de lluvia de la ciudad por defecto."""
    c    = CIUDADES["cucuta"]
    data = modulo_lluvia(c["humedad"], c["nubosidad"])
    return jsonify({"titulo": "Probabilidad de Lluvia / Rain Probability", "datos": data})

@app.route("/opcion/5")
def opcion_5():
    """Opción 5: Promedio de temperaturas simuladas del día."""
    data = modulo_promedio(TEMPERATURAS_DIA, HORAS_DIA)
    return jsonify({"titulo": "Promedio del Día / Daily Average", "datos": data})

@app.route("/opcion/6")
def opcion_6():
    """
    Opción 6: Búsqueda en el diccionario CIUDADES con estandarizar_texto().
    Option 6: Dictionary search with estandarizar_texto().
    Aplica .strip().lower() al término antes de comparar.
    Applies .strip().lower() to term before comparing.
    """
    termino = request.args.get("q", "").strip()

    if not termino:
        return jsonify({"titulo": "Búsqueda / Search", "datos": [
            {"label": "Estado / Status", "valor": "Ingresa una ciudad / Enter a city"}
        ]})

    resultado = buscar_ciudad_catalogo(termino, CIUDADES)

    if resultado:
        nombre_display = formatear_nombre(resultado["nombre"])
        datos = [
            {"label": "Término / Search term",  "valor": f'"{termino}"  →  "{nombre_display}"'},
            {"label": "Ciudad / City",           "valor": nombre_display},
            {"label": "País / Country",          "valor": resultado["pais"]},
            {"label": "Temperatura / Temp",      "valor": f"{resultado['temp']}°C"},
            {"label": "Humedad / Humidity",      "valor": f"{resultado['humedad']}%"},
            {"label": "Condición / Condition",   "valor": resultado["descripcion"]},
            {"label": "Estado / Status",         "valor": "✔ Encontrada / Found"},
        ]
    else:
        nombre_display = formatear_nombre(termino)
        datos = [
            {"label": "Búsqueda / Search", "valor": f'"{termino}"'},
            {"label": "Estado / Status",   "valor": f"✘ '{nombre_display}' no encontrada / not found"},
            {"label": "Sugerencia / Hint", "valor": "Prueba: cucuta, bogota, medellin, cali…"},
        ]

    return jsonify({"titulo": "Búsqueda en Diccionario / Dictionary Search", "datos": datos})

@app.route("/reporte")
def reporte():
    """
    Reporte con f-strings alineados de la ciudad por defecto.
    Report with aligned f-strings of the default city.
    """
    c      = CIUDADES["cucuta"]
    lineas = generar_reporte_clima(c)
    return jsonify({"titulo": "Reporte Profesional / Professional Report", "lineas": lineas})


# ==============================================================
# PUNTO DE ENTRADA / ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
