"""
Funciones para carga y procesamiento de archivos
"""
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from Config.constants import (
    FILA_INICIO_DATOS,
    COLUMNA_SHIFT,
    COLUMNAS_ASIGNACIONES,
    FECHA_INICIO,
    FECHA_FIN
)

from utils.calculations import parse_shift_column, process_updt_file
from utils.validators import (
    validate_filename,
    validate_file_structure,
    validate_shift_format,
    validate_date_range,
    validate_turno_values,
    validate_numeric_values,
    generate_validation_report
)


def load_excel_file(uploaded_file, indicador: str) -> Tuple[Optional[pd.DataFrame], List[str]]:
    """
    Carga un archivo Excel/CSV desde Streamlit uploader.

    Args:
        uploaded_file: Archivo subido por st.file_uploader
        indicador: Tipo de indicador

    Returns:
        Tupla (DataFrame, lista_errores)
    """
    errores: List[str] = []
    try:
        file_ext = Path(uploaded_file.name).suffix.lower()
        # Leer archivo desde la fila 3 (índice 2)
        if file_ext == '.csv':
            df = pd.read_csv(uploaded_file, skiprows=FILA_INICIO_DATOS)
        else:  # .xlsx, .xls
            df = pd.read_excel(uploaded_file, skiprows=FILA_INICIO_DATOS)

        # Limpiar nombres de columnas (quitar espacios a los extremos)
        df.columns = df.columns.str.strip()
        return df, errores
    except Exception as e:
        errores.append(f"❌ Error leyendo archivo: {str(e)}")
        return None, errores


def process_indicator_file(uploaded_file, indicador: str, maquina: str) -> Tuple[Optional[pd.DataFrame], Dict]:
    """
    Procesa completamente un archivo de indicador:
    - Valida nombre/estructura/Shift
    - (UPDT) calcula suma de columnas y filtra >50% antes del parseo
    - Parsea Shift (fecha, turno, week, mes_asignado, etc.)
    - Valida fechas, turnos y rangos numéricos
    - Convierte a porcentaje KPIs de % cuando vienen en 0-1
    - Regla especial Strategic PR: excluir 0% y 100% de promedios (NaN)
    - Asigna máquina y ordena por fecha

    Returns:
        Tupla (DataFrame_procesado, reporte_validacion)
    """
    validaciones: List[Tuple[bool, str]] = []

    # 1) Validar nombre de archivo
    es_valido, ind_detectado, msg = validate_filename(uploaded_file.name)
    validaciones.append((es_valido, msg))
    if not es_valido:
        return None, generate_validation_report(validaciones)

    # 2) Cargar archivo
    df, errores = load_excel_file(uploaded_file, indicador)
    if errores:
        for error in errores:
            validaciones.append((False, error))
        return None, generate_validation_report(validaciones)

    # 3) Validar estructura
    es_valido, msg = validate_file_structure(df, indicador)
    validaciones.append((es_valido, msg))
    if not es_valido:
        return None, generate_validation_report(validaciones)

    # 4) Validar formato de columna Shift (eliminar inválidos)
    es_valido, msg, invalid_idx = validate_shift_format(df[COLUMNA_SHIFT])
    validaciones.append((es_valido, msg))
    if not es_valido:
        df = df.drop(invalid_idx).reset_index(drop=True)
        validaciones.append((True, f"⚠️ Se eliminaron {len(invalid_idx)} filas con formato inválido"))

    # 4.5) Procesar UPDT ANTES del parseo de Shift
    #     (evita perder 'fecha' y asegura sumar solo columnas de causas)
    if indicador == 'UPDT':
        try:
            # process_updt_file devuelve ['Shift','UPDT'] con filas UPDT <= 50
            df = process_updt_file(df)
            validaciones.append((True, "✅ Archivo UPDT procesado (suma de columnas y filtro ≤ 50%)"))
        except Exception as e:
            validaciones.append((False, f"❌ Error procesando UPDT: {str(e)}"))
            return None, generate_validation_report(validaciones)

    # 5) Parsear columna Shift -> agrega fecha/turno/week/mes_asignado/etc.
    try:
        parsed_data = df[COLUMNA_SHIFT].apply(parse_shift_column)
        df_parsed = pd.DataFrame(parsed_data.tolist())
        df = pd.concat([df, df_parsed], axis=1)
        validaciones.append((True, "✅ Columna Shift parseada correctamente"))
    except Exception as e:
        validaciones.append((False, f"❌ Error parseando Shift: {str(e)}"))
        return None, generate_validation_report(validaciones)

    # 6) Validar rango de fechas (informativo, no bloquea)
    es_valido, msg = validate_date_range(df, FECHA_INICIO, FECHA_FIN)
    validaciones.append((es_valido, msg))

    # 7) Validar valores de turno
    es_valido, msg = validate_turno_values(df['turno'])
    validaciones.append((es_valido, msg))

    # 8) Validar valores numéricos del KPI
    kpi_col = indicador if indicador in df.columns else None
    if kpi_col:
        if indicador in ['UPDT', 'Reject Rate', 'Strategic PR']:
            # Porcentajes esperados entre 0 y 100 (o 0-1 previo a conversión)
            es_valido, msg = validate_numeric_values(df[kpi_col], kpi_col, 0, 100)
        else:  # MTBF
            es_valido, msg = validate_numeric_values(df[kpi_col], kpi_col, 0)
        validaciones.append((es_valido, msg))

    # 9) Asignar columna de máquina
    df['maquina'] = maquina
    validaciones.append((True, f"✅ Datos asignados a máquina '{maquina}'"))

    # 10) Conversión a porcentaje y REGLAS ESPECIALES
    if kpi_col and indicador in ['UPDT', 'Reject Rate', 'Strategic PR']:
        # Si los valores están en 0-1, convertir a 0-100
        if df[kpi_col].max() <= 1:
            df[kpi_col] = df[kpi_col] * 100
            validaciones.append((True, f"✅ {indicador} convertido a porcentaje (0-100)"))

        # Regla Strategic PR: excluir 0% y 100% para cálculos (promedios, etc.)
        if indicador == 'Strategic PR':
            mask_excluir = df[kpi_col].isin([0, 100])
            n_excluidos = int(mask_excluir.sum())
            if n_excluidos > 0:
                # Marcar como NA: pandas y plotly ignorarán en promedios/estadísticas
                df.loc[mask_excluir, kpi_col] = pd.NA
                validaciones.append(
                    (True, f"⚠️ Strategic PR: {n_excluidos} valores (0% o 100%) excluidos de los promedios")
                )

    # 11) Ordenar por fecha
    df = df.sort_values('fecha').reset_index(drop=True)

    # 12) Generar reporte
    reporte = generate_validation_report(validaciones)
    return df, reporte


