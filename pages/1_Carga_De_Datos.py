import streamlit as st
import pandas as pd
from Config.constants import MAQUINAS, INDICADORES, FECHA_INICIO, FECHA_FIN
from utils import (
    load_asignaciones_csv,
    consolidate_all_data,
    save_to_session_state,
    check_data_completeness
)

# ============================
# CONFIGURACIÓN DE LA PÁGINA
# ============================
st.set_page_config(
    page_title="Carga de Datos - PMI Dashboard",
    page_icon="📤",
    layout="wide"
)

st.sidebar.image("assets/logo.png", use_column_width=True)

# ============================
# TÍTULO E INSTRUCCIONES
# ============================
st.title("📤 Carga de Datos")
st.markdown("### Sube los archivos de indicadores para cada máquina")

st.markdown("---")

with st.expander("📋 **Instrucciones de Carga**", expanded=True):
    st.markdown("""
    **Pasos para cargar datos:**
    
    1. **Selecciona una o varias máquinas** de la lista disponible
    2. **Para cada máquina**, sube los archivos de los 4 indicadores:
       - **MTBF**: Mean Time Between Failures (minutos)
       - **UPDT**: Unplanned Downtime (%)
       - **Reject Rate**: Tasa de Rechazo (%)
       - **Strategic PR**: Performance Rate (%)
    3. Los archivos deben:
       - Empezar con el nombre del indicador (ej: `MTBF-Shift-data.xlsx`)
       - Ser formato `.csv` o `.xlsx`
       - Contener columna `Shift` con formato: `S[1-3] DD-MM-YYYY`
       - Tener datos desde la fila 3
    4. Haz clic en **"Procesar Datos"** para validar y cargar
    
    ⚠️ **Nota**: No es necesario subir los 4 indicadores para todas las máquinas. Puedes cargar datos parciales.
    """)

st.markdown("---")

# ============================
# ESTADO INICIAL
# ============================
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = {}

# ============================
# SELECCIÓN DE MÁQUINAS
# ============================
st.subheader("1️⃣ Selecciona Máquinas")
selected_machines = st.multiselect(
    "Elige las máquinas que deseas cargar:",
    options=MAQUINAS,
    default=None,
    help="Puedes seleccionar una o varias máquinas"
)

if not selected_machines:
    st.info("👆 Selecciona al menos una máquina para comenzar")
    st.stop()

st.markdown("---")

# ============================
# CARGA DE ARCHIVOS POR MÁQUINA
# ============================
st.subheader("2️⃣ Sube Archivos por Máquina e Indicador")

uploaded_data = {}

for maquina in selected_machines:
    with st.expander(f"🔧 **{maquina}**", expanded=True):
        st.markdown(f"##### Archivos para {maquina}")
        cols = st.columns(4)
        uploaded_data[maquina] = {}

        for idx, (indicador, config) in enumerate(INDICADORES.items()):
            with cols[idx]:
                st.markdown(f"**{indicador}**")
                st.caption(f"{config['unidad']} - {config['mejor']} es mejor")
                
                file = st.file_uploader(
                    f"Subir archivo",
                    type=['csv', 'xlsx', 'xls'],
                    key=f"{maquina}_{indicador}",
                    help=f"Archivo debe empezar con '{indicador}'"
                )
                
                uploaded_data[maquina][indicador] = file
                
                if file is not None:
                    st.success(f"✅ {file.name}")

st.markdown("---")

# ============================
# RESUMEN DE ARCHIVOS SUBIDOS
# ============================
st.subheader("3️⃣ Resumen de Archivos Subidos")

total_files = sum(
    1 for maquina in uploaded_data.values() 
    for file in maquina.values() 
    if file is not None
)

col_summary1, col_summary2, col_summary3 = st.columns(3)

with col_summary1:
    st.metric("Máquinas Seleccionadas", len(selected_machines))
with col_summary2:
    st.metric("Archivos Subidos", total_files)
with col_summary3:
    expected_files = len(selected_machines) * 4
    completeness = (total_files / expected_files * 100) if expected_files > 0 else 0
    st.metric("Completitud", f"{completeness:.0f}%")

st.markdown("#### Estado de Carga por Máquina")

summary_data = []
for maquina in selected_machines:
    row = {'Máquina': maquina}
    for indicador in INDICADORES.keys():
        file = uploaded_data[maquina][indicador]
        row[indicador] = "✅" if file is not None else "⬜"
    summary_data.append(row)

df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================
# PROCESAMIENTO DE DATOS
# ============================
st.subheader("4️⃣ Procesar y Validar Datos")

if total_files == 0:
    st.warning("⚠️ No hay archivos subidos. Sube al menos un archivo para continuar.")
    st.stop()

col_btn1, col_btn2 = st.columns([1, 3])
with col_btn1:
    process_button = st.button("🚀 Procesar Datos", type="primary", use_container_width=True)
with col_btn2:
    st.caption("Esto validará los archivos, parseará las fechas y cruzará con asignaciones de operadores")

