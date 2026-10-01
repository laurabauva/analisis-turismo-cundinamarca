from flask import Flask, render_template, request
import pandas as pd
from pathlib import Path

app = Flask(__name__)

# =====================================
# CONFIGURACIÓN DE RUTAS DEL PROYECTO
# =====================================
BASE_DIR = Path(__file__).resolve().parent
RUTA_DATOS = BASE_DIR / 'data' / 'rnt_cundinamarca.csv'


# =====================================
# CARGA Y LIMPIEZA DEL DATASET
# =====================================
def cargar_datos():
    df = pd.read_csv(
        RUTA_DATOS,
        sep=';',
        encoding='latin-1',
        on_bad_lines='skip',
        dtype={
            'CODIGO_DEPARTAMENTO': str,
            'CODIGO_MUNICIPIO': str
        }
    )
    df.columns = [c.strip().upper() for c in df.columns]
    df = df.dropna(subset=['DEPARTAMENTO', 'MUNICIPIO'])
    df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.strip().str.upper()
    df['MUNICIPIO']    = df['MUNICIPIO'].str.strip().str.upper()
    return df


# =====================================
# INICIO
# =====================================
@app.route('/')
def index():
    return render_template('index.html')


# =====================================
# DIMENSIÓN POBLACIONAL  (Integrante 1)
# =====================================
@app.route('/poblacional')
def poblacional():
    # ⚠️ El Integrante 1 debe completar este diccionario "datos"
    # con lo que su plantilla poblacional.html espera.
    # Dejamos un placeholder mínimo para que no explote.

    df = cargar_datos()

    categorias_count = df['CATEGORIA'].value_counts()
    subcategorias_count = df['SUB_CATEGORIA'].value_counts()

    total = len(df)

    categoria_principal = categorias_count.index[0] if total else '—'
    cantidad_categoria_principal = int(categorias_count.iloc[0]) if total else 0
    porcentaje_categoria_principal = round(
        cantidad_categoria_principal / total * 100, 2
    ) if total else 0

    datos = {
        "total_registros": total,
        "total_categorias": df['CATEGORIA'].nunique(),
        "categoria_principal": categoria_principal,
        "cantidad_categoria_principal": cantidad_categoria_principal,
        "porcentaje_categoria_principal": porcentaje_categoria_principal,

        # listas para las gráficas (Chart.js)
        "categorias": [
            {"categoria": cat, "cantidad": int(cant),
             "porcentaje": round(cant / total * 100, 2)}
            for cat, cant in categorias_count.items()
        ],
        "subcategorias": [
            {"subcategoria": sub, "cantidad": int(cant)}
            for sub, cant in subcategorias_count.head(10).items()
        ],
    }

    return render_template('poblacional.html', datos=datos)


# =====================================
# DIMENSIÓN TERRITORIAL  (Integrante 2 - TÚ)
# =====================================
@app.route('/territorial')
def territorial():

    df = cargar_datos()

    # --- Filtros interactivos (query params) ---
    depto_sel = request.args.get('departamento', 'TODOS')
    cat_sel   = request.args.get('categoria', 'TODAS')

    df_filtrado = df.copy()
    if depto_sel != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['DEPARTAMENTO'] == depto_sel]
    if cat_sel != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['CATEGORIA'] == cat_sel]

    total = len(df_filtrado)

    # --- Indicadores ---
    por_municipio = df_filtrado['MUNICIPIO'].value_counts()

    municipio_top    = por_municipio.index[0] if total else '—'
    cantidad_top     = int(por_municipio.iloc[0]) if total else 0
    porcentaje_top   = round(cantidad_top / total * 100, 2) if total else 0

    top3             = int(por_municipio.head(3).sum())
    concentracion_top3 = round(top3 / total * 100, 2) if total else 0

    por_depto = df_filtrado['DEPARTAMENTO'].value_counts()

    # --- Datos para gráficas ---
    top10 = por_municipio.head(10)
    municipios_grafica = [
        {"municipio": m, "cantidad": int(c),
         "porcentaje": round(c / total * 100, 2)}
        for m, c in top10.items()
    ]

    deptos_grafica = [
        {"departamento": d, "cantidad": int(c),
         "porcentaje": round(c / total * 100, 2)}
        for d, c in por_depto.items()
    ]

    top8_muns = por_municipio.head(8).index.tolist()
    cruce = (
        df_filtrado[df_filtrado['MUNICIPIO'].isin(top8_muns)]
        .groupby(['MUNICIPIO', 'CATEGORIA'])
        .size()
        .reset_index(name='cantidad')
    )

    categorias_unicas = cruce['CATEGORIA'].unique().tolist()

    datos_cruce = {
        cat: [
            int(cruce[(cruce['MUNICIPIO'] == m) &
                      (cruce['CATEGORIA'] == cat)]['cantidad'].sum())
            for m in top8_muns
        ]
        for cat in categorias_unicas
    }

    # --- Listas para los <select> de filtros ---
    departamentos = sorted(df['DEPARTAMENTO'].dropna().unique().tolist())
    categorias    = sorted(df['CATEGORIA'].dropna().unique().tolist())

    # --- Diccionario que consume territorial.html ---
    datos = {
        "total_registros": total,
        "municipio_top": municipio_top,
        "cantidad_municipio_top": cantidad_top,
        "porcentaje_municipio_top": porcentaje_top,
        "concentracion_top3": concentracion_top3,
        "participacion_depto": {
            k: round(v / total * 100, 2) for k, v in por_depto.items()
        } if total else {},
        "municipios_grafica": municipios_grafica,
        "deptos_grafica": deptos_grafica,
        "municipios_cruce": top8_muns,
        "categorias_unicas": categorias_unicas,
        "datos_cruce": datos_cruce,
    }

    return render_template(
        'territorial.html',
        datos=datos,
        departamentos=departamentos,
        categorias=categorias,
        filtro_dep=depto_sel,
        filtro_cat=cat_sel
    )


# =====================================
# DIMENSIÓN TEMPORAL  (Integrante 3)
# =====================================
@app.route('/temporal')
def temporal():
    # ⚠️ El Integrante 3 debe completar esta ruta.
    # Por ahora solo renderiza la plantilla.
    return render_template('temporal.html')


# =====================================
# DIMENSIÓN MULTIVARIADA  (Integrante 4)
# =====================================
@app.route('/multivariada')
def multivariada():
    # ⚠️ El Integrante 4 debe completar esta ruta.
    # Por ahora solo renderiza la plantilla.
    return render_template('multivariada.html')


# =====================================
# EJECUCIÓN
# =====================================
if __name__ == '__main__':
    app.run(debug=True)