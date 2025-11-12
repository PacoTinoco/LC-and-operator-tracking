"""
Análisis de Operadores - Deep Dive Individual
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from Config.constants import INDICADORES, TURNOS, COLOR_PALETTE
from utils import (
    load_from_session_state,
    calculate_week_average,
    get_kpi_direction,
    calculate_percentile_rank,
    calculate_trend,
    create_line_chart,
    create_bar_chart,
    create_histogram,
    create_box_plot,
    create_heatmap,
    create_scatter_plot
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Operadores - PMI",
    page_icon="👷",
    layout="wide"
)
st.sidebar.image("assets/logo.png", use_column_width=True)

# Verificar datos cargados
data = load_from_session_state()

if data is None:
    st.warning("⚠️ No hay datos cargados")
    st.info("👉 Por favor, ve a la sección '📤 Carga de Datos' para subir archivos")
    if st.button("Ir a Carga de Datos"):
        st.switch_page("pages/1_📤_Carga_de_Datos.py")
    st.stop()

# Título
st.title("👷 Análisis de Operadores")
st.markdown("### Performance Individual Detallado")

st.markdown("---")

# ============================================
# SELECCIÓN DE OPERADOR
# ============================================

# Obtener lista de operadores únicos (excluyendo SIN_ASIGNAR)
all_operadores = set()
for df in data.values():
    ops = df[df['operador'] != 'SIN_ASIGNAR']['operador'].unique()
    all_operadores.update(ops)

all_operadores = sorted(list(all_operadores))

if len(all_operadores) == 0:
    st.error("❌ No hay operadores asignados en los datos cargados")
    st.stop()

# Selector de operador en la barra lateral
st.sidebar.header("👤 Selección de Operador")

selected_operador = st.sidebar.selectbox(
    "Selecciona un Operador:",
    options=all_operadores,
    index=0
)

st.sidebar.markdown("---")

# Filtros adicionales
st.sidebar.header("🔍 Filtros")

# Obtener fechas del operador
operador_dates = []
for df in data.values():
    df_op = df[df['operador'] == selected_operador]
    if len(df_op) > 0:
        operador_dates.extend(df_op['fecha'].tolist())

if operador_dates:
    min_date = pd.to_datetime(operador_dates).min()
    max_date = pd.to_datetime(operador_dates).max()
    
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
else:
    st.error("No hay datos para el operador seleccionado")
    st.stop()

# Filtro de turnos
selected_turnos = st.sidebar.multiselect(
    "Turnos",
    options=TURNOS,
    default=TURNOS
)

# Filtrar datos para el operador seleccionado
operador_data = {}
for indicador, df in data.items():
    df_filtered = df[
        (df['operador'] == selected_operador) &
        (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
        (df['fecha'] <= pd.to_datetime(fecha_fin)) &
        (df['turno'].isin(selected_turnos))
    ].copy()
    operador_data[indicador] = df_filtered

# Información del operador
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Info del Operador")

# Obtener información general
total_registros = sum(len(df) for df in operador_data.values())
maquinas_trabajadas = set()
coordinador = None

for df in operador_data.values():
    if len(df) > 0:
        maquinas_trabajadas.update(df['maquina'].unique())
        if coordinador is None and 'coordinador' in df.columns:
            coordinador = df['coordinador'].iloc[0]

st.sidebar.metric("Total Registros", f"{total_registros:,}")
st.sidebar.metric("Máquinas Operadas", len(maquinas_trabajadas))
if coordinador and coordinador != 'SIN_ASIGNAR':
    st.sidebar.info(f"**Line Coordinator:** {coordinador}")

# ============================================
# RESUMEN DEL OPERADOR
# ============================================

st.subheader(f"📊 Resumen de Performance - {selected_operador}")

# KPIs principales en cards
kpi_cols = st.columns(len(operador_data))

operador_stats = {}

for idx, (indicador, df) in enumerate(operador_data.items()):
    with kpi_cols[idx]:
        if len(df) > 0:
            avg_value = df[indicador].mean()
            operador_stats[indicador] = avg_value
            
            # Calcular percentil vs todos los operadores
            all_data = data[indicador][data[indicador]['operador'] != 'SIN_ASIGNAR']
            percentile = calculate_percentile_rank(all_data, indicador, avg_value)
            
            # Determinar si es top performer
            better_direction = get_kpi_direction(indicador)
            is_top = (percentile >= 75 and better_direction == 'alto') or (percentile <= 25 and better_direction == 'bajo')
            
            # Calcular tendencia
            if len(df) > 1:
                tendencia = calculate_trend(df, indicador)
                trend_icon = "📈" if tendencia == "mejorando" else "📉" if tendencia == "empeorando" else "➡️"
            else:
                trend_icon = "➡️"
            
            unidad = INDICADORES[indicador]['unidad']
            
            st.metric(
                label=f"**{indicador}**",
                value=f"{avg_value:.2f} {unidad}",
                delta=f"{trend_icon} Percentil {percentile:.0f}"
            )
            
            # Badge si es top performer
            if is_top:
                st.success("🏆 Top Performer")
            
            st.caption(f"{len(df):,} registros")
        else:
            st.info("Sin datos")

st.markdown("---")

# ============================================
# EVOLUCIÓN TEMPORAL POR KPI
# ============================================

st.subheader("📈 Evolución Temporal")

# Tabs para cada indicador
evolution_tabs = st.tabs([f"{ind}" for ind in operador_data.keys()])

for idx, (indicador, df) in enumerate(operador_data.items()):
    with evolution_tabs[idx]:
        if len(df) > 0:
            # Gráfico de línea con comparativa vs promedio general
            fig = create_line_chart(
                df=df.sort_values('fecha'),
                x_col='fecha_str',
                y_col=indicador,
                title=f"Evolución de {indicador} - {selected_operador}",
                x_label="Fecha",
                y_label=indicador,
                show_range_slider=True
            )
            
            # Agregar línea de promedio del operador
            avg_operador = df[indicador].mean()
            fig.add_hline(
                y=avg_operador,
                line_dash="dash",
                line_color="blue",
                annotation_text=f"Promedio Operador: {avg_operador:.2f}",
                annotation_position="left"
            )
            
            # Agregar línea de promedio general
            all_data = data[indicador][data[indicador]['operador'] != 'SIN_ASIGNAR']
            avg_general = all_data[indicador].mean()
            fig.add_hline(
                y=avg_general,
                line_dash="dot",
                line_color="red",
                annotation_text=f"Promedio General: {avg_general:.2f}",
                annotation_position="right"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas comparativas
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("Promedio Operador", f"{avg_operador:.2f}")
            with col_stat2:
                st.metric("Promedio General", f"{avg_general:.2f}")
            with col_stat3:
                diff = avg_operador - avg_general
                better = get_kpi_direction(indicador)
                is_better = (diff > 0 and better == 'alto') or (diff < 0 and better == 'bajo')
                st.metric(
                    "Diferencia", 
                    f"{diff:+.2f}",
                    delta="Mejor" if is_better else "Peor"
                )
            with col_stat4:
                st.metric("Desv. Est.", f"{df[indicador].std():.2f}")
        else:
            st.info("No hay datos disponibles para este indicador en el periodo seleccionado")

st.markdown("---")

# ============================================
# PERFORMANCE POR MÁQUINA
# ============================================

st.subheader("⚙️ Performance por Máquina")

# Selector de KPI
col_maq_kpi, col_empty1 = st.columns([1, 3])
with col_maq_kpi:
    maq_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(operador_data.keys())
    )

df_maq = operador_data[maq_kpi]

if len(df_maq) > 0 and df_maq['maquina'].nunique() > 0:
    # Calcular promedio por máquina
    maq_avg = df_maq.groupby('maquina')[maq_kpi].agg(['mean', 'count', 'std']).reset_index()
    maq_avg.columns = ['maquina', 'promedio', 'registros', 'desv_est']
    maq_avg = maq_avg.sort_values('promedio', ascending=False)
    
    # Gráfico de barras
    fig = create_bar_chart(
        df=maq_avg,
        x_col='maquina',
        y_col='promedio',
        title=f"Promedio de {maq_kpi} por Máquina - {selected_operador}",
        x_label="Máquina",
        y_label=maq_kpi
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla detallada
    col_table1, col_table2 = st.columns([2, 1])
    
    with col_table1:
        st.markdown("**📋 Detalle por Máquina:**")
        st.dataframe(
            maq_avg.style.background_gradient(subset=['promedio'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )
    
    with col_table2:
        # Identificar mejor y peor máquina
        best_maq = maq_avg.iloc[0]['maquina']
        worst_maq = maq_avg.iloc[-1]['maquina']
        
        st.markdown("**🏆 Mejor Máquina:**")
        st.success(f"{best_maq}: {maq_avg.iloc[0]['promedio']:.2f}")
        
        st.markdown("**⚠️ Máquina con Mayor Oportunidad:**")
        st.warning(f"{worst_maq}: {maq_avg.iloc[-1]['promedio']:.2f}")
else:
    st.info("El operador no tiene datos suficientes para analizar por máquina")

st.markdown("---")

# ============================================
# PERFORMANCE POR TURNO
# ============================================

st.subheader("🔄 Performance por Turno")

# Selector de KPI
col_turno_kpi, col_empty2 = st.columns([1, 3])
with col_turno_kpi:
    turno_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(operador_data.keys()),
        key='turno_kpi'
    )

df_turno = operador_data[turno_kpi]

if len(df_turno) > 0:
    col_graph, col_box = st.columns([2, 1])
    
    with col_graph:
        # Gráfico de barras por turno
        turno_avg = df_turno.groupby('turno')[turno_kpi].mean().reset_index()
        turno_avg = turno_avg.sort_values('turno')
        
        fig = create_bar_chart(
            df=turno_avg,
            x_col='turno',
            y_col=turno_kpi,
            title=f"Promedio de {turno_kpi} por Turno",
            x_label="Turno",
            y_label=turno_kpi
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_box:
        # Box plot para ver distribución
        fig_box = create_box_plot(
            df=df_turno,
            y_col=turno_kpi,
            x_col='turno',
            title="Distribución por Turno",
            y_label=turno_kpi
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Estadísticas por turno
    st.markdown("**📊 Estadísticas por Turno:**")
    turno_stats = df_turno.groupby('turno').agg({
        turno_kpi: ['mean', 'std', 'min', 'max', 'count']
    }).reset_index()
    turno_stats.columns = ['Turno', 'Promedio', 'Desv.Est', 'Mínimo', 'Máximo', 'Registros']
    
    st.dataframe(
        turno_stats.style.background_gradient(subset=['Promedio'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# ============================================
# COMPARATIVA CON OTROS OPERADORES
# ============================================

st.subheader("👥 Comparativa con Otros Operadores")

col_comp_kpi, col_comp_ops = st.columns([1, 2])

with col_comp_kpi:
    comp_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(operador_data.keys()),
        key='comp_kpi'
    )

with col_comp_ops:
    # Obtener otros operadores
    other_ops = [op for op in all_operadores if op != selected_operador]
    selected_compare_ops = st.multiselect(
        "Selecciona operadores para comparar:",
        options=other_ops,
        default=other_ops[:3] if len(other_ops) >= 3 else other_ops
    )

if selected_compare_ops:
    # Preparar datos para comparación
    compare_data = []
    
    # Datos del operador seleccionado
    df_selected = operador_data[comp_kpi]
    if len(df_selected) > 0:
        compare_data.append({
            'operador': selected_operador,
            'promedio': df_selected[comp_kpi].mean(),
            'desv_est': df_selected[comp_kpi].std(),
            'registros': len(df_selected)
        })
    
    # Datos de operadores comparados
    df_all = data[comp_kpi][data[comp_kpi]['operador'] != 'SIN_ASIGNAR']
    for op in selected_compare_ops:
        df_op = df_all[df_all['operador'] == op]
        if len(df_op) > 0:
            compare_data.append({
                'operador': op,
                'promedio': df_op[comp_kpi].mean(),
                'desv_est': df_op[comp_kpi].std(),
                'registros': len(df_op)
            })
    
    if compare_data:
        df_compare = pd.DataFrame(compare_data)
        df_compare = df_compare.sort_values('promedio', ascending=False)
        
        # Gráfico de barras comparativo
        fig = create_bar_chart(
            df=df_compare,
            x_col='operador',
            y_col='promedio',
            title=f"Comparativa de {comp_kpi} entre Operadores",
            x_label="Operador",
            y_label=comp_kpi,
            orientation='v'
        )
        
        # Resaltar operador seleccionado
        colors = ['#FF6B6B' if op == selected_operador else '#4ECDC4' for op in df_compare['operador']]
        fig.data[0].marker.color = colors
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla comparativa
        st.markdown("**📋 Tabla Comparativa:**")
        st.dataframe(
            df_compare.style.background_gradient(subset=['promedio'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )

st.markdown("---")

# ============================================
# RESUMEN Y RECOMENDACIONES
# ============================================

st.subheader("📝 Resumen y Observaciones")

col_summary1, col_summary2 = st.columns(2)

with col_summary1:
    st.markdown("**💪 Fortalezas Identificadas:**")
    
    fortalezas = []
    for indicador, df in operador_data.items():
        if len(df) > 0:
            avg_op = df[indicador].mean()
            all_data = data[indicador][data[indicador]['operador'] != 'SIN_ASIGNAR']
            avg_gen = all_data[indicador].mean()
            
            better = get_kpi_direction(indicador)
            is_strong = (avg_op > avg_gen and better == 'alto') or (avg_op < avg_gen and better == 'bajo')
            
            if is_strong:
                diff_pct = abs((avg_op - avg_gen) / avg_gen * 100)
                fortalezas.append(f"- **{indicador}**: {diff_pct:.1f}% mejor que promedio")
    
    if fortalezas:
        for f in fortalezas:
            st.success(f)
    else:
        st.info("Performance en línea con el promedio general")

with col_summary2:
    st.markdown("**🎯 Oportunidades de Mejora:**")
    
    oportunidades = []
    for indicador, df in operador_data.items():
        if len(df) > 0:
            avg_op = df[indicador].mean()
            all_data = data[indicador][data[indicador]['operador'] != 'SIN_ASIGNAR']
            avg_gen = all_data[indicador].mean()
            
            better = get_kpi_direction(indicador)
            needs_improvement = (avg_op < avg_gen and better == 'alto') or (avg_op > avg_gen and better == 'bajo')
            
            if needs_improvement:
                diff_pct = abs((avg_op - avg_gen) / avg_gen * 100)
                oportunidades.append(f"- **{indicador}**: {diff_pct:.1f}% por debajo del promedio")
    
    if oportunidades:
        for o in oportunidades:
            st.warning(o)
    else:
        st.info("No se identificaron áreas críticas de mejora")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Análisis Individual de Operador - Philip Morris International</p>
    <p>Datos actualizados al {}</p>
</div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)