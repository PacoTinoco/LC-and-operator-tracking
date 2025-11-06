import pandas as pd
import os

# Función para asignar operadores y coordinadores
def asignar_operadores(df_indicadores, df_asignacion):
    df_asignacion['Fecha_Inicio'] = pd.to_datetime(df_asignacion['Fecha_Inicio'], errors='coerce')
    df_asignacion['Fecha_Fin'] = pd.to_datetime(df_asignacion['Fecha_Fin'], errors='coerce')

    df_indicadores['Operador'] = None
    df_indicadores['Coordinador'] = None

    for _, row in df_asignacion.iterrows():
        mask = (
            (df_indicadores['Fecha'] >= row['Fecha_Inicio']) &
            (df_indicadores['Fecha'] <= row['Fecha_Fin']) &
            (df_indicadores['Turno'] == row['Turno']) &
            (df_indicadores['Maquina'] == row['Maquina'])
        )
        df_indicadores.loc[mask, 'Operador'] = row['Operador']
        df_indicadores.loc[mask, 'Coordinador'] = row['Coordinador']

    # Filtrar solo las filas que tienen asignación válida
    df_asignado = df_indicadores[df_indicadores['Coordinador'].notna() & df_indicadores['Operador'].notna()].copy()
    return df_asignado

# Intentar cargar archivo de asignación en formato Excel o CSV
asignacion_path_xlsx = 'data/operators_assignments.xlsx'
asignacion_path_csv = 'data/operators_assignments.csv'

if os.path.exists(asignacion_path_xlsx):
    df_asignacion = pd.read_excel(asignacion_path_xlsx, engine='openpyxl')
elif os.path.exists(asignacion_path_csv):
    df_asignacion = pd.read_csv(asignacion_path_csv)
else:
    raise FileNotFoundError("No se encontró el archivo de asignación en formato .xlsx o .csv")

# Mostrar columnas cargadas para verificación
print("Columnas del archivo de asignación:", df_asignacion.columns.tolist())