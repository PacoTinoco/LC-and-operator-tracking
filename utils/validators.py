"""
Funciones de validación de archivos y datos
"""

import pandas as pd
import re
from typing import Dict, List, Tuple
from pathlib import Path

from Config.constants import (
    INDICADORES,
    EXTENSIONES_PERMITIDAS,
    COLUMNA_SHIFT,
    FILA_INICIO_DATOS,
    MAQUINAS,
    TURNOS
)


def validate_filename(filename: str) -> Tuple[bool, str, str]:
    """
    Valida que el nombre del archivo corresponda a un indicador válido
    
    Args:
        filename: Nombre del archivo (ej: 'MTBF-Shift-data.xlsx')
    
    Returns:
        Tupla (es_valido, indicador, mensaje)
    """
    # Obtener extensión
    ext = Path(filename).suffix.lower()
    
    # Validar extensión
    if ext not in EXTENSIONES_PERMITIDAS:
        return False, '', f"Extensión '{ext}' no permitida. Use: {', '.join(EXTENSIONES_PERMITIDAS)}"
    
    # Buscar indicador en el nombre
    filename_upper = filename.upper()
    
    for indicador, config in INDICADORES.items():
        for variante in config['variantes']:
            if filename_upper.startswith(variante.upper()):
                return True, indicador, f"✅ Archivo identificado como '{indicador}'"
    
    # Si no coincide con ningún indicador
    indicadores_validos = ', '.join(INDICADORES.keys())
    return False, '', f"❌ El archivo debe empezar con: {indicadores_validos}"


def validate_file_structure(df: pd.DataFrame, indicador: str) -> Tuple[bool, str]:
    """
    Valida la estructura del DataFrame cargado
    
    Args:
        df: DataFrame cargado desde el archivo
        indicador: Tipo de indicador ('MTBF', 'UPDT', etc.)
    
    Returns:
        Tupla (es_valido, mensaje)
    """
    # 1. Validar que tenga columna 'Shift'
    if COLUMNA_SHIFT not in df.columns:
        return False, f"❌ Falta columna requerida: '{COLUMNA_SHIFT}'"
    
    # 2. Validar que no esté vacío
    if len(df) == 0:
        return False, "❌ El archivo está vacío"
    
    # 3. Validar según tipo de indicador
    if indicador == 'UPDT':
        # UPDT debe tener columnas numéricas además de Shift
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return False, "❌ UPDT debe tener columnas numéricas (porcentajes)"
    else:
        # Otros indicadores deben tener columna del valor
        expected_col = None
        for variante in INDICADORES[indicador]['variantes']:
            if variante in df.columns:
                expected_col = variante
                break
        
        if expected_col is None:
            variantes = ', '.join(INDICADORES[indicador]['variantes'])
            return False, f"❌ Falta columna de valor. Esperado: {variantes}"
    
    return True, "✅ Estructura válida"


def validate_shift_format(shift_series: pd.Series) -> Tuple[bool, str, List[int]]:
    """
    Valida el formato de la columna 'Shift'
    
    Formato esperado: 'S[1-3] DD-MM-YYYY'
    
    Args:
        shift_series: Serie de pandas con valores de Shift
    
    Returns:
        Tupla (es_valido, mensaje, lista_indices_invalidos)
    """
    # Pattern: S[1-3] seguido de espacio y fecha DD-MM-YYYY
    pattern = r'^S[1-3]\s\d{2}-\d{2}-\d{4}$'
    
    invalid_indices = []
    
    for idx, value in enumerate(shift_series):
        if pd.isna(value):
            invalid_indices.append(idx)
            continue
        
        value_str = str(value).strip()
        if not re.match(pattern, value_str):
            invalid_indices.append(idx)
    
    if invalid_indices:
        n_invalid = len(invalid_indices)
        sample = invalid_indices[:5]  # Primeros 5 errores
        msg = f"❌ {n_invalid} registros con formato inválido de Shift. "
        msg += f"Filas con error: {sample}"
        if n_invalid > 5:
            msg += f" (y {n_invalid - 5} más...)"
        return False, msg, invalid_indices
    
    return True, "✅ Formato de Shift correcto", []


def validate_date_range(df: pd.DataFrame, fecha_inicio: str, fecha_fin: str) -> Tuple[bool, str]:
    """
    Valida que las fechas estén dentro del rango esperado (OPCIONAL - solo informativo)
    
    Args:
        df: DataFrame con columna 'fecha' parseada
        fecha_inicio: Fecha mínima esperada (YYYY-MM-DD)
        fecha_fin: Fecha máxima esperada (YYYY-MM-DD)
    
    Returns:
        Tupla (es_valido, mensaje)
    """
    # Esta validación es solo informativa, no bloquea la carga
    fecha_min_data = df['fecha'].min()
    fecha_max_data = df['fecha'].max()
    
    msg = f"✅ Rango de fechas: {fecha_min_data.strftime('%Y-%m-%d')} a {fecha_max_data.strftime('%Y-%m-%d')}"
    
    return True, msg  # Siempre retorna True, solo informa el rango


