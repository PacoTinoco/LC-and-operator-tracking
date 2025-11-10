"""
Funciones de cálculo para KPIs, weeks y agregaciones
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import calendar
from Config.constants import FORMATO_FECHA_SHIFT, INDICADORES

def parse_shift_column(shift_str: str) -> Dict:
    """
    Parsea la columna 'Shift' con formato 'S1 07-01-2025'
    
    Args:
        shift_str: String con formato 'S[1-3] DD-MM-YYYY'
    
    Returns:
        Dict con turno, fecha y componentes
    """
    try:
        # Dividir por espacio
        parts = shift_str.strip().split()
        
        if len(parts) != 2:
            raise ValueError(f"Formato incorrecto: {shift_str}")
        
        turno = parts[0]  # 'S1', 'S2', 'S3'
        fecha_str = parts[1]  # '07-01-2025'
        
        # Parsear fecha
        fecha = datetime.strptime(fecha_str, FORMATO_FECHA_SHIFT)
        
        # Calcular week number y día de la semana
        week_num = get_pmi_week_number(fecha)
        dia_semana = fecha.strftime('%A')  # Nombre del día en inglés
        
        # Determinar mes basado en la lógica de weeks
        mes_asignado = get_month_for_week(fecha, week_num)
        
        return {
            'turno': turno,
            'fecha': fecha,
            'dia': fecha.day,
            'mes': fecha.month,
            'año': fecha.year,
            'week': week_num,
            'dia_semana': dia_semana,
            'mes_asignado': mes_asignado,  # Mes al que pertenece la week
            'fecha_str': fecha.strftime('%Y-%m-%d')
        }
    
    except Exception as e:
        raise ValueError(f"Error parseando shift '{shift_str}': {str(e)}")


def get_pmi_week_number(fecha: datetime) -> int:
    """
    Calcula el número de week según lógica PMI
    
    Reglas:
    - Week 1 = Primera semana del año (aunque no empiece en Lunes)
    - Cada week va de Lunes a Domingo
    - Si el año empieza en otro día, Week 1 va de ese día hasta el Domingo
    
    Args:
        fecha: Fecha a calcular
    
    Returns:
        Número de week (1-53)
    """
    año = fecha.year
    
    # Primer día del año
    primer_dia = datetime(año, 1, 1)
    
    # Si el año empieza en Lunes, usar ISO week
    if primer_dia.weekday() == 0:  # 0 = Lunes
        return fecha.isocalendar()[1]
    
    # Si no empieza en Lunes, calcular week custom
    # Encontrar el primer Lunes del año
    dias_hasta_lunes = (7 - primer_dia.weekday()) % 7
    if dias_hasta_lunes == 0:
        dias_hasta_lunes = 7
    
    primer_lunes = primer_dia + timedelta(days=dias_hasta_lunes)
    
    # Si la fecha es antes del primer Lunes, es Week 1
    if fecha < primer_lunes:
        return 1
    
    # Calcular semanas desde el primer Lunes
    dias_desde_primer_lunes = (fecha - primer_lunes).days
    week_num = (dias_desde_primer_lunes // 7) + 2  # +2 porque Week 1 ya pasó
    
    return week_num


def get_month_for_week(fecha: datetime, week_num: int) -> int:
    """
    Determina a qué mes asignar una week cuando cruza entre meses
    
    Lógica: Se asigna al mes donde caen MÁS días de esa week
    
    Args:
        fecha: Fecha dentro de la week
        week_num: Número de week
    
    Returns:
        Número de mes (1-12)
    """
    # Encontrar el rango completo de la week
    inicio_week, fin_week = get_week_date_range(fecha.year, week_num)
    
    # Contar días en cada mes
    dias_por_mes = {}
    current_date = inicio_week
    
    while current_date <= fin_week:
        mes = current_date.month
        dias_por_mes[mes] = dias_por_mes.get(mes, 0) + 1
        current_date += timedelta(days=1)
    
    # Devolver el mes con más días
    mes_asignado = max(dias_por_mes, key=dias_por_mes.get)
    return mes_asignado


def get_week_date_range(año: int, week_num: int) -> Tuple[datetime, datetime]:
    """
    Obtiene el rango de fechas (inicio, fin) de una week específica
    
    Args:
        año: Año
        week_num: Número de week
    
    Returns:
        Tupla (fecha_inicio, fecha_fin) de la week
    """
    primer_dia = datetime(año, 1, 1)
    
    if week_num == 1:
        # Week 1 va desde el primer día del año hasta el primer Domingo
        inicio = primer_dia
        dias_hasta_domingo = (6 - primer_dia.weekday()) % 7
        if dias_hasta_domingo == 0 and primer_dia.weekday() != 6:
            dias_hasta_domingo = 7
        fin = primer_dia + timedelta(days=dias_hasta_domingo)
    else:
        # Encontrar el primer Lunes después de Week 1
        dias_hasta_lunes = (7 - primer_dia.weekday()) % 7
        if dias_hasta_lunes == 0:
            dias_hasta_lunes = 7
        primer_lunes = primer_dia + timedelta(days=dias_hasta_lunes)
        
        # Calcular inicio de la week solicitada
        inicio = primer_lunes + timedelta(weeks=week_num - 2)
        fin = inicio + timedelta(days=6)  # Domingo
    
    return inicio, fin


def calculate_week_average(df: pd.DataFrame, kpi_column: str) -> pd.DataFrame:
    """
    Calcula promedios por week para un KPI específico
    
    Args:
        df: DataFrame con columna 'week' y el KPI
        kpi_column: Nombre de la columna del KPI
    
    Returns:
        DataFrame con promedios por week
    """
    # Filtrar valores nulos
    df_clean = df[df[kpi_column].notna()].copy()
    
    # Agrupar por week y calcular promedio
    week_avg = df_clean.groupby('week').agg({
        kpi_column: 'mean',
        'fecha': ['min', 'max', 'count']  # Min/Max date, cantidad de días
    }).reset_index()
    
    # Renombrar columnas
    week_avg.columns = ['week', 'promedio', 'fecha_inicio', 'fecha_fin', 'dias_datos']
    
    return week_avg


def calculate_month_average(df: pd.DataFrame, kpi_column: str) -> pd.DataFrame:
    """
    Calcula promedios por mes para un KPI específico
    
    Args:
        df: DataFrame con columna 'mes_asignado' y el KPI
        kpi_column: Nombre de la columna del KPI
    
    Returns:
        DataFrame con promedios por mes
    """
    # Filtrar valores nulos
    df_clean = df[df[kpi_column].notna()].copy()
    
    # Agrupar por mes asignado
    month_avg = df_clean.groupby('mes_asignado').agg({
        kpi_column: 'mean',
        'fecha': 'count'  # Cantidad de días con datos
    }).reset_index()
    
    # Renombrar columnas
    month_avg.columns = ['mes', 'promedio', 'dias_datos']
    
    # Agregar nombre del mes
    month_avg['mes_nombre'] = month_avg['mes'].apply(
        lambda x: calendar.month_name[x]
    )
    
    return month_avg


def process_updt_file(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa archivo UPDT con múltiples columnas de porcentajes
    
    Acciones:
    1. Suma todas las columnas excepto 'Shift'
    2. Filtra registros donde suma > 50%
    
    Args:
        df: DataFrame con columna 'Shift' y columnas numéricas
    
    Returns:
        DataFrame con columna 'UPDT' calculada
    """
    # Identificar columnas numéricas (excluir 'Shift')
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        raise ValueError("No se encontraron columnas numéricas en archivo UPDT")
    
    # Sumar todas las columnas numéricas
    df['UPDT'] = df[numeric_cols].sum(axis=1)
    
    # Filtrar registros con suma > 50%
    df_filtered = df[df['UPDT'] <= 50.0].copy()
    
    # Log de registros eliminados
    n_eliminados = len(df) - len(df_filtered)
    if n_eliminados > 0:
        print(f"⚠️ UPDT: {n_eliminados} registros eliminados (suma > 50%)")
    
    # Retornar solo columnas necesarias
    return df_filtered[['Shift', 'UPDT']]


