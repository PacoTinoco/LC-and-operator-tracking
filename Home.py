"""
Home Page - Landing del Dashboard PMI
"""

import streamlit as st
from datetime import datetime
from Config.constants import MAQUINAS, INDICADORES, MENSAJES, FECHA_INICIO, FECHA_FIN
from utils import load_from_session_state

# =====================================================
# 🔧 Configuración de la página (DEBE SER LO PRIMERO)
# =====================================================
st.set_page_config(
    page_title="PMI Operators Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Home.py (muy arriba, antes o después del título)
st.sidebar.image("assets/PMI-LOGO.png", use_column_width=True)

# =====================================================
# 🏠 Contenido principal
# =====================================================
st.title("📊 Dashboard de Performance - Philip Morris International")
st.markdown("---")

# Verificar si hay datos cargados
data = load_from_session_state()
data_loaded = data is not None

# ---------------------------
# Estado del sistema
# ---------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Estado de Datos",
        value="✅ Cargados" if data_loaded else "⏳ Pendiente",
        delta="Listo para análisis" if data_loaded else "Sube archivos"
    )

with col2:
    st.metric(
        label="Máquinas Configuradas",
        value=len(MAQUINAS),
        delta="KDF-7 a KDF-17"
    )

with col3:
    st.metric(
        label="Indicadores (KPIs)",
        value=len(INDICADORES),
        delta="MTBF, UPDT, RR, SPR"
    )

st.markdown("---")

# ---------------------------
# Si hay datos cargados
# ---------------------------
if data_loaded:
    st.success("🎉 **Datos cargados exitosamente!**")
    st.subheader("📈 Resumen de Datos Cargados")

    info_cols = st.columns(len(data))
    for idx, (indicador, df) in enumerate(data.items()):
        with info_cols[idx]:
            st.metric(
                label=f"**{indicador}**",
                value=f"{len(df):,} registros",
                delta=f"{df['maquina'].nunique()} máquinas"
            )

    if 'fecha_carga' in st.session_state:
        st.info(f"📅 Última carga: {st.session_state['fecha_carga']}")

    st.markdown("---")
    st.markdown("### 🚀 ¿Qué puedes hacer ahora?")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **📊 Visualizaciones Disponibles:**
        - Dashboard General: Vista ejecutiva de todos los KPIs  
        - Análisis de Operadores: Performance individual detallado  
        - Análisis de Line Coordinators: Comparativa de equipos  
        - Análisis de Máquinas: Deep dive por equipo
        """)
    with col_b:
        st.markdown("""
        **🔍 Filtros y Análisis:**
        - Por rango de fechas  
        - Por turno (S1, S2, S3)  
        - Por máquina específica  
        - Por week o mes  
        - Comparativas entre operadores
        """)

else:
    # ---------------------------
    # Si no hay datos cargados
    # ---------------------------
    st.warning("⚠️ **No hay datos cargados**")
    st.markdown("### 📤 Para comenzar:")
    st.markdown("""
    1. Ve a la sección **"📤 Carga de Datos"** en el menú lateral  
    2. Selecciona la(s) máquina(s) que deseas analizar  
    3. Sube los archivos Excel/CSV de cada indicador:  
       - MTBF (Mean Time Between Failures)  
       - UPDT (Unplanned Downtime)  
       - Reject Rate (Tasa de Rechazo)  
       - Strategic PR (Performance Rate)  
    4. El sistema validará y procesará automáticamente los datos  
    5. ¡Listo! Podrás acceder a todas las visualizaciones
    """)

st.markdown("---")

# ---------------------------
# Información del sistema
# ---------------------------
st.subheader("ℹ️ Información del Sistema")

col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown("**🏭 Máquinas Monitoreadas:**")
    for maquina in MAQUINAS:
        st.markdown(f"- {maquina}")

with col_info2:
    st.markdown("**📊 Indicadores (KPIs):**")
    for indicador, config in INDICADORES.items():
        st.markdown(f"- **{indicador}**: {config['descripcion']}")

st.markdown(f"""
**📅 Periodo de Análisis:**  
Desde **{FECHA_INICIO}** hasta **{FECHA_FIN}**
""")

st.markdown("---")

# ---------------------------
# Footer
# ---------------------------
st.markdown("""
<div style='text-align: center; color: #999; padding: 20px;'>
    <p>Dashboard desarrollado para Philip Morris International</p>
    <p>Análisis de Performance de Operadores y Máquinas KDF</p>
    <p>© 2025 - PMI Operations Analytics</p>
</div>
""", unsafe_allow_html=True)