def validate_turno_values(turno_series: pd.Series) -> Tuple[bool, str]:
    """
    Valida que los valores de turno sean correctos
    
    Args:
        turno_series: Serie con valores de turno
    
    Returns:
        Tupla (es_valido, mensaje)
    """
    unique_turnos = turno_series.unique()
    invalid_turnos = [t for t in unique_turnos if t not in TURNOS]
    
    if invalid_turnos:
        msg = f"❌ Turnos inválidos encontrados: {invalid_turnos}. "
        msg += f"Valores válidos: {TURNOS}"
        return False, msg
    
    return True, "✅ Valores de turno correctos"


def validate_numeric_values(series: pd.Series, column_name: str, 
                           min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
    """
    Valida valores numéricos de un KPI
    
    Args:
        series: Serie con valores numéricos
        column_name: Nombre de la columna
        min_val: Valor mínimo permitido (opcional)
        max_val: Valor máximo permitido (opcional)
    
    Returns:
        Tupla (es_valido, mensaje)
    """
    # Verificar que sea numérico
    if not pd.api.types.is_numeric_dtype(series):
        return False, f"❌ Columna '{column_name}' debe ser numérica"
    
    # Contar valores nulos
    n_nulls = series.isna().sum()
    if n_nulls > 0:
        pct_nulls = (n_nulls / len(series)) * 100
        if pct_nulls > 50:  # Más del 50% nulos
            return False, f"❌ Demasiados valores nulos en '{column_name}': {pct_nulls:.1f}%"
    
    # Verificar valores negativos (si aplica)
    if min_val is not None:
        n_below = (series < min_val).sum()
        if n_below > 0:
            return False, f"❌ {n_below} valores menores a {min_val} en '{column_name}'"
    
    # Verificar valores máximos (si aplica)
    if max_val is not None:
        n_above = (series > max_val).sum()
        if n_above > 0:
            return False, f"❌ {n_above} valores mayores a {max_val} en '{column_name}'"
    
    return True, f"✅ Valores numéricos válidos en '{column_name}'"


def validate_machine_name(machine: str) -> Tuple[bool, str]:
    """
    Valida que el nombre de máquina sea correcto
    
    Args:
        machine: Nombre de la máquina
    
    Returns:
        Tupla (es_valido, mensaje)
    """
    if machine not in MAQUINAS:
        return False, f"❌ Máquina inválida: '{machine}'. Válidas: {', '.join(MAQUINAS)}"
    
    return True, f"✅ Máquina '{machine}' válida"


def check_data_completeness(df: pd.DataFrame, fecha_inicio: str, fecha_fin: str) -> Dict:
    """
    Calcula métricas de completitud de datos
    
    Args:
        df: DataFrame con datos
        fecha_inicio: Fecha de inicio del periodo
        fecha_fin: Fecha de fin del periodo
    
    Returns:
        Dict con métricas de completitud
    """
    fecha_min = pd.to_datetime(fecha_inicio)
    fecha_max = pd.to_datetime(fecha_fin)
    
    # Días totales esperados
    dias_totales = (fecha_max - fecha_min).days + 1
    
    # Días únicos en el dataset (por turno = 3 registros por día)
    dias_unicos = df['fecha'].nunique()
    
    # Completitud general
    completitud = (dias_unicos / dias_totales) * 100
    
    # Por turno
    registros_por_turno = df.groupby('turno').size()
    
    return {
        'dias_totales_esperados': dias_totales,
        'dias_con_datos': dias_unicos,
        'completitud_pct': completitud,
        'registros_por_turno': registros_por_turno.to_dict(),
        'fecha_min_datos': df['fecha'].min().strftime('%Y-%m-%d'),
        'fecha_max_datos': df['fecha'].max().strftime('%Y-%m-%d')
    }


def generate_validation_report(validations: List[Tuple[bool, str]]) -> Dict:
    """
    Genera reporte consolidado de validaciones
    
    Args:
        validations: Lista de tuplas (es_valido, mensaje)
    
    Returns:
        Dict con resumen de validaciones
    """
    total = len(validations)
    exitosas = sum(1 for v in validations if v[0])
    fallidas = total - exitosas
    
    mensajes_error = [msg for es_valido, msg in validations if not es_valido]
    mensajes_ok = [msg for es_valido, msg in validations if es_valido]
    
    return {
        'total': total,
        'exitosas': exitosas,
        'fallidas': fallidas,
        'tasa_exito': (exitosas / total * 100) if total > 0 else 0,
        'errores': mensajes_error,
        'validaciones_ok': mensajes_ok,
        'es_valido': fallidas == 0
    }