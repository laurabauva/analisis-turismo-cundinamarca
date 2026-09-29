import pandas as pd

DATA_PATH = "data/rnt_cundinamarca.csv"


def cargar_datos():
    return pd.read_csv(
        DATA_PATH,
        sep=";",
        encoding="latin1"
    )


def obtener_analisis_poblacional():
    df = cargar_datos()

    total_registros = len(df)

    categorias = (
        df["CATEGORIA"]
        .value_counts()
        .reset_index()
    )
    categorias.columns = ["categoria", "cantidad"]

    categorias["porcentaje"] = (
        categorias["cantidad"] / total_registros * 100
    ).round(2)

    subcategorias = (
        df["SUB_CATEGORIA"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    subcategorias.columns = ["subcategoria", "cantidad"]

    categoria_principal = categorias.iloc[0]

    return {
        "total_registros": total_registros,
        "total_categorias": df["CATEGORIA"].nunique(),
        "categoria_principal": categoria_principal["categoria"],
        "cantidad_categoria_principal": int(categoria_principal["cantidad"]),
        "porcentaje_categoria_principal": float(
            categoria_principal["porcentaje"]
        ),
        "categorias": categorias.to_dict("records"),
        "subcategorias": subcategorias.to_dict("records")
    }