def get_kpi_direction(kpi_name: str) -> str:
    """
    Obtiene la dirección de mejora de un KPI
    
    Args:
        kpi_name: Nombre del KPI
    
    Returns:
        'alto' o 'bajo' indicando qué es mejor
    """
    for key, value in INDICADORES.items():
        if kpi_name in value['variantes']:
            return value['mejor']
    
    return 'alto'  # Default


def calculate_percentile_rank(df: pd.DataFrame, kpi_column: str, value: float) -> float:
    """
    Calcula el percentil de un valor dentro de una distribución
    
    Args:
        df: DataFrame con los datos
        kpi_column: Columna del KPI
        value: Valor a evaluar
    
    Returns:
        Percentil (0-100)
    """
    values = df[kpi_column].dropna()
    
    if len(values) == 0:
        return 50.0  # Default si no hay datos
    
    percentile = (values < value).sum() / len(values) * 100
    
    return percentile


def identify_outliers(df: pd.DataFrame, kpi_column: str) -> pd.DataFrame:
    """
    Identifica outliers usando IQR (Interquartile Range)
    
    Args:
        df: DataFrame con el KPI
        kpi_column: Columna del KPI
    
    Returns:
        DataFrame con columna 'is_outlier' (bool)
    """
    Q1 = df[kpi_column].quantile(0.25)
    Q3 = df[kpi_column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df['is_outlier'] = (df[kpi_column] < lower_bound) | (df[kpi_column] > upper_bound)
    
    return df


def calculate_trend(df: pd.DataFrame, kpi_column: str, date_column: str = 'fecha') -> str:
    """
    Calcula la tendencia de un KPI en el tiempo
    
    Args:
        df: DataFrame con KPI y fechas
        kpi_column: Columna del KPI
        date_column: Columna de fecha
    
    Returns:
        'mejorando', 'empeorando' o 'estable'
    """
    # Ordenar por fecha
    df_sorted = df.sort_values(date_column)
    
    # Calcular correlación entre fecha y KPI
    # Convertir fecha a ordinal para correlación
    df_sorted['fecha_num'] = pd.to_datetime(df_sorted[date_column]).apply(lambda x: x.toordinal())
    
    corr = df_sorted[['fecha_num', kpi_column]].corr().iloc[0, 1]
    
    # Determinar tendencia según dirección del KPI
    kpi_mejor = get_kpi_direction(kpi_column)
    
    if abs(corr) < 0.1:
        return 'estable'
    elif kpi_mejor == 'alto':
        return 'mejorando' if corr > 0 else 'empeorando'
    else:  # kpi_mejor == 'bajo'
        return 'mejorando' if corr < 0 else 'empeorando'