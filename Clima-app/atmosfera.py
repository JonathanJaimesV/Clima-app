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
import csv              # Lectura y escritura de archivos CSV / CSV file reading and writing
import datetime         # Marcas de tiempo para el log / Timestamps for the log
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
OPENWEATHER_API_KEY  = os.environ.get("OPENWEATHER_API_KEY", "")
GROQ_API_KEY         = os.environ.get("GROQ_API_KEY", "")

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
# ACTIVIDAD 8 — PERSISTENCIA DE DATOS / DATA PERSISTENCE
# ==============================================================
# Este módulo implementa la persistencia del sistema usando
# archivos de texto y CSV. Cada búsqueda de ciudad queda
# registrada permanentemente, incluso tras cerrar el servidor.
#
# This module implements system persistence using text and CSV
# files. Every city search is permanently recorded, even after
# closing the server.
#
# Archivos generados / Generated files:
#   log_sistema.txt  — log de eventos del sistema (bilingüe)
#   historial.csv    — historial de búsquedas con temperatura y hora
#
# Patrones usados / Patterns used:
#   with open()  — context manager para gestión de buffers
#   mode 'w'     — escritura (crea o sobreescribe el archivo)
#   mode 'a'     — append (agrega sin borrar lo existente)
#   mode 'r'     — lectura del contenido completo
#   try/except FileNotFoundError — crea el archivo si no existe
# ==============================================================

# Rutas de los archivos de persistencia / Persistence file paths
LOG_FILE      = "log_sistema.txt"    # str — log de eventos / event log
HISTORIAL_CSV = "historial.csv"      # str — historial de búsquedas / search history

# Lista de diccionarios cargada desde el CSV al iniciar
# List of dictionaries loaded from CSV on startup
# Estructura de cada entrada / Structure of each entry:
#   {"ciudad": str, "pais": str, "temp": str, "humedad": str,
#    "viento": str, "descripcion": str, "fecha": str, "hora": str}
historial_busquedas = []   # list[dict] — se llena en cargar_historial_csv()


def inicializar_log():
    """
    ACTIVIDAD 8 — Misión Técnica paso 1, 2 y 3:
    Crea el archivo log_sistema.txt con context manager (with open).
    Escribe tres líneas bilingües con marca de tiempo.
    Luego lo abre en modo 'a' (append) para agregar una línea sin borrar.

    Activity 8 — Technical Mission steps 1, 2 and 3:
    Creates log_sistema.txt with context manager (with open).
    Writes three bilingual lines with timestamps.
    Then opens it in 'a' (append) mode to add a line without erasing.

    Usa / Uses: with open(), mode 'w', mode 'a', encoding='utf-8'
    """
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # PASO 1 y 2: Creación con context manager + escritura de buffers
    # STEP 1 & 2: Creation with context manager + buffer writing
    # with open() garantiza que Python vacíe el buffer al salir del bloque
    # with open() guarantees Python flushes the buffer on block exit
    with open(LOG_FILE, "w", encoding="utf-8") as archivo:
        archivo.write(f"[{ahora}] Sistema iniciado / System started\n")
        archivo.write(f"[{ahora}] Atmosfera v1.0 — Sistema de Clima con IA / AI Weather System\n")
        archivo.write(f"[{ahora}] APIs conectadas: OpenWeatherMap + Groq LLaMA3 / APIs connected\n")

    # PASO 3: Modo append — agrega línea sin borrar las anteriores
    # STEP 3: Append mode — adds line without erasing previous ones
    with open(LOG_FILE, "a", encoding="utf-8") as archivo:
        archivo.write(f"[{ahora}] Servidor Flask en puerto 5000 / Flask server on port 5000\n")


