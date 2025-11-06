import streamlit as st
import pandas as pd
from Scripts.asignacion import asignar_operadores

st.set_page_config(page_title="Asignación de Operadores y Coordinadores")
st.title("Asignación de Operadores y Coordinadores")

# Verificar si los datos limpios están disponibles
if 'df_limpio' not in st.session_state:
    st.warning("Primero debes subir y validar un archivo en la página de carga.")
    st.stop()

# Cargar archivo fijo de asignación
try:
    df_asignacion = pd.read_csv("data/operators_assignments.csv")

    # Validar columnas requeridas
    columnas_requeridas = ['Operador', 'Coordinador', 'Fecha_Inicio', 'Fecha_Fin', 'Turno', 'Maquina']
    columnas_faltantes = [col for col in columnas_requeridas if col not in df_asignacion.columns]

    if columnas_faltantes:
        st.error(f"El archivo de asignación no contiene las siguientes columnas requeridas: {columnas_faltantes}")
        st.stop()
    else:
        st.success("Archivo de asignación cargado correctamente.")

except Exception as e:
    st.error(f"Error al cargar el archivo de asignación: {e}")
    st.stop()

# Asignar operadores y coordinadores
df_limpio = st.session_state['df_limpio']
df_asignado = asignar_operadores(df_limpio, df_asignacion)

# Mostrar resultados
st.subheader("Datos con Operadores y Coordinadores Asignados")
st.dataframe(df_asignado)

# Guardar en session_state para uso posterior
st.session_state['df_asignado'] = df_asignado