def load_asignaciones_csv(filepath: str = 'data/asignaciones_operadores.csv') -> Tuple[Optional[pd.DataFrame], List[str]]:
    """
    Carga el archivo CSV de asignaciones fijas y parsea fechas.

    Returns:
        (DataFrame, lista_errores)
    """
    errores: List[str] = []
    try:
        # Cargar CSV
        df = pd.read_csv(filepath)

        # Validar columnas requeridas
        missing_cols = [col for col in COLUMNAS_ASIGNACIONES if col not in df.columns]
        if missing_cols:
            errores.append(f"❌ Faltan columnas en asignaciones: {missing_cols}")
            return None, errores

        # Parsear fechas - intentar múltiples formatos y luego inferencia
        date_formats = ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y']
        for col in ['Fecha_Inicio', 'Fecha_Fin']:
            parsed = False
            for fmt in date_formats:
                try:
                    df[col] = pd.to_datetime(df[col], format=fmt)
                    parsed = True
                    break
                except Exception:
                    continue
            if not parsed:
                try:
                    df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
                except Exception:
                    errores.append(f"❌ No se pudo parsear la columna de fecha: {col}")
                    return None, errores

        return df, errores

    except FileNotFoundError:
        errores.append(f"❌ No se encontró el archivo: {filepath}")
        return None, errores
    except Exception as e:
        errores.append(f"❌ Error cargando asignaciones: {str(e)}")
        return None, errores


def merge_with_asignaciones(df_indicador: pd.DataFrame, df_asignaciones: pd.DataFrame) -> pd.DataFrame:
    """
    Cruza datos de indicador con asignaciones para obtener operador y LC
    por (fecha ∈ [ini, fin]) AND (turno) AND (máquina).
    """

    def get_operador_info(row):
        fecha = row['fecha']
        turno = row['turno']
        maquina = row['maquina']

        match = df_asignaciones[
            (df_asignaciones['Fecha_Inicio'] <= fecha) &
            (df_asignaciones['Fecha_Fin'] >= fecha) &
            (df_asignaciones['Turno'] == turno) &
            (df_asignaciones['Máquina'] == maquina)
        ]

        if len(match) > 0:
            return pd.Series({
                'operador': match.iloc[0]['Operador'],
                'coordinador': match.iloc[0]['Coordinador']
            })
        else:
            # No eliminar: útil para análisis por máquina aunque falte asignación
            return pd.Series({'operador': 'SIN_ASIGNAR', 'coordinador': 'SIN_ASIGNAR'})

    df_merged = df_indicador.copy()
    operador_info = df_merged.apply(get_operador_info, axis=1)
    df_merged = pd.concat([df_merged, operador_info], axis=1)
    return df_merged


def consolidate_all_data(
    uploaded_files_dict: Dict[str, Dict[str, any]],
    df_asignaciones: pd.DataFrame
) -> Tuple[Dict[str, pd.DataFrame], List[Dict]]:
    """
    Consolida todos los archivos subidos en DataFrames por indicador y
    devuelve (final_data, reportes_de_validación).
    """
    consolidated: Dict[str, List[pd.DataFrame]] = {
        'MTBF': [],
        'UPDT': [],
        'Reject Rate': [],
        'Strategic PR': []
    }
    reportes: List[Dict] = []

    # Procesar cada archivo
    for maquina, archivos in uploaded_files_dict.items():
        for indicador, uploaded_file in archivos.items():
            if uploaded_file is None:
                continue

            df_processed, reporte = process_indicator_file(uploaded_file, indicador, maquina)

            # Guardar el reporte siempre (exitoso o no)
            reportes.append({
                'maquina': maquina,
                'indicador': indicador,
                'reporte': reporte
            })

            # Si fue válido, cruzar con asignaciones y acumular
            if df_processed is not None and reporte.get('es_valido', False):
                df_with_operators = merge_with_asignaciones(df_processed, df_asignaciones)
                consolidated[indicador].append(df_with_operators)

    # Concatenar por indicador
    final_data: Dict[str, pd.DataFrame] = {}
    for indicador, dfs_list in consolidated.items():
        if dfs_list:
            final_data[indicador] = pd.concat(dfs_list, ignore_index=True)

    return final_data, reportes


def save_to_session_state(data_dict: Dict[str, pd.DataFrame]):
    """
    Guarda datos procesados en session_state de Streamlit.
    """
    st.session_state['data_loaded'] = True
    st.session_state['kpi_data'] = data_dict
    st.session_state['fecha_carga'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')


def load_from_session_state() -> Optional[Dict[str, pd.DataFrame]]:
    """
    Carga datos desde session_state.
    """
    if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
        return st.session_state.get('kpi_data', None)
    return None