def leer_log():
    """
    ACTIVIDAD 8 — Misión Técnica paso 4:
    Lee el contenido completo del log, lo almacena en una lista
    y lo muestra por consola.

    Activity 8 — Technical Mission step 4:
    Reads the complete log content, stores it in a list
    and displays it on the console.

    Validación / Validation: try/except FileNotFoundError
    Retorna / Returns: list[str] — líneas del log / log lines
    """
    try:
        # Lectura con context manager / Reading with context manager
        with open(LOG_FILE, "r", encoding="utf-8") as archivo:
            # Almacenar en lista / Store in list
            lineas = archivo.readlines()

        # Mostrar por consola / Display on console
        print("\n" + "=" * 50)
        print("  LOG DEL SISTEMA / SYSTEM LOG")
        print("=" * 50)
        for linea in lineas:
            print(linea, end="")
        print("=" * 50 + "\n")

        return lineas

    except FileNotFoundError:
        # Si el archivo no existe, lo creamos en lugar de cerrarse
        # If file doesn't exist, create it instead of crashing
        print(f"[INFO] Archivo '{LOG_FILE}' no encontrado. Creando... / File not found. Creating...")
        inicializar_log()
        return []


def registrar_evento_log(mensaje):
    """
    Agrega una línea al log con marca de tiempo actual.
    Appends a line to the log with current timestamp.
    Usa modo 'a' para no borrar el historial previo.
    Uses mode 'a' to not erase previous history.

    Parámetro / Parameter: mensaje (str) — evento a registrar / event to log
    Validación / Validation: try/except captura errores de escritura
    """
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Append con context manager / Append with context manager
        with open(LOG_FILE, "a", encoding="utf-8") as archivo:
            archivo.write(f"[{ahora}] {mensaje}\n")
            # Python vacía el buffer automáticamente al salir del with
            # Python flushes the buffer automatically on with exit
    except Exception as e:
        print(f"[ERROR] No se pudo escribir en el log: {e} / Could not write to log: {e}")


def guardar_busqueda_csv(weather):
    """
    ACTIVIDAD 8 — Integración al Proyecto:
    Guarda cada búsqueda de ciudad en historial.csv automáticamente.
    Cada fila es un diccionario con los datos del clima consultado.

    Activity 8 — Project Integration:
    Saves every city search to historial.csv automatically.
    Each row is a dictionary with the queried weather data.

    Parámetro / Parameter: weather (dict) — datos del clima / weather data
    Usa / Uses: with open(), mode 'a', csv.DictWriter, newline=''
    Validación / Validation: try/except para errores de I/O
    """
    ahora     = datetime.datetime.now()
    campos    = ["ciudad", "pais", "temp", "humedad", "viento",
                 "descripcion", "fecha", "hora"]

    # Construir fila como diccionario / Build row as dictionary
    fila = {
        "ciudad":      estandarizar_texto(weather.get("ciudad", "")).title(),
        "pais":        weather.get("pais",        ""),
        "temp":        str(weather.get("temp",     "")),
        "humedad":     str(weather.get("humedad",  "")),
        "viento":      str(weather.get("viento",   "")),
        "descripcion": weather.get("descripcion", ""),
        "fecha":       ahora.strftime("%Y-%m-%d"),
        "hora":        ahora.strftime("%H:%M:%S"),
    }

    try:
        # Verificar si el archivo ya existe para escribir o no el header
        # Check if file exists to decide whether to write header
        archivo_existe = os.path.isfile(HISTORIAL_CSV)

        # Modo 'a' con newline='' requerido por csv en Windows
        # Mode 'a' with newline='' required by csv on Windows
        with open(HISTORIAL_CSV, "a", encoding="utf-8", newline="") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=campos)

            # Solo escribir header si el archivo es nuevo
            # Only write header if file is new
            if not archivo_existe:
                writer.writeheader()

            # Escribir la fila — Python vacía el buffer al salir del with
            # Write row — Python flushes buffer on with exit
            writer.writerow(fila)

        # También agregar a la lista en memoria / Also add to in-memory list
        historial_busquedas.append(fila)

        # Registrar en el log / Register in log
        registrar_evento_log(
            f"Búsqueda guardada / Search saved: {fila['ciudad']}, {fila['pais']} — {fila['temp']}°C"
        )

    except Exception as e:
        registrar_evento_log(f"Error al guardar búsqueda / Error saving search: {e}")


