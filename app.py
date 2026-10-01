from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

def cargar_datos():
    df = pd.read_csv(
        'data/rnt_cundinamarca.csv',
        sep=';',
        encoding='latin-1',
        on_bad_lines='skip',
        dtype={'CODIGO_DEPARTAMENTO': str, 'CODIGO_MUNICIPIO': str}
    )
    df.columns = [c.strip().upper() for c in df.columns]
    df = df.dropna(subset=['DEPARTAMENTO', 'MUNICIPIO'])
    df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.strip().str.upper()
    df['MUNICIPIO']    = df['MUNICIPIO'].str.strip().str.upper()
    return df


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/poblacional')
def poblacional():
    # lo llena el Integrante 1
    return render_template('poblacional.html')


@app.route('/territorial')     # ← TU DIMENSIÓN
def territorial():
    ...


@app.route('/temporal')
def temporal():
    # lo llena el Integrante 3
    return render_template('temporal.html')


@app.route('/multivariada')
def multivariada():
    # lo llena el Integrante 4
    return render_template('multivariada.html')


if __name__ == '__main__':
    app.run(debug=True)