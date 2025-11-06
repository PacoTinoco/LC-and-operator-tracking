import pandas as pd
import re

# Lista de nombres válidos para los indicadores
INDICADORES_VALIDOS = ['MTBF', 'Reject Rate', 'Strategic PR', 'UPDT Categories']

# Validar nombre del archivo
def validar_nombre_archivo(nombre_archivo):
    nombre_archivo = nombre_archivo.lower().replace(".xlsx", "").replace(".csv", "")
    for indicador in INDICADORES_VALIDOS:
        nombre_base = indicador.lower().replace(" ", "_")
        if nombre_base in nombre_archivo.replace(" ", "_"):
            return indicador
    return None

# Procesar columna Shift
def procesar_shift(df):
    df[['Turno', 'Fecha_str']] = df['Shift'].str.extract(r'(S\d)\s+(\d{2}-\d{2}-\d{4})')
    df['Fecha'] = pd.to_datetime(df['Fecha_str'], format='%d-%m-%Y', errors='coerce')
    df['Día'] = df['Fecha'].dt.day
    df['Mes'] = df['Fecha'].dt.month
    df['Año'] = df['Fecha'].dt.year
    df['Semana'] = df['Fecha'].dt.isocalendar().week
    df['Día_semana'] = df['Fecha'].dt.day_name()
    return df

# Limpiar UPDT
def limpiar_updt(df):
    columnas_updt = [col for col in df.columns if re.match(r'\d{3}', str(col))]
    df_updt = df.copy()
    for col in columnas_updt:
        df_updt[col] = pd.to_numeric(df_updt[col], errors='coerce')
        df_updt[col] = df_updt[col].apply(lambda x: x if x <= 50 else 0)
    df_updt['UPDT_Total'] = df_updt[columnas_updt].sum(axis=1)
    return df_updt

# Función principal de limpieza
def limpiar_datos(archivo):
    nombre_archivo = archivo.name
    indicador = validar_nombre_archivo(nombre_archivo)

    if not indicador:
        raise ValueError("Nombre de archivo no válido. Usa nombres como 'MTBF.xlsx', 'Reject_Rate.csv', etc.")

    # Leer archivo desde la fila 3 (index 2)
    if nombre_archivo.endswith('.xlsx'):
        df = pd.read_excel(archivo, skiprows=2, engine='openpyxl')
    elif nombre_archivo.endswith('.csv'):
        df = pd.read_csv(archivo, skiprows=2)
    else:
        raise ValueError("Formato de archivo no soportado. Usa .xlsx o .csv")

    # Validar columna Shift
    if 'Shift' not in df.columns:
        raise ValueError("El archivo no contiene la columna 'Shift'.")

    # Validar columna del indicador
    if indicador == 'UPDT Categories':
        columnas_updt = [col for col in df.columns if re.match(r'\d{3}', str(col))]
        if not columnas_updt:
            raise ValueError("El archivo UPDT no contiene columnas válidas como '300', '301', etc.")
    else:
        if indicador not in df.columns:
            raise ValueError(f"El archivo no contiene la columna del indicador '{indicador}'.")

    # Procesar Shift
    df = procesar_shift(df)

    # Procesar UPDT si aplica
    if indicador == 'UPDT Categories':
        df = limpiar_updt(df)

    return df, indicador