def cargar_historial_csv():
    """
    ACTIVIDAD 8 — Carga de Datos al Startup:
    Al iniciar el servidor, lee historial.csv y carga todas las
    búsquedas previas en la lista de diccionarios historial_busquedas.
    Así los datos persisten entre reinicios del servidor.

    Activity 8 — Startup Data Loading:
    On server start, reads historial.csv and loads all previous
    searches into the historial_busquedas list of dictionaries.
    This way data persists between server restarts.

    Validación / Validation:
      - FileNotFoundError → crea el archivo vacío automáticamente
      - csv vacío → retorna lista vacía sin errores
    Retorna / Returns: list[dict] — registros cargados / loaded records
    """
    global historial_busquedas

    try:
        # Lectura con context manager / Reading with context manager
        with open(HISTORIAL_CSV, "r", encoding="utf-8", newline="") as archivo:
            reader = csv.DictReader(archivo)
            # Cargar cada fila como diccionario en la lista global
            # Load each row as dict into the global list
            historial_busquedas = [dict(fila) for fila in reader]

        total = len(historial_busquedas)
        print(f"[STARTUP] {total} búsquedas cargadas desde {HISTORIAL_CSV} / searches loaded from CSV")
        registrar_evento_log(f"Historial cargado: {total} registros / History loaded: {total} records")

    except FileNotFoundError:
        # Si no existe el archivo, el sistema lo crea vacío y continúa
        # If file doesn't exist, system creates it empty and continues
        print(f"[STARTUP] '{HISTORIAL_CSV}' no encontrado. Creando archivo nuevo... / File not found. Creating...")
        historial_busquedas = []

        try:
            # Crear archivo vacío con solo el header
            # Create empty file with only the header
            campos = ["ciudad", "pais", "temp", "humedad", "viento",
                      "descripcion", "fecha", "hora"]
            with open(HISTORIAL_CSV, "w", encoding="utf-8", newline="") as archivo:
                writer = csv.DictWriter(archivo, fieldnames=campos)
                writer.writeheader()
            registrar_evento_log(f"Archivo '{HISTORIAL_CSV}' creado automáticamente / File auto-created")
        except Exception as e:
            print(f"[ERROR] No se pudo crear {HISTORIAL_CSV}: {e}")

    except Exception as e:
        print(f"[ERROR] Error al cargar historial: {e} / Error loading history: {e}")
        historial_busquedas = []

    return historial_busquedas


def obtener_historial_reciente(limite=10):
    """
    Retorna los últimos N registros del historial en memoria.
    Returns the last N records from the in-memory history.
    Parámetro / Parameter: limite (int) — cantidad de registros a retornar
    Retorna   / Returns  : list[dict] — registros más recientes / most recent records
    """
    # Invertir la lista para obtener los más recientes primero
    # Reverse the list to get the most recent first
    return list(reversed(historial_busquedas))[:limite]


# ==============================================================
# ACTIVIDAD 9 — TAD + APAREO DE ARCHIVOS / TAD + FILE MATCHING
# ==============================================================
# Un TAD (Tipo Abstracto de Datos) es un molde que define tanto
# los ATRIBUTOS (qué es) como los MÉTODOS (qué hace) de una entidad.
# Ya no usamos diccionarios sueltos en el flujo principal;
# instanciamos objetos de la clase CiudadTAD.
#
# A TAD (Abstract Data Type) is a mold that defines both the
# ATTRIBUTES (what it is) and the METHODS (what it does) of an entity.
# We no longer use loose dictionaries in the main flow;
# we instantiate objects of the CiudadTAD class.
#
# Apareo / Matching:
#   historial.csv  ←→  ciudades_maestro.txt
#   Se cruzan por la clave "ciudad" para generar reportes de corte.
#   They are crossed by the "ciudad" key to generate cut reports.
# ==============================================================

