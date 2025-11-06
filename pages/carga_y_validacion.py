import sys
import os
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scripts.limpieza import limpiar_datos

st.set_page_config(page_title="Carga y Validación de Indicadores")
st.title("Carga y Validación de Indicadores")

# Selección de máquina antes de subir archivo
maquinas_disponibles = ["KDF7", "KDF8", "KDF9", "KDF10 (MULFI)", "KDF11", "KDF17"]
maquina_seleccionada = st.selectbox("Selecciona la máquina correspondiente al archivo", maquinas_disponibles)

# Subida de archivo
archivo = st.file_uploader("Sube tu archivo de indicador", type=["xlsx", "csv"])

if archivo and maquina_seleccionada:
    try:
        # Procesar archivo con función de limpieza
        df_limpio, indicador = limpiar_datos(archivo)

        # Asignar máquina seleccionada como nueva columna
        df_limpio['Maquina'] = maquina_seleccionada

        # Mostrar resultados
        st.success(f"Archivo procesado correctamente como indicador: {indicador}")
        st.dataframe(df_limpio)

        # Guardar en session_state para otras páginas
        st.session_state['df_limpio'] = df_limpio
        st.session_state['indicador'] = indicador

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")