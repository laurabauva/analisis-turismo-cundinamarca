import pandas as pd
import os

def obtener_ruta_csv():
    """Retorna la ruta absoluta al CSV en la carpeta data/."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base_dir, 'data', 'rnt_cundinamarca.csv')

def cargar_y_limpiar_datos():
    """Carga el dataset y elimina datos personales/identificadores sensibles."""
    ruta = obtener_ruta_csv()
    if not os.path.exists(ruta):
        # En caso de que el archivo tenga otro nombre dentro de data/
        files = [f for f in os.listdir(os.path.join(os.path.dirname(ruta))) if f.endswith('.csv')]
        if files:
            ruta = os.path.join(os.path.dirname(ruta), files[0])
            
    df = pd.read_csv(ruta)
    
    # Eliminación de columnas con datos personales o sensibles según el README
    cols_sensibles = ['RAZON_SOCIAL', 'NIT', 'CODIGO_RNT', 'razon_social', 'nit', 'codigo_rnt']
    df = df.drop(columns=[col for col in cols_sensibles if col in df.columns])
    return df

def obtener_matriz_relacional_categoria_municipio(top_muni=8, top_cat=5):
    """
    Relaciona las principales categorías de turismo con los municipios de mayor registro.
    """
    df = cargar_y_limpiar_datos()
    
    # Identificar columna de municipio y categoría (independiente de mayúsculas/minúsculas)
    col_muni = next((c for c in df.columns if 'muni' in c.lower()), 'MUNICIPIO')
    col_cat = next((c for c in df.columns if 'cat' in c.lower() or 'tipo' in c.lower()), 'CATEGORIA')
    
    muni_top = df[col_muni].value_counts().head(top_muni).index
    cat_top = df[col_cat].value_counts().head(top_cat).index
    
    df_sub = df[(df[col_muni].isin(muni_top)) & (df[col_cat].isin(cat_top))]
    matriz = pd.crosstab(df_sub[col_muni], df_sub[col_cat])
    
    return {
        "municipios": matriz.index.tolist(),
        "categorias": matriz.columns.tolist(),
        "matriz": matriz.values.tolist()
    }

def obtener_diversidad_por_municipio():
    """Calcula la variedad de categorías registradas por cada municipio."""
    df = cargar_y_limpiar_datos()
    col_muni = next((c for c in df.columns if 'muni' in c.lower()), 'MUNICIPIO')
    col_cat = next((c for c in df.columns if 'cat' in c.lower() or 'tipo' in c.lower()), 'CATEGORIA')
    
    diversidad = df.groupby(col_muni)[col_cat].nunique().reset_index()
    diversidad.columns = ['municipio', 'variedad_servicios']
    diversidad = diversidad.sort_values(by='variedad_servicios', ascending=False)
    return diversidad.head(10).to_dict(orient='records')