# Archivo maestro de ciudades para el apareo / Master city file for matching
MAESTRO_CIUDADES_TXT = "ciudades_maestro.txt"


class CiudadTAD:
    """
    TAD — Tipo Abstracto de Datos para una Ciudad con datos climáticos.
    TAD — Abstract Data Type for a City with weather data.

    Encapsula los atributos y la lógica de negocio del clima en un objeto.
    Encapsulates weather attributes and business logic in one object.

    Atributos / Attributes:
        nombre      (str)   — nombre de la ciudad / city name
        pais        (str)   — código de país ISO / ISO country code
        temperatura (float) — temperatura en °C / temperature in °C
        humedad     (int)   — humedad relativa % / relative humidity %
        viento      (float) — velocidad del viento km/h / wind speed km/h
        descripcion (str)   — condición del cielo / sky condition
    """

    def __init__(self, nombre, pais, temperatura, humedad, viento, descripcion=""):
        """
        Constructor: recibe 6 parámetros y los asigna como atributos del objeto.
        Constructor: receives 6 parameters and assigns them as object attributes.
        Validación robusta de tipos dentro del constructor.
        Robust type validation inside the constructor.
        """
        # Actividad 5 — Tratamiento de cadenas en el constructor
        # Activity 5 — String handling in the constructor
        self.nombre      = estandarizar_texto(nombre).title()   # .strip().lower().title()
        self.pais        = str(pais).strip().upper()            # estandarizar país
        self.temperatura = round(float(temperatura), 1)         # validar float
        self.humedad     = max(0, min(100, int(humedad)))       # clamp 0–100
        self.viento      = round(float(viento), 1)             # validar float
        self.descripcion = str(descripcion).strip().capitalize()

    # ── Métodos de lógica de negocio / Business logic methods ──

    def calcular_fahrenheit(self):
        """
        Método de negocio: convierte la temperatura del objeto a °F.
        Business method: converts object temperature to °F.
        Retorna / Returns: float — temperatura en °F
        """
        return round((self.temperatura * 9 / 5) + 32, 1)

    def calcular_indice_calor(self):
        """
        Método de negocio: calcula el índice de calor del objeto.
        Business method: calculates the object's heat index.
        Retorna / Returns: float — índice de calor / heat index
        """
        return round(self.temperatura + (self.humedad * 0.1), 1)

    def calcular_probabilidad_lluvia(self):
        """
        Método de negocio: estima la probabilidad de lluvia.
        Business method: estimates rain probability.
        Retorna / Returns: tuple (float prob, str nivel)
        """
        prob  = (self.humedad * 0.6) + (20 * 0.4)   # nubosidad asumida 20%
        nivel = "Alta / High" if prob >= 70 else ("Media / Medium" if prob >= 40 else "Baja / Low")
        return round(prob, 1), nivel

    def clasificar_temperatura(self):
        """
        Método de negocio: clasifica la temperatura en categoría textual.
        Business method: classifies temperature into text category.
        Se usa en el corte de control / Used in control break report.
        Retorna / Returns: str — categoría / category
        """
        if self.temperatura >= 30:
            return "Caluroso / Hot"
        elif self.temperatura >= 20:
            return "Templado / Warm"
        elif self.temperatura >= 10:
            return "Fresco / Cool"
        else:
            return "Frío / Cold"

    def a_dict(self):
        """
        Convierte el objeto TAD a diccionario para serialización JSON.
        Converts TAD object to dictionary for JSON serialization.
        Retorna / Returns: dict con todos los atributos calculados
        """
        prob, nivel = self.calcular_probabilidad_lluvia()
        return {
            "nombre":        self.nombre,
            "pais":          self.pais,
            "temperatura":   self.temperatura,
            "fahrenheit":    self.calcular_fahrenheit(),
            "humedad":       self.humedad,
            "viento":        self.viento,
            "descripcion":   self.descripcion,
            "indice_calor":  self.calcular_indice_calor(),
            "prob_lluvia":   prob,
            "nivel_lluvia":  nivel,
            "categoria":     self.clasificar_temperatura(),
        }

    def __repr__(self):
        """Representación legible del objeto en consola / Readable object repr."""
        return (f"CiudadTAD('{self.nombre}', {self.pais}, "
                f"{self.temperatura}°C, {self.humedad}% hum)")