# ============================
# AL HACER CLIC EN PROCESAR
# ============================
if process_button:
    with st.spinner("⏳ Procesando y validando datos..."):
        
        # 1. Cargar asignaciones
        st.info("📋 Cargando asignaciones de operadores...")
        df_asignaciones, errores_asig = load_asignaciones_csv()
        
        if errores_asig:
            st.error("❌ Error cargando asignaciones:")
            for error in errores_asig:
                st.error(error)
            st.stop()
        
        st.success("✅ Asignaciones cargadas correctamente")
        
        # 2. Consolidar archivos
        st.info("🔄 Validando y procesando archivos...")
        consolidated_data, reportes = consolidate_all_data(uploaded_data, df_asignaciones)
        
        # 3. Reporte general
        st.markdown("---")
        st.subheader("📊 Reporte de Validación")
        
        total_validations = len(reportes)
        successful = sum(1 for r in reportes if r['reporte']['es_valido'])
        failed = total_validations - successful
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            st.metric("Total Archivos", total_validations)
        with col_v2:
            st.metric("Validados ✅", successful, delta="OK")
        with col_v3:
            st.metric("Con Errores ❌", failed, delta="Revisar" if failed > 0 else "Todo bien")

        # 4. Detalle de validaciones
        with st.expander("📝 Ver Detalle de Validaciones", expanded=(failed > 0)):
            for reporte in reportes:
                maquina = reporte['maquina']
                indicador = reporte['indicador']
                validacion = reporte['reporte']

                status_icon = "✅" if validacion['es_valido'] else "❌"
                st.markdown(f"### {status_icon} {maquina} - {indicador}")

                tab_ok, tab_err = st.tabs(["✅ Exitosas", "❌ Errores"])

                with tab_ok:
                    if validacion['validaciones_ok']:
                        for msg in validacion['validaciones_ok']:
                            st.markdown(f"- {msg}")
                    else:
                        st.info("No hay validaciones exitosas en este archivo.")

                with tab_err:
                    if validacion['errores']:
                        for error in validacion['errores']:
                            st.error(error)
                    else:
                        st.info("Sin errores detectados.")

                st.markdown("---")

        # 5. Si hay datos válidos, guardar y mostrar preview
        if consolidated_data:
            st.success("🎉 **¡Datos procesados exitosamente!**")

            save_to_session_state(consolidated_data)

            st.markdown("---")
            st.subheader("👀 Vista Previa de Datos")

            tabs = st.tabs([f"{ind} ({len(df)} registros)" for ind, df in consolidated_data.items()])

            for idx, (indicador, df) in enumerate(consolidated_data.items()):
                with tabs[idx]:
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    with col_m1:
                        st.metric("Registros", f"{len(df):,}")
                    with col_m2:
                        st.metric("Máquinas", df['maquina'].nunique())
                    with col_m3:
                        st.metric("Operadores", df['operador'].nunique())
                    with col_m4:
                        st.metric("Weeks", df['week'].nunique())

                    completeness = check_data_completeness(df, FECHA_INICIO, FECHA_FIN)

                    st.markdown("**📈 Completitud de Datos:**")
                    st.progress(completeness['completitud_pct'] / 100)
                    st.caption(f"{completeness['completitud_pct']:.1f}% de días con datos "
                               f"({completeness['dias_con_datos']} de {completeness['dias_totales_esperados']} días)")

                    st.markdown("**🔄 Distribución por Turno:**")
                    turno_cols = st.columns(3)
                    for idx_t, (turno, count) in enumerate(completeness['registros_por_turno'].items()):
                        with turno_cols[idx_t]:
                            st.metric(turno, f"{count:,}")

                    st.markdown("**📋 Muestra de Datos:**")
                    st.dataframe(
                        df[['fecha_str', 'turno', 'maquina', 'operador', 'coordinador',
                            indicador, 'week', 'mes_asignado']].head(20),
                        use_container_width=True,
                        hide_index=True
                    )

            st.markdown("---")
            st.success("✅ **Datos listos para análisis!** Puedes ir a las otras secciones del dashboard.")

            col_nav1, col_nav2, col_nav3 = st.columns(3)
            with col_nav1:
                if st.button("📊 Ir a Dashboard General", use_container_width=True):
                    st.switch_page("pages/2_📊_Dashboard_General.py")
            with col_nav2:
                if st.button("👷 Análisis de Operadores", use_container_width=True):
                    st.switch_page("pages/3_👷_Análisis_Operadores.py")
            with col_nav3:
                if st.button("⚙️ Análisis de Máquinas", use_container_width=True):
                    st.switch_page("pages/5_⚙️_Análisis_Máquinas.py")

        else:
            st.error("❌ No se pudo procesar ningún archivo correctamente. Revisa los errores arriba.")

# ============================
# OPCIONES AVANZADAS
# ============================
st.markdown("---")

with st.expander("🗑️ Opciones Avanzadas"):
    st.markdown("### Limpiar Datos Cargados")
    st.warning("⚠️ Esto eliminará todos los datos cargados actualmente")
    
    if st.button("🗑️ Limpiar Todo", type="secondary"):
        for key in ['data_loaded', 'kpi_data', 'fecha_carga']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Datos limpiados. Recarga la página para empezar de nuevo.")
        st.rerun()
