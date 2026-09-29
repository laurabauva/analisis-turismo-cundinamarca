from flask import Blueprint, render_template

from .poblacional import obtener_analisis_poblacional

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/dimension-poblacional")
def dimension_poblacional():
    datos = obtener_analisis_poblacional()
    return render_template(
        "dimension_poblacional.html",
        datos=datos
    )
