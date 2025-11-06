import pandas as pd

def calcular_promedios(df, indicador):
    """
    Calcula promedios semanales, mensuales y anuales para el indicador dado.
    """
    # Determinar la columna de valores
    if indicador == 'UPDT Categories':
        valor_col = 'UPDT_Total'
    else:
        # Asume que la columna del indicador tiene el mismo nombre
        valor_col = indicador

    # Asegurar que la columna de fecha esté en datetime
    if not pd.api.types.is_datetime64_any_dtype(df['Fecha']):
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

    # Agregar columnas de agrupación
    df['Semana'] = df['Fecha'].dt.isocalendar().week
    df['Mes'] = df['Fecha'].dt.month
    df['Año'] = df['Fecha'].dt.year

    # Agrupaciones
    promedio_semanal = df.groupby(['Año', 'Semana'])[valor_col].mean().reset_index()
    promedio_mensual = df.groupby(['Año', 'Mes'])[valor_col].mean().reset_index()
    promedio_anual = df.groupby(['Año'])[valor_col].mean().reset_index()

    return {
        'semanal': promedio_semanal,
        'mensual': promedio_mensual,
        'anual': promedio_anual
    }