def weather_dict_a_tad(weather):
    """
    Convierte un diccionario de clima (de la API) a un objeto CiudadTAD.
    Converts a weather dictionary (from API) to a CiudadTAD object.
    Capa de abstracción: separa acceso a datos de procesamiento.
    Abstraction layer: separates data access from processing.
    Parámetro / Parameter: weather (dict) — datos crudos del clima
    Retorna   / Returns  : CiudadTAD — objeto instanciado
    """
    return CiudadTAD(
        nombre      = weather.get("ciudad",      "Desconocida"),
        pais        = weather.get("pais",         ""),
        temperatura = weather.get("temp",          0),
        humedad     = weather.get("humedad",       0),
        viento      = weather.get("viento",        0),
        descripcion = weather.get("descripcion",  ""),
    )


def guardar_maestro_ciudades():
    """
    ACTIVIDAD 9 — Apareo paso 1:
    Genera el archivo maestro ciudades_maestro.txt desde el diccionario
    CIUDADES precargado. Es la fuente de datos "maestra" para el apareo.

    Activity 9 — Matching step 1:
    Generates master file ciudades_maestro.txt from preloaded CIUDADES dict.
    It is the "master" data source for matching.

    Formato de cada línea / Line format:
        ciudad,pais,lat,lon,temp,humedad
    Usa / Uses: with open(), mode 'w', encoding='utf-8'
    """
    try:
        with open(MAESTRO_CIUDADES_TXT, "w", encoding="utf-8") as archivo:
            archivo.write("ciudad,pais,lat,lon,temp,humedad\n")
            for clave, datos in CIUDADES.items():
                linea = (f"{datos['nombre']},{datos['pais']},"
                         f"{datos['lat']},{datos['lon']},"
                         f"{datos['temp']},{datos['humedad']}\n")
                archivo.write(linea)
        registrar_evento_log(f"Maestro generado / Master generated: {MAESTRO_CIUDADES_TXT}")
    except Exception as e:
        registrar_evento_log(f"Error generando maestro / Error generating master: {e}")


