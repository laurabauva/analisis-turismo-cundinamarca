   # Análisis de prestadores de servicios turísticos en Cundinamarca

   Análisis exploratorio con Python, Flask y Bootstrap.

   ## Conjunto de datos
   - Nombre: Registro Nacional de Turismo - RNT (filtrado por Cundinamarca)
   - Entidad: Ministerio de Comercio, Industria y Turismo (MinCIT)
   - URL: https://www.datos.gov.co/Comercio-Industria-y-Turismo/Registro-Nacional-de-Turismo-RNT/thwd-ivmp
   - Nota: se eliminaron las columnas de razón social, NIT y código RNT para no incluir datos personales.


## Cómo ejecutar localmente

1. Clonar el repositorio
2. Crear entorno virtual:
   python -m venv venv
3. Activar:
   venv\Scripts\activate
4. Instalar dependencias:
   pip install -r requirements.txt
5. Ejecutar:
   python app.py
6. Abrir http://127.0.0.1:5000


   ## Integrantes
   1. Laura Bautista: dimensión poblacional y administración del repositorio
   2. Nicolás Gutiérrez: dimensión territorial y configuración de Flask
   3. Leonardo Moscoso: dimensión temporal y publicación
   4. Andrés Pineda: dimensión relacional y informe
