import app
from flask import Blueprint, render_template
from .poblacional import obtener_analisis_poblacional
from app.logic.relacional import obtener_matriz_relacional_categoria_municipio, obtener_diversidad_por_municipio

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route('/api/relacional')
def api_relacional():
    datos_matriz = obtener_matriz_relacional_categoria_municipio()
    datos_diversidad = obtener_diversidad_por_municipio()
    return {
        "matriz": datos_matriz,
        "diversidad": datos_diversidad
    }
@main.route('/relacional')
def vista_relacional():
    return render_template('relacional.html')