def aparear_historial_con_maestro():
    """
    ACTIVIDAD 9 — Lógica de Apareo:
    Lee historial.csv (novedades) y ciudades_maestro.txt (maestro).
    Cruza ambos archivos por la clave común "ciudad".
    Para cada búsqueda del historial, instancia un CiudadTAD con los datos
    del maestro y calcula métricas adicionales.

    Activity 9 — Matching Logic:
    Reads historial.csv (transactions) and ciudades_maestro.txt (master).
    Crosses both files by the common key "ciudad".
    For each history search, instantiates a CiudadTAD with master data
    and calculates additional metrics.

    Retorna / Returns: list[dict] — registros apareados / matched records
    Validación / Validation: FileNotFoundError si algún archivo no existe
    """
    registros_apareados = []   # list[dict] — resultado del apareo

    try:
        # ── Leer archivo maestro / Read master file ──
        # Capa de acceso a datos: solo lectura, sin procesamiento aquí
        # Data access layer: read only, no processing here
        maestro = {}
        with open(MAESTRO_CIUDADES_TXT, "r", encoding="utf-8") as f_maestro:
            lector = csv.DictReader(f_maestro)
            for fila in lector:
                # Clave de apareo: nombre de ciudad estandarizado
                # Matching key: standardized city name
                clave = estandarizar_texto(fila["ciudad"])
                maestro[clave] = fila   # dict con lat, lon, temp, humedad

        # ── Leer archivo de novedades (historial) / Read transactions ──
        with open(HISTORIAL_CSV, "r", encoding="utf-8", newline="") as f_hist:
            lector_hist = csv.DictReader(f_hist)

            for fila_hist in lector_hist:
                clave_hist = estandarizar_texto(fila_hist["ciudad"])

                # APAREO: buscar la ciudad del historial en el maestro
                # MATCHING: find history city in master file
                if clave_hist in maestro:
                    datos_maestro = maestro[clave_hist]

                    # Instanciar CiudadTAD con datos del maestro
                    # Instantiate CiudadTAD with master data
                    ciudad_obj = CiudadTAD(
                        nombre      = datos_maestro["ciudad"],
                        pais        = datos_maestro["pais"],
                        temperatura = float(datos_maestro["temp"]),
                        humedad     = int(datos_maestro["humedad"]),
                        viento      = float(fila_hist.get("viento", 0)),
                        descripcion = fila_hist.get("descripcion", ""),
                    )

                    # Combinar datos del historial con métricas del TAD
                    # Combine history data with TAD metrics
                    registro = {
                        "ciudad":       ciudad_obj.nombre,
                        "pais":         ciudad_obj.pais,
                        "temperatura":  ciudad_obj.temperatura,
                        "fahrenheit":   ciudad_obj.calcular_fahrenheit(),
                        "indice_calor": ciudad_obj.calcular_indice_calor(),
                        "categoria":    ciudad_obj.clasificar_temperatura(),
                        "fecha":        fila_hist.get("fecha", ""),
                        "hora":         fila_hist.get("hora", ""),
                        "apareado":     True,
                    }
                else:
                    # Ciudad en historial pero no en maestro — registrar igual
                    # City in history but not in master — record anyway
                    registro = {
                        "ciudad":      fila_hist["ciudad"],
                        "pais":        fila_hist.get("pais", ""),
                        "temperatura": fila_hist.get("temp", ""),
                        "categoria":   "Sin clasificar / Unclassified",
                        "fecha":       fila_hist.get("fecha", ""),
                        "hora":        fila_hist.get("hora", ""),
                        "apareado":    False,
                    }

                registros_apareados.append(registro)

    except FileNotFoundError as e:
        # Validación robusta: informa qué archivo falta
        # Robust validation: reports which file is missing
        registrar_evento_log(f"Archivo no encontrado en apareo / File not found in matching: {e}")
        return []
    except Exception as e:
        registrar_evento_log(f"Error en apareo / Matching error: {e}")
        return []

    registrar_evento_log(f"Apareo completado: {len(registros_apareados)} registros / Matching complete")
    return registros_apareados


