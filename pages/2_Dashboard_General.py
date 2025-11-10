"""
Dashboard General - Vista Ejecutiva de KPIs
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from Config.constants import INDICADORES, MAQUINAS, TURNOS, COLOR_PALETTE
from utils import (
    load_from_session_state,
    calculate_week_average,
    calculate_month_average,
    get_kpi_direction,
    calculate_trend,
    create_line_chart,
    create_bar_chart,
    create_heatmap,
    create_gauge_chart,
    create_multi_line_comparison,
    create_week_performance_chart,
    create_operator_ranking
)

# Configuración de la página
st.set_page_config(
    page_title="Dashboard General - PMI",
    page_icon="📊",
    layout="wide"
)
# Verificar datos cargados
data = load_from_session_state()

if data is None:
    st.warning("⚠️ No hay datos cargados")
    st.info("👉 Por favor, ve a la sección '📤 Carga de Datos' para subir archivos")
    if st.button("Ir a Carga de Datos"):
        st.switch_page("pages/1_📤_Carga_de_Datos.py")
    st.stop()

# Título
st.title("📊 Dashboard General")
st.markdown("### Vista Ejecutiva de Performance")

st.markdown("---")

# ============================================
# FILTROS GLOBALES
# ============================================
st.sidebar.header("🔍 Filtros")

# Obtener todas las fechas disponibles
all_dates = pd.concat([df['fecha'] for df in data.values()]).unique()
min_date = pd.to_datetime(all_dates).min()
max_date = pd.to_datetime(all_dates).max()

# Filtro de rango de fechas
date_range = st.sidebar.date_input(
    "Rango de Fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    fecha_inicio, fecha_fin = date_range
else:
    fecha_inicio, fecha_fin = min_date, max_date

# Filtro de máquinas
all_maquinas = pd.concat([df['maquina'] for df in data.values()]).unique().tolist()
selected_maquinas = st.sidebar.multiselect(
    "Máquinas",
    options=sorted(all_maquinas),
    default=sorted(all_maquinas)
)

# Filtro de turnos
selected_turnos = st.sidebar.multiselect(
    "Turnos",
    options=TURNOS,
    default=TURNOS
)

# Aplicar filtros a todos los DataFrames
filtered_data = {}
for indicador, df in data.items():
    df_filtered = df[
        (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
        (df['fecha'] <= pd.to_datetime(fecha_fin)) &
        (df['maquina'].isin(selected_maquinas)) &
        (df['turno'].isin(selected_turnos))
    ].copy()
    filtered_data[indicador] = df_filtered

st.sidebar.markdown("---")
st.sidebar.info(f"📅 Periodo: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")

# ============================================
# MÉTRICAS PRINCIPALES (KPI CARDS)
# ============================================
st.subheader("🎯 Métricas Principales")

# Crear columnas para KPIs
kpi_cols = st.columns(len(filtered_data))

for idx, (indicador, df) in enumerate(filtered_data.items()):
    if len(df) > 0:
        with kpi_cols[idx]:
            # Calcular promedio
            avg_value = df[indicador].mean()
            
            # Calcular tendencia
            if len(df) > 1:
                tendencia = calculate_trend(df, indicador)
                delta_icon = "📈" if tendencia == "mejorando" else "📉" if tendencia == "empeorando" else "➡️"
            else:
                tendencia = "N/A"
                delta_icon = "➡️"
            
            # Determinar color según dirección del KPI
            better_direction = get_kpi_direction(indicador)
            
            # Unidad
            unidad = INDICADORES[indicador]['unidad']
            
            # Mostrar métrica
            st.metric(
                label=f"**{indicador}**",
                value=f"{avg_value:.2f} {unidad}",
                delta=f"{delta_icon} {tendencia}"
            )
            
            # Mini descripción
            st.caption(f"{len(df):,} registros • {df['maquina'].nunique()} máquinas")

st.markdown("---")

# ============================================
# GAUGE CHARTS (Velocímetros)
# ============================================
st.subheader("🎛️ Indicadores de Performance")

gauge_cols = st.columns(len(filtered_data))

for idx, (indicador, df) in enumerate(filtered_data.items()):
    if len(df) > 0:
        with gauge_cols[idx]:
            avg_value = df[indicador].mean()
            min_val = df[indicador].min()
            max_val = df[indicador].max()
            
            # Ajustar umbrales según dirección
            better_direction = get_kpi_direction(indicador)
            
            if better_direction == 'alto':
                # Para KPIs donde alto es mejor (MTBF, Strategic PR)
                threshold_red = min_val + (max_val - min_val) * 0.33
                threshold_yellow = min_val + (max_val - min_val) * 0.66
            else:
                # Para KPIs donde bajo es mejor (UPDT, Reject Rate)
                threshold_red = min_val + (max_val - min_val) * 0.66
                threshold_yellow = min_val + (max_val - min_val) * 0.33
            
            fig = create_gauge_chart(
                value=avg_value,
                title=indicador,
                min_val=min_val,
                max_val=max_val,
                threshold_red=threshold_red,
                threshold_yellow=threshold_yellow
            )
            
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================
# PERFORMANCE POR WEEK (Gráficos de Línea)
# ============================================
st.subheader("📈 Evolución por Week")

# Tabs para cada indicador
week_tabs = st.tabs([f"{ind}" for ind in filtered_data.keys()])

for idx, (indicador, df) in enumerate(filtered_data.items()):
    with week_tabs[idx]:
        if len(df) > 0:
            better_direction = get_kpi_direction(indicador)
            
            fig = create_week_performance_chart(
                df=df,
                kpi_col=indicador,
                kpi_name=indicador,
                better_direction=better_direction
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas rápidas
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("Promedio", f"{df[indicador].mean():.2f}")
            with col_stat2:
                st.metric("Mejor Week", f"{df.groupby('week')[indicador].mean().max():.2f}")
            with col_stat3:
                st.metric("Peor Week", f"{df.groupby('week')[indicador].mean().min():.2f}")
            with col_stat4:
                st.metric("Desv. Est.", f"{df[indicador].std():.2f}")
        else:
            st.info("No hay datos disponibles para este indicador")

st.markdown("---")

# ============================================
# COMPARATIVA POR MÁQUINA (Bar Chart)
# ============================================
st.subheader("⚙️ Comparativa por Máquina")

# Selector de indicador
col_selector, col_empty = st.columns([1, 3])
with col_selector:
    selected_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(filtered_data.keys())
    )

df_selected = filtered_data[selected_kpi]

if len(df_selected) > 0:
    # Calcular promedio por máquina
    maquina_avg = df_selected.groupby('maquina')[selected_kpi].mean().reset_index()
    maquina_avg = maquina_avg.sort_values(selected_kpi, ascending=False)
    
    fig = create_bar_chart(
        df=maquina_avg,
        x_col='maquina',
        y_col=selected_kpi,
        title=f"Promedio de {selected_kpi} por Máquina",
        x_label="Máquina",
        y_label=selected_kpi
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar tabla de datos
    with st.expander("📋 Ver datos detallados"):
        st.dataframe(
            maquina_avg.style.background_gradient(subset=[selected_kpi], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )

st.markdown("---")

# ============================================
# HEATMAP: MÁQUINA x TURNO
# ============================================
st.subheader("🔥 Heatmap: Máquina vs Turno")

col_heatmap_kpi, col_empty2 = st.columns([1, 3])
with col_heatmap_kpi:
    heatmap_kpi = st.selectbox(
        "Selecciona KPI para Heatmap:",
        options=list(filtered_data.keys()),
        key='heatmap_kpi'
    )

df_heatmap = filtered_data[heatmap_kpi]

if len(df_heatmap) > 0:
    # Determinar escala de color según dirección del KPI
    better_direction = get_kpi_direction(heatmap_kpi)
    colorscale = 'RdYlGn' if better_direction == 'alto' else 'RdYlGn_r'
    
    fig = create_heatmap(
        df=df_heatmap,
        x_col='turno',
        y_col='maquina',
        value_col=heatmap_kpi,
        title=f"Heatmap: {heatmap_kpi} por Máquina y Turno",
        colorscale=colorscale
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("💡 **Interpretación**: Los colores muestran el promedio del KPI. Verde = mejor performance, Rojo = peor performance")

st.markdown("---")

# ============================================
# TOP OPERADORES
# ============================================
st.subheader("🏆 Top Operadores")

col_top_kpi, col_top_n = st.columns([2, 1])

with col_top_kpi:
    top_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(filtered_data.keys()),
        key='top_kpi'
    )

with col_top_n:
    top_n = st.number_input(
        "Cantidad a mostrar:",
        min_value=5,
        max_value=15,
        value=10,
        step=1
    )

df_top = filtered_data[top_kpi]

if len(df_top) > 0:
    # Filtrar operadores sin asignar
    df_top = df_top[df_top['operador'] != 'SIN_ASIGNAR']
    
    if len(df_top) > 0:
        fig = create_operator_ranking(
            df=df_top,
            kpi_col=top_kpi,
            kpi_name=top_kpi,
            top_n=top_n
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar tabla con detalles
        with st.expander("📊 Ver estadísticas detalladas"):
            op_stats = df_top.groupby('operador').agg({
                top_kpi: ['mean', 'std', 'count'],
                'maquina': lambda x: ', '.join(x.unique())
            }).reset_index()
            
            op_stats.columns = ['Operador', 'Promedio', 'Desv.Est', 'Registros', 'Máquinas']
            op_stats = op_stats.sort_values('Promedio', ascending=False).head(top_n)
            
            st.dataframe(
                op_stats.style.background_gradient(subset=['Promedio'], cmap='RdYlGn'),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("No hay operadores asignados en el periodo seleccionado")

st.markdown("---")


# ============================================
# RESUMEN ESTADÍSTICO
# ============================================
st.subheader("📈 Resumen Estadístico")

summary_tabs = st.tabs([f"{ind}" for ind in filtered_data.keys()])

for idx, (indicador, df) in enumerate(filtered_data.items()):
    with summary_tabs[idx]:
        if len(df) > 0:
            col_sum1, col_sum2, col_sum3 = st.columns(3)
            
            with col_sum1:
                st.markdown("**Estadísticas Generales**")
                st.metric("Total Registros", f"{len(df):,}")
                st.metric("Promedio", f"{df[indicador].mean():.2f}")
                st.metric("Mediana", f"{df[indicador].median():.2f}")
                st.metric("Desviación Estándar", f"{df[indicador].std():.2f}")
            
            with col_sum2:
                st.markdown("**Valores Extremos**")
                st.metric("Valor Máximo", f"{df[indicador].max():.2f}")
                st.metric("Valor Mínimo", f"{df[indicador].min():.2f}")
                st.metric("Rango", f"{df[indicador].max() - df[indicador].min():.2f}")
                st.metric("Percentil 95", f"{df[indicador].quantile(0.95):.2f}")
            
            with col_sum3:
                st.markdown("**Cobertura de Datos**")
                st.metric("Máquinas", df['maquina'].nunique())
                st.metric("Operadores", df['operador'].nunique())
                st.metric("Weeks", df['week'].nunique())
                st.metric("Días con Datos", df['fecha'].nunique())
        else:
            st.info("No hay datos disponibles para este indicador")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Dashboard General - Philip Morris International</p>
    <p>Datos actualizados al {}</p>
</div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)