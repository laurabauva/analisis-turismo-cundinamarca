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
    cantidad_menor   = int(por_municipio.min()) if total else 0
    municipios_menor = (
        por_municipio[por_municipio == cantidad_menor].index.tolist()
        if total else []
    )
    municipio_menor = municipios_menor[0] if municipios_menor else '—'
    territorios = int(por_municipio.size)
    promedio_municipio = round(total / territorios, 2) if territorios else 0
    brecha_registros = cantidad_top - cantidad_menor

    top3             = int(por_municipio.head(3).sum())
    concentracion_top3 = round(top3 / total * 100, 2) if total else 0

    por_depto = df_filtrado['DEPARTAMENTO'].value_counts()
    departamento_top = por_depto.index[0] if total else '—'
    porcentaje_depto_top = round(int(por_depto.iloc[0]) / total * 100, 2) if total else 0

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
    municipios_tabla = []
    for municipio, cantidad in top10.items():
        categorias_municipio = (
            df_filtrado[df_filtrado['MUNICIPIO'] == municipio]['CATEGORIA']
            .value_counts()
        )
        municipios_tabla.append({
            "municipio": municipio,
            "cantidad": int(cantidad),
            "porcentaje": round(cantidad / total * 100, 2) if total else 0,
            "categoria": categorias_municipio.index[0] if len(categorias_municipio) else '—'
        })
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
        "municipio_menor": municipio_menor,
        "cantidad_municipio_menor": cantidad_menor,
        "municipios_menor": municipios_menor,
        "territorios": territorios,
        "promedio_municipio": promedio_municipio,
        "brecha_registros": brecha_registros,
        "hay_datos": bool(total),
        "concentracion_top3": concentracion_top3,
        "departamento_top": departamento_top,
        "porcentaje_depto_top": porcentaje_depto_top,
        "participacion_depto": {
            k: round(v / total * 100, 2) for k, v in por_depto.items()
        } if total else {},
        "municipios_grafica": municipios_grafica,
        "municipios_tabla": municipios_tabla,
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
# DIMENSIÓN TEMPORAL  Cristian Moscoso Integrante 3
# =====================================
@app.route('/temporal')
def temporal():
    df = cargar_datos()
    df = df.copy()
    df['ANIO'] = pd.to_numeric(df['ANIO'], errors='coerce')
    df = df.dropna(subset=['ANIO']).copy()
    df['ANIO'] = df['ANIO'].astype(int)

    if df.empty:
        datos = {
            'anio_max': '—',
            'anio_min': '—',
            'anio_max_total': 0,
            'anio_min_total': 0,
            'promedio_anual': 0,
            'variacion_total': 0,
            'tendencia': 'No hay datos para analizar en el rango disponible.',
            'resumen': 'No se encontraron registros con año válido para construir la línea de tiempo.',
            'conclusion': 'El conjunto de datos no presenta información suficiente para describir cambios temporales.',
            'evolucion': [],
            'variacion': [],
            'top_categorias': [],
            'estado_trend': [],
            'categoria_reciente': []
        }
        return render_template('temporal.html', datos=datos)

    conteo_anual = df.groupby('ANIO').size().sort_index()
    anios = [int(a) for a in conteo_anual.index.tolist()]
    cantidades = [int(v) for v in conteo_anual.values.tolist()]

    anio_max = int(conteo_anual.idxmax())
    anio_max_total = int(conteo_anual.max())
    anio_min = int(conteo_anual.idxmin())
    anio_min_total = int(conteo_anual.min())
    promedio_anual = round(float(conteo_anual.mean()), 1)

    primer_anio = cantidades[0] if cantidades else 0
    ultimo_anio = cantidades[-1] if cantidades else 0
    variacion_total = round(((ultimo_anio - primer_anio) / primer_anio * 100), 1) if primer_anio else 0

    if variacion_total > 0:
        tendencia = f'La actividad creció un {variacion_total}% entre {anios[0]} y {anios[-1]}.'
    elif variacion_total < 0:
        tendencia = f'La actividad cayó un {abs(variacion_total)}% entre {anios[0]} y {anios[-1]}.'
    else:
        tendencia = f'La actividad se mantuvo estable entre {anios[0]} y {anios[-1]}.'

    evolucion = []
    variacion = []
    for i, anio in enumerate(anios):
        cantidad = cantidades[i]
        variacion_periodo = 0
        if i > 0:
            anterior = cantidades[i - 1]
            variacion_periodo = round(((cantidad - anterior) / anterior) * 100, 1) if anterior else 0
        evolucion.append({
            'anio': anio,
            'cantidad': cantidad,
            'porcentaje': round((cantidad / sum(cantidades)) * 100, 2) if sum(cantidades) else 0
        })
        variacion.append({
            'anio': anio,
            'variacion': variacion_periodo
        })

    categorias_total = df['CATEGORIA'].value_counts().head(5)
    top_categorias = [
        {'categoria': cat, 'cantidad': int(cant), 'porcentaje': round((cant / len(df)) * 100, 2) if len(df) else 0}
        for cat, cant in categorias_total.items()
    ]

    categoria_reciente = (
        df[df['ANIO'] == anios[-1]].groupby('CATEGORIA').size().sort_values(ascending=False).head(5)
    )
    categoria_reciente = [
        {'categoria': categoria, 'cantidad': int(cantidad), 'porcentaje': round((cantidad / len(df[df['ANIO'] == anios[-1]])) * 100, 2) if len(df[df['ANIO'] == anios[-1]]) else 0}
        for categoria, cantidad in categoria_reciente.items()
    ]

    estado_trend = [
        {'estado': estado, 'cantidad': int(cantidad)}
        for estado, cantidad in df['ESTADO'].value_counts().items()
    ]

    resumen = (
        f'En el rango analizado, el conjunto registró {sum(cantidades):,} observaciones entre {anios[0]} y {anios[-1]}. '
        f'El año más fuerte fue {anio_max} con {anio_max_total:,} registros, mientras que {anio_min} fue el más bajo con {anio_min_total:,}. '
        f'La media anual fue de {promedio_anual:,.1f} registros por año.'
    )

    conclusion = (
        f'El comportamiento se puede resumir en un crecimiento o ajuste gradual de la actividad turística en el tiempo. '
        f'En la práctica, esto sugiere que la oferta no se mantiene estática: cambia su intensidad según el año, '
        f'lo que puede estar relacionado con la demanda, la apertura de nuevos prestadores o cambios en la forma en que se reporta la actividad.'
    )

    datos = {
        'anio_max': anio_max,
        'anio_min': anio_min,
        'anio_max_total': anio_max_total,
        'anio_min_total': anio_min_total,
        'promedio_anual': promedio_anual,
        'variacion_total': variacion_total,
        'tendencia': tendencia,
        'resumen': resumen,
        'conclusion': conclusion,
        'evolucion': evolucion,
        'variacion': variacion,
        'top_categorias': top_categorias,
        'estado_trend': estado_trend,
        'categoria_reciente': categoria_reciente,
        'anios': anios,
        'cantidades': cantidades,
        'anio_inicial': anios[0],
        'anio_final': anios[-1],
        'total_registros': int(sum(cantidades))
    }

    return render_template('temporal.html', datos=datos)


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