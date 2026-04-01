# ==========================================================
# Proyecto: Atmosfera — Sistema de Clima con IA
# Autor: Jonathan
# Descripción: Sistema web que muestra el clima de una ciudad
#              y genera recomendaciones usando inteligencia artificial.
# ==========================================================

from flask import Flask, render_template

app = Flask(__name__)


# ==========================================================
# ACTIVIDAD 1 — VARIABLES INICIALES
# Declaración de variables con valores de ejemplo
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
recomendacion    = "Usa ropa ligera y bebe suficiente agua hoy."  # str — recomendación generada


# ==========================================================
# ACTIVIDAD 1 — OPERACIONES BÁSICAS
# Cálculos con sentido dentro del proyecto
# ==========================================================

# Convertir temperatura de °C a °F / Convert temperature from °C to °F
temperatura_fahrenheit = (temperatura * 9 / 5) + 32

# Calcular índice de calor aproximado (temperatura + factor humedad)
# Approximate heat index (temperature + humidity factor)
indice_calor = temperatura + (humedad * 0.1)

# Calcular diferencia entre temperatura real y sensación térmica
# Difference between real temperature and feels-like
diferencia_sensacion = round(sensacion - temperatura, 1)


# ==========================================================
# ACTIVIDAD 1 — RUTA PRINCIPAL / MAIN ROUTE
# Envía todas las variables a la plantilla HTML para mostrarlas en la web
# ==========================================================

@app.route("/")
def index():
    return render_template("index.html",
        ciudad                 = ciudad,
        pais                   = pais,
        temperatura            = temperatura,
        temperatura_fahrenheit = temperatura_fahrenheit,
        sensacion              = sensacion,
        diferencia_sensacion   = diferencia_sensacion,
        indice_calor           = round(indice_calor, 1),
        humedad                = humedad,
        velocidad_viento       = velocidad_viento,
        visibilidad            = visibilidad,
        nubosidad              = nubosidad,
        recomendacion          = recomendacion,
    )


# ==========================================================
# PUNTO DE ENTRADA / ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