def generar_reporte_corte():
    """
    ACTIVIDAD 9 — Corte de Control:
    Agrupa los registros apareados por categoría de temperatura y
    calcula el total de búsquedas y temperatura promedio por categoría.
    Esto es un "corte de control": cada cambio de categoría genera
    un subtotal y se imprime el resumen completo al final.

    Activity 9 — Control Break:
    Groups matched records by temperature category and calculates
    total searches and average temperature per category.
    This is a "control break": each category change generates
    a subtotal and the full summary is printed at the end.

    Retorna / Returns: list[dict] — resumen por categoría / summary by category
    """
    registros = aparear_historial_con_maestro()

    if not registros:
        return []

    # Agrupar por categoría de temperatura / Group by temperature category
    # Usamos un diccionario como acumulador / Use a dict as accumulator
    grupos = {}   # dict[str, dict] — categoría → acumulador

    for reg in registros:
        cat   = reg.get("categoria", "Sin categoría")
        temp  = reg.get("temperatura", 0)

        # Crear grupo si no existe / Create group if not exists
        if cat not in grupos:
            grupos[cat] = {
                "categoria":  cat,
                "total":      0,        # int — total de búsquedas / total searches
                "suma_temps": 0.0,      # float — suma de temperaturas / temp sum
                "ciudades":   [],       # list[str] — ciudades del grupo / group cities
            }

        # Acumular datos del registro / Accumulate record data
        grupos[cat]["total"]      += 1
        try:
            grupos[cat]["suma_temps"] += float(temp)
        except (ValueError, TypeError):
            pass
        grupos[cat]["ciudades"].append(reg.get("ciudad", ""))

    # Calcular promedio por categoría (corte de control)
    # Calculate average per category (control break)
    reporte = []
    for cat, datos in sorted(grupos.items()):
        promedio = (datos["suma_temps"] / datos["total"]
                    if datos["total"] > 0 else 0)
        reporte.append({
            "categoria":         datos["categoria"],
            "total_busquedas":   datos["total"],
            "temp_promedio":     round(promedio, 1),
            "ciudades_unicas":   list(set(datos["ciudades"])),
        })

    return reporte


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

    # f-strings con modificadores de ancho :<EW (alinea izquierda) y :>VW (alinea derecha)
    # f-strings with width modifiers :<EW (left-align) and :>VW (right-align)
    sep      = "─" * (EW + VW + 4)
    ciudad   = f"{c['ciudad']}, {c['pais']}"
    temp     = f"{c['temp']}°C"
    sens     = f"{c['sensacion']}°C"
    hum      = f"{c['humedad']}%"
    viento   = f"{c['viento']} km/h"
    vis      = f"{c['visibilidad']} km"
    nub      = f"{c['nubosidad']}%"
    desc     = c['descripcion']

    lineas = [
        sep,
        f"  {'REPORTE DE CLIMA / WEATHER REPORT':^{EW + VW}}",
        sep,
        f"  {'Ciudad / City':<{EW}} {ciudad:>{VW}}",
        f"  {'Temperatura / Temperature':<{EW}} {temp:>{VW}}",
        f"  {'Sensación / Feels Like':<{EW}} {sens:>{VW}}",
        f"  {'Humedad / Humidity':<{EW}} {hum:>{VW}}",
        f"  {'Viento / Wind':<{EW}} {viento:>{VW}}",
        f"  {'Visibilidad / Visibility':<{EW}} {vis:>{VW}}",
        f"  {'Nubosidad / Cloudiness':<{EW}} {nub:>{VW}}",
        f"  {'Condición / Condition':<{EW}} {desc:>{VW}}",
        sep,
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

    # ACTIVIDAD 8 — Guardar búsqueda exitosa en historial.csv
    # ACTIVITY 8 — Save successful search to historial.csv
    guardar_busqueda_csv(weather)

    # ACTIVIDAD 9 — Instanciar objeto CiudadTAD con los datos obtenidos
    # ACTIVITY 9 — Instantiate CiudadTAD object with obtained data
    # Ya no usamos el diccionario suelto en el flujo — usamos el TAD
    # We no longer use the loose dictionary in the flow — we use the TAD
    ciudad_tad = weather_dict_a_tad(weather)
    registrar_evento_log(f"TAD instanciado / TAD instantiated: {ciudad_tad!r}")

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


@app.route("/api/tad/<ciudad>")
def api_tad(ciudad):
    """
    ACTIVIDAD 9 — Endpoint TAD:
    Instancia un CiudadTAD desde el diccionario CIUDADES y retorna
    todos sus atributos y métricas calculadas como JSON.
    Demuestra el uso del TAD en lugar de diccionarios sueltos.

    Activity 9 — TAD Endpoint:
    Instantiates a CiudadTAD from CIUDADES dict and returns
    all its attributes and calculated metrics as JSON.
    Demonstrates TAD usage instead of loose dictionaries.
    """
    clave = estandarizar_texto(ciudad)
    datos = buscar_ciudad_catalogo(clave, CIUDADES)

    if not datos:
        return jsonify({"error": f"Ciudad '{ciudad}' no en el catálogo / not in catalog"}), 404

    # Instanciar el TAD / Instantiate the TAD
    obj = CiudadTAD(
        nombre      = datos["nombre"],
        pais        = datos["pais"],
        temperatura = datos["temp"],
        humedad     = datos["humedad"],
        viento      = datos["viento"],
        descripcion = datos["descripcion"],
    )

    return jsonify({"tad": obj.a_dict(), "repr": repr(obj)})


@app.route("/api/apareo")
def api_apareo():
    """
    ACTIVIDAD 9 — Endpoint Apareo:
    Ejecuta el apareo entre historial.csv y ciudades_maestro.txt
    y retorna los registros cruzados con métricas del TAD.

    Activity 9 — Matching Endpoint:
    Runs matching between historial.csv and ciudades_maestro.txt
    and returns crossed records with TAD metrics.
    """
    registros = aparear_historial_con_maestro()
    return jsonify({
        "apareo":  registros,
        "total":   len(registros),
        "fuentes": [HISTORIAL_CSV, MAESTRO_CIUDADES_TXT],
    })


@app.route("/api/reporte-corte")
def api_reporte_corte():
    """
    ACTIVIDAD 9 — Endpoint Corte de Control:
    Agrupa el historial por categoría de temperatura y retorna
    el total de búsquedas y temperatura promedio por categoría.

    Activity 9 — Control Break Endpoint:
    Groups history by temperature category and returns
    total searches and average temperature per category.
    """
    reporte = generar_reporte_corte()
    return jsonify({"reporte_corte": reporte, "categorias": len(reporte)})


# ==============================================================
# PUNTO DE ENTRADA / ENTRY POINT
    """
    ACTIVIDAD 8 — Endpoint que expone el historial cargado desde CSV.
    Activity 8 — Endpoint that exposes history loaded from CSV.
    Retorna / Returns: JSON con los últimos 10 registros del historial.
    """
    registros = obtener_historial_reciente(10)
    return jsonify({"historial": registros, "total": len(historial_busquedas)})


@app.route("/api/log")
def api_log():
    """
    ACTIVIDAD 8 — Endpoint que expone el contenido del log_sistema.txt.
    Activity 8 — Endpoint that exposes log_sistema.txt content.
    """
    lineas = leer_log()
    return jsonify({"log": [l.rstrip() for l in lineas], "archivo": LOG_FILE})


# ==============================================================
# PUNTO DE ENTRADA / ENTRY POINT
# ==============================================================
# ACTIVIDAD 8 — Al iniciar, se ejecutan los módulos de persistencia:
# 1. inicializar_log()      → crea/actualiza log_sistema.txt
# 2. leer_log()             → lee y muestra el log en consola
# 3. cargar_historial_csv() → carga búsquedas previas en memoria
# ==============================================================

if __name__ == "__main__":
    # Paso 1: Inicializar y escribir en log_sistema.txt
    inicializar_log()

    # Paso 2: Leer el log y mostrarlo en consola
    leer_log()

    # Paso 3: Cargar historial previo desde CSV al iniciar
    cargar_historial_csv()

    # ACTIVIDAD 9: Generar archivo maestro de ciudades para el apareo
    # ACTIVITY 9: Generate master cities file for matching
    guardar_maestro_ciudades()

    # Demostrar instanciación del TAD en consola / Demonstrate TAD instantiation
    print("\n── ACTIVIDAD 9: Prueba de instancias CiudadTAD ──")
    tad1 = CiudadTAD("Cucuta",  "CO", 32,   78, 14.4, "Cielo despejado")
    tad2 = CiudadTAD("Bogota",  "CO", 14,   85, 10.8, "Parcialmente nublado")
    print(f"Objeto 1: {tad1!r}")
    print(f"  → Fahrenheit   : {tad1.calcular_fahrenheit()}°F")
    print(f"  → Índice calor : {tad1.calcular_indice_calor()}")
    print(f"  → Categoría    : {tad1.clasificar_temperatura()}")
    print(f"Objeto 2: {tad2!r}")
    print(f"  → Fahrenheit   : {tad2.calcular_fahrenheit()}°F")
    print(f"  → Índice calor : {tad2.calcular_indice_calor()}")
    print(f"  → Categoría    : {tad2.clasificar_temperatura()}")
    print("──────────────────────────────────────────────────\n")

    app.run(debug=True, port=5000)
