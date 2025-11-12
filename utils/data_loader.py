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
    errores = []
    try:
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext == '.csv':
            df = pd.read_csv(uploaded_file, skiprows=FILA_INICIO_DATOS)
        else:
            df = pd.read_excel(uploaded_file, skiprows=FILA_INICIO_DATOS)
        df.columns = df.columns.str.strip()
        return df, errores
    except Exception as e:
        errores.append(f"❌ Error leyendo archivo: {str(e)}")
        return None, errores


def process_indicator_file(uploaded_file, indicador: str, maquina: str) -> Tuple[Optional[pd.DataFrame], Dict]:
    validaciones = []

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

    # 4) Validar formato Shift
    es_valido, msg, invalid_idx = validate_shift_format(df[COLUMNA_SHIFT])
    validaciones.append((es_valido, msg))
    if not es_valido:
        df = df.drop(invalid_idx).reset_index(drop=True)
        validaciones.append((True, f"⚠️ Se eliminaron {len(invalid_idx)} filas con formato inválido"))

    # 4.5) Procesar UPDT antes del parseo
    if indicador == 'UPDT':
        try:
            df = process_updt_file(df)  # Devuelve ['Shift', 'UPDT']
            validaciones.append((True, "✅ Archivo UPDT procesado (suma de columnas)"))
        except Exception as e:
            validaciones.append((False, f"❌ Error procesando UPDT: {str(e)}"))
            return None, generate_validation_report(validaciones)

    # 5) Parsear columna Shift
    try:
        parsed_data = df[COLUMNA_SHIFT].apply(parse_shift_column)
        df_parsed = pd.DataFrame(parsed_data.tolist())
        df = pd.concat([df, df_parsed], axis=1)
        validaciones.append((True, "✅ Columna Shift parseada correctamente"))
    except Exception as e:
        validaciones.append((False, f"❌ Error parseando Shift: {str(e)}"))
        return None, generate_validation_report(validaciones)

    # 6) Validar rango de fechas
    es_valido, msg = validate_date_range(df, FECHA_INICIO, FECHA_FIN)
    validaciones.append((es_valido, msg))

    # 7) Validar valores de turno
    es_valido, msg = validate_turno_values(df['turno'])
    validaciones.append((es_valido, msg))

    # 8) Validar valores numéricos
    kpi_col = indicador if indicador in df.columns else None
    if kpi_col:
        if indicador in ['UPDT', 'Reject Rate', 'Strategic PR']:
            es_valido, msg = validate_numeric_values(df[kpi_col], kpi_col, 0, 100)
        else:
            es_valido, msg = validate_numeric_values(df[kpi_col], kpi_col, 0)
        validaciones.append((es_valido, msg))

    # 9) Asignar máquina
    df['maquina'] = maquina
    validaciones.append((True, f"✅ Datos asignados a máquina '{maquina}'"))

    # 10) Conversión a porcentaje para KPIs relevantes
    if indicador in ['UPDT', 'Reject Rate', 'Strategic PR'] and kpi_col:
        # Multiplicar por 100 si los valores parecen estar en escala 0-1
        if df[kpi_col].max() <= 1:
            df[kpi_col] = df[kpi_col] * 100
            validaciones.append((True, f"✅ {indicador} convertido a porcentaje (0-100)"))

    # 11) Ordenar por fecha
    df = df.sort_values('fecha').reset_index(drop=True)

    reporte = generate_validation_report(validaciones)
    return df, reporte


def load_asignaciones_csv(filepath: str = 'data/asignaciones_operadores.csv') -> Tuple[Optional[pd.DataFrame], List[str]]:
    errores = []
    try:
        df = pd.read_csv(filepath)
        missing_cols = [col for col in COLUMNAS_ASIGNACIONES if col not in df.columns]
        if missing_cols:
            errores.append(f"❌ Faltan columnas en asignaciones: {missing_cols}")
            return None, errores

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
            return pd.Series({'operador': match.iloc[0]['Operador'], 'coordinador': match.iloc[0]['Coordinador']})
        else:
            return pd.Series({'operador': 'SIN_ASIGNAR', 'coordinador': 'SIN_ASIGNAR'})

    df_merged = df_indicador.copy()
    operador_info = df_merged.apply(get_operador_info, axis=1)
    df_merged = pd.concat([df_merged, operador_info], axis=1)
    return df_merged


def consolidate_all_data(uploaded_files_dict: Dict[str, Dict[str, any]], df_asignaciones: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    consolidated = {'MTBF': [], 'UPDT': [], 'Reject Rate': [], 'Strategic PR': []}
    reportes = []
    for maquina, archivos in uploaded_files_dict.items():
        for indicador, uploaded_file in archivos.items():
            if uploaded_file is not None:
                df_processed, reporte = process_indicator_file(uploaded_file, indicador, maquina)
                reportes.append({'maquina': maquina, 'indicador': indicador, 'reporte': reporte})
                if df_processed is not None and reporte['es_valido']:
                    df_with_operators = merge_with_asignaciones(df_processed, df_asignaciones)
                    consolidated[indicador].append(df_with_operators)
    final_data = {}
    for indicador, dfs_list in consolidated.items():
        if dfs_list:
            final_data[indicador] = pd.concat(dfs_list, ignore_index=True)
    return final_data, reportes


def save_to_session_state(data_dict: Dict[str, pd.DataFrame]):
    st.session_state['data_loaded'] = True
    st.session_state['kpi_data'] = data_dict
    st.session_state['fecha_carga'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')


def load_from_session_state() -> Optional[Dict[str, pd.DataFrame]]:
    if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
        return st.session_state.get('kpi_data', None)
    return None