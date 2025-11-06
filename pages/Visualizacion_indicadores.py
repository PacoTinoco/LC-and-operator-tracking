import streamlit as st
from Scripts.visualizaciones import filtrar_y_visualizar

st.set_page_config(page_title="Visualización de Indicadores")
st.title("Visualización de Indicadores")

if 'df_asignado' not in st.session_state:
    st.warning("Primero debes asignar operadores y coordinadores en la página de asignación.")
    st.stop()

# Obtener datos desde session_state
df_asignado = st.session_state.get('df_asignado')
indicador = st.session_state['indicador']

# Obtener listas únicas para filtros
lcs = df_asignado['Coordinador'].dropna().unique().tolist()
operadores = df_asignado['Operador'].dropna().unique().tolist()
maquinas = df_asignado['Maquina'].dropna().unique().tolist()
min_fecha = df_asignado['Fecha'].min()
max_fecha = df_asignado['Fecha'].max()

# Filtros en barra lateral
st.sidebar.subheader("Filtros")
lcs_seleccionados = st.sidebar.multiselect("Selecciona LC", lcs, default=lcs)
operadores_seleccionados = st.sidebar.multiselect("Selecciona Operadores", operadores, default=operadores)
maquinas_seleccionadas = st.sidebar.multiselect("Selecciona Máquinas", maquinas, default=maquinas)
fecha_inicio, fecha_fin = st.sidebar.slider("Rango de fechas", min_value=min_fecha, max_value=max_fecha, value=(min_fecha, max_fecha))

# Botón para generar visualización
if st.sidebar.button("Generar Visualización"):
    resultados = filtrar_y_visualizar(
        df_asignado,
        indicador,
        lcs_seleccionados,
        operadores_seleccionados,
        maquinas_seleccionadas,
        fecha_inicio,
        fecha_fin
    )

    st.subheader("Performance por Turno")
    st.plotly_chart(resultados['fig_turno'])

    st.subheader("Performance Combinado por Mes")
    st.plotly_chart(resultados['fig_combinado'])

    st.subheader("Comparación por LC")
    st.plotly_chart(resultados['fig_lc'])