"""
Análisis de Máquinas - Deep Dive por Equipo
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from Config.constants import INDICADORES, TURNOS, MAQUINAS, COLOR_PALETTE
from utils import (
    load_from_session_state,
    calculate_week_average,
    get_kpi_direction,
    calculate_trend,
    identify_outliers,
    create_line_chart,
    create_bar_chart,
    create_histogram,
    create_box_plot,
    create_heatmap,
    create_scatter_plot,
    create_multi_line_comparison,
    create_operator_ranking,
    create_week_performance_chart
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Máquinas - PMI",
    page_icon="⚙️",
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
st.title("⚙️ Análisis de Máquinas")
st.markdown("### Deep Dive por Equipo KDF")

st.markdown("---")

# ============================================
# SELECCIÓN DE MÁQUINA
# ============================================

# Obtener lista de máquinas disponibles en los datos
available_machines = set()
for df in data.values():
    machines = df['maquina'].unique()
    available_machines.update(machines)

available_machines = sorted(list(available_machines))

if len(available_machines) == 0:
    st.error("❌ No hay máquinas disponibles en los datos cargados")
    st.stop()

# Selector de máquina en la barra lateral
st.sidebar.header("⚙️ Selección de Máquina")

selected_machine = st.sidebar.selectbox(
    "Selecciona una Máquina:",
    options=available_machines,
    index=0
)

st.sidebar.markdown("---")

# Filtros adicionales
st.sidebar.header("🔍 Filtros")

# Obtener fechas de la máquina
machine_dates = []
for df in data.values():
    df_maq = df[df['maquina'] == selected_machine]
    if len(df_maq) > 0:
        machine_dates.extend(df_maq['fecha'].tolist())

if machine_dates:
    min_date = pd.to_datetime(machine_dates).min()
    max_date = pd.to_datetime(machine_dates).max()
    
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
    st.error("No hay datos para la máquina seleccionada")
    st.stop()

# Filtro de turnos
selected_turnos = st.sidebar.multiselect(
    "Turnos",
    options=TURNOS,
    default=TURNOS
)

# Filtrar datos para la máquina seleccionada
machine_data = {}
for indicador, df in data.items():
    df_filtered = df[
        (df['maquina'] == selected_machine) &
        (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
        (df['fecha'] <= pd.to_datetime(fecha_fin)) &
        (df['turno'].isin(selected_turnos))
    ].copy()
    machine_data[indicador] = df_filtered

# Información de la máquina
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Info de la Máquina")

# Obtener información general
total_registros = sum(len(df) for df in machine_data.values())
operadores_trabajados = set()

for df in machine_data.values():
    if len(df) > 0:
        operadores_trabajados.update(df[df['operador'] != 'SIN_ASIGNAR']['operador'].unique())

st.sidebar.metric("Total Registros", f"{total_registros:,}")
st.sidebar.metric("Operadores Diferentes", len(operadores_trabajados))
st.sidebar.metric("Periodo", f"{(fecha_fin - fecha_inicio).days} días")

# ============================================
# RESUMEN DE LA MÁQUINA
# ============================================

st.subheader(f"📊 Resumen de Performance - {selected_machine}")

# KPIs principales en cards
kpi_cols = st.columns(len(machine_data))

machine_stats = {}

for idx, (indicador, df) in enumerate(machine_data.items()):
    with kpi_cols[idx]:
        if len(df) > 0:
            avg_value = df[indicador].mean()
            machine_stats[indicador] = avg_value
            
            # Comparar con promedio de todas las máquinas
            all_machines_avg = data[indicador][indicador].mean()
            diff = avg_value - all_machines_avg
            
            # Calcular tendencia
            if len(df) > 1:
                tendencia = calculate_trend(df, indicador)
                trend_icon = "📈" if tendencia == "mejorando" else "📉" if tendencia == "empeorando" else "➡️"
            else:
                trend_icon = "➡️"
            
            # Determinar si está mejor o peor que el promedio
            better_direction = get_kpi_direction(indicador)
            is_better = (diff > 0 and better_direction == 'alto') or (diff < 0 and better_direction == 'bajo')
            
            unidad = INDICADORES[indicador]['unidad']
            
            st.metric(
                label=f"**{indicador}**",
                value=f"{avg_value:.2f} {unidad}",
                delta=f"{diff:+.2f} vs general {trend_icon}"
            )
            
            # Badge de performance
            if is_better:
                st.success("✅ Sobre promedio")
            else:
                st.warning("⚠️ Bajo promedio")
            
            st.caption(f"{len(df):,} registros")
        else:
            st.info("Sin datos")

st.markdown("---")

# ============================================
# ANÁLISIS INDIVIDUAL POR KPI
# ============================================

st.subheader("🔍 Análisis Detallado por KPI")

# Tabs para cada indicador
kpi_tabs = st.tabs([f"{ind}" for ind in machine_data.keys()])

for idx, (indicador, df) in enumerate(machine_data.items()):
    with kpi_tabs[idx]:
        if len(df) > 0:
            col_evolution, col_distribution = st.columns([2, 1])
            
            with col_evolution:
                # Gráfico de evolución por week
                better_direction = get_kpi_direction(indicador)
                
                fig = create_week_performance_chart(
                    df=df,
                    kpi_col=indicador,
                    kpi_name=indicador,
                    better_direction=better_direction
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col_distribution:
                # Histograma de distribución
                fig_hist = create_histogram(
                    df=df,
                    column=indicador,
                    title=f"Distribución de {indicador}",
                    x_label=indicador,
                    bins=25,
                    color=COLOR_PALETTE['kpis'].get(indicador, COLOR_PALETTE['primary'])
                )
                
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Estadísticas detalladas
            st.markdown(f"**📊 Estadísticas de {indicador}:**")
            
            stat_cols = st.columns(6)
            
            with stat_cols[0]:
                st.metric("Promedio", f"{df[indicador].mean():.2f}")
            with stat_cols[1]:
                st.metric("Mediana", f"{df[indicador].median():.2f}")
            with stat_cols[2]:
                st.metric("Desv. Est.", f"{df[indicador].std():.2f}")
            with stat_cols[3]:
                st.metric("Mínimo", f"{df[indicador].min():.2f}")
            with stat_cols[4]:
                st.metric("Máximo", f"{df[indicador].max():.2f}")
            with stat_cols[5]:
                st.metric("Rango", f"{df[indicador].max() - df[indicador].min():.2f}")
            
            # Detectar outliers
            df_outliers = identify_outliers(df.copy(), indicador)
            n_outliers = df_outliers['is_outlier'].sum()
            
            if n_outliers > 0:
                st.warning(f"⚠️ Se detectaron **{n_outliers}** valores atípicos ({n_outliers/len(df)*100:.1f}%)")
                
                with st.expander("Ver outliers detectados"):
                    df_outliers_only = df_outliers[df_outliers['is_outlier']]
                    st.dataframe(
                        df_outliers_only[['fecha_str', 'turno', 'operador', indicador]],
                        use_container_width=True,
                        hide_index=True
                    )
        else:
            st.info("No hay datos disponibles para este indicador")

st.markdown("---")

# ============================================
# PERFORMANCE POR OPERADOR
# ============================================

st.subheader("👷 Performance de Operadores en esta Máquina")

# Selector de KPI
col_op_kpi, col_op_n = st.columns([2, 1])

with col_op_kpi:
    operator_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(machine_data.keys())
    )

with col_op_n:
    top_n_ops = st.number_input(
        "Top N operadores:",
        min_value=5,
        max_value=15,
        value=10,
        step=1
    )

df_ops = machine_data[operator_kpi]

if len(df_ops) > 0:
    # Filtrar operadores asignados
    df_ops_assigned = df_ops[df_ops['operador'] != 'SIN_ASIGNAR']
    
    if len(df_ops_assigned) > 0:
        # Ranking de operadores
        fig_rank = create_operator_ranking(
            df=df_ops_assigned,
            kpi_col=operator_kpi,
            kpi_name=operator_kpi,
            top_n=top_n_ops
        )
        
        st.plotly_chart(fig_rank, use_container_width=True)
        
        # Tabla detallada de operadores
        op_stats = df_ops_assigned.groupby('operador').agg({
            operator_kpi: ['mean', 'std', 'min', 'max', 'count']
        }).reset_index()
        
        op_stats.columns = ['Operador', 'Promedio', 'Desv.Est', 'Mínimo', 'Máximo', 'Registros']
        op_stats = op_stats.sort_values('Promedio', ascending=False).head(top_n_ops)
        
        st.markdown("**📋 Estadísticas Detalladas:**")
        st.dataframe(
            op_stats.style.background_gradient(subset=['Promedio'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )
        
        # Análisis de variabilidad entre operadores
        st.markdown("**📊 Análisis de Variabilidad:**")
        
        overall_mean = df_ops_assigned[operator_kpi].mean()
        between_op_std = op_stats['Promedio'].std()
        within_op_std = op_stats['Desv.Est'].mean()
        
        col_var1, col_var2, col_var3 = st.columns(3)
        
        with col_var1:
            st.metric("Promedio General", f"{overall_mean:.2f}")
        with col_var2:
            st.metric("Variabilidad Entre Operadores", f"{between_op_std:.2f}")
        with col_var3:
            st.metric("Variabilidad Promedio Intra-Operador", f"{within_op_std:.2f}")
        
        # Interpretación
        if between_op_std > within_op_std:
            st.info("💡 La variabilidad **entre operadores** es mayor que la variabilidad de cada operador. Esto sugiere que algunos operadores son consistentemente mejores/peores.")
        else:
            st.info("💡 La variabilidad **intra-operador** es mayor. Esto sugiere que factores externos (materiales, condiciones, etc.) tienen más impacto que el operador.")
    else:
        st.warning("No hay operadores asignados en el periodo seleccionado")
else:
    st.info("No hay datos suficientes")

st.markdown("---")

# ============================================
# PERFORMANCE POR TURNO
# ============================================

st.subheader("🔄 Análisis por Turno")

# Selector de KPI
col_turno_kpi, col_empty = st.columns([1, 3])
with col_turno_kpi:
    turno_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(machine_data.keys()),
        key='turno_kpi'
    )

df_turno = machine_data[turno_kpi]

if len(df_turno) > 0:
    col_turno_bar, col_turno_box, col_turno_heat = st.columns([1, 1, 1])
    
    with col_turno_bar:
        # Promedio por turno
        turno_avg = df_turno.groupby('turno')[turno_kpi].mean().reset_index()
        
        fig_turno = create_bar_chart(
            df=turno_avg,
            x_col='turno',
            y_col=turno_kpi,
            title=f"Promedio por Turno",
            x_label="Turno",
            y_label=turno_kpi
        )
        
        st.plotly_chart(fig_turno, use_container_width=True)
    
    with col_turno_box:
        # Box plot por turno
        fig_box = create_box_plot(
            df=df_turno,
            y_col=turno_kpi,
            x_col='turno',
            title="Distribución por Turno",
            y_label=turno_kpi
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
    
    with col_turno_heat:
        # Evolución por turno (heatmap semana x turno)
        if df_turno['week'].nunique() > 1:
            fig_heat = create_heatmap(
                df=df_turno,
                x_col='turno',
                y_col='week',
                value_col=turno_kpi,
                title="Week x Turno",
                colorscale='RdYlGn' if get_kpi_direction(turno_kpi) == 'alto' else 'RdYlGn_r'
            )
            
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Se necesitan más weeks para generar heatmap")
    
    # Tabla estadística por turno
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
    
    # Identificar mejor y peor turno
    better_direction = get_kpi_direction(turno_kpi)
    
    if better_direction == 'alto':
        best_turno = turno_stats.loc[turno_stats['Promedio'].idxmax(), 'Turno']
        worst_turno = turno_stats.loc[turno_stats['Promedio'].idxmin(), 'Turno']
    else:
        best_turno = turno_stats.loc[turno_stats['Promedio'].idxmin(), 'Turno']
        worst_turno = turno_stats.loc[turno_stats['Promedio'].idxmax(), 'Turno']
    
    col_best, col_worst = st.columns(2)
    
    with col_best:
        st.success(f"🏆 **Mejor Turno**: {best_turno}")
    with col_worst:
        st.warning(f"⚠️ **Turno con Mayor Oportunidad**: {worst_turno}")

st.markdown("---")

# ============================================
# COMPARATIVA CON OTRAS MÁQUINAS
# ============================================

st.subheader("🏭 Comparativa con Otras Máquinas")

col_comp_kpi, col_empty2 = st.columns([1, 3])
with col_comp_kpi:
    comp_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(machine_data.keys()),
        key='comp_kpi'
    )

# Calcular promedio de todas las máquinas
all_machines_data = []

df_all = data[comp_kpi]
for maquina in df_all['maquina'].unique():
    df_maq = df_all[df_all['maquina'] == maquina]
    all_machines_data.append({
        'Máquina': maquina,
        'Promedio': df_maq[comp_kpi].mean(),
        'Desv_Est': df_maq[comp_kpi].std(),
        'Registros': len(df_maq)
    })

if all_machines_data:
    df_comp = pd.DataFrame(all_machines_data)
    df_comp = df_comp.sort_values('Promedio', ascending=False)
    
    # Bar chart comparativo
    fig_comp = create_bar_chart(
        df=df_comp,
        x_col='Máquina',
        y_col='Promedio',
        title=f"Comparativa de {comp_kpi} entre Máquinas",
        x_label="Máquina",
        y_label=comp_kpi
    )
    
    # Resaltar máquina seleccionada
    colors = ['#FF6B6B' if m == selected_machine else '#4ECDC4' for m in df_comp['Máquina']]
    fig_comp.data[0].marker.color = colors
    
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Tabla comparativa
    st.markdown("**📋 Ranking de Máquinas:**")
    
    # Agregar ranking
    df_comp['Ranking'] = range(1, len(df_comp) + 1)
    df_comp = df_comp[['Ranking', 'Máquina', 'Promedio', 'Desv_Est', 'Registros']]
    
    st.dataframe(
        df_comp.style.background_gradient(subset=['Promedio'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )
    
    # Posición de la máquina seleccionada
    machine_rank = df_comp[df_comp['Máquina'] == selected_machine]['Ranking'].values[0]
    total_machines = len(df_comp)
    
    st.info(f"📍 **{selected_machine}** está en la posición **{machine_rank}** de {total_machines} máquinas para {comp_kpi}")

st.markdown("---")

# ============================================
# RESUMEN Y RECOMENDACIONES
# ============================================

st.subheader("📝 Resumen y Recomendaciones")

col_summary1, col_summary2 = st.columns(2)

with col_summary1:
    st.markdown("**💪 Puntos Fuertes:**")
    
    strengths = []
    for indicador, df in machine_data.items():
        if len(df) > 0:
            machine_avg = df[indicador].mean()
            all_avg = data[indicador][indicador].mean()
            
            better = get_kpi_direction(indicador)
            is_strong = (machine_avg > all_avg and better == 'alto') or (machine_avg < all_avg and better == 'bajo')
            
            if is_strong:
                diff_pct = abs((machine_avg - all_avg) / all_avg * 100)
                strengths.append(f"- **{indicador}**: {diff_pct:.1f}% mejor que promedio general")
    
    if strengths:
        for s in strengths:
            st.success(s)
    else:
        st.info("Performance en línea con el promedio general")

with col_summary2:
    st.markdown("**🎯 Oportunidades de Mejora:**")
    
    opportunities = []
    for indicador, df in machine_data.items():
        if len(df) > 0:
            machine_avg = df[indicador].mean()
            all_avg = data[indicador][indicador].mean()
            
            better = get_kpi_direction(indicador)
            needs_improvement = (machine_avg < all_avg and better == 'alto') or (machine_avg > all_avg and better == 'bajo')
            
            if needs_improvement:
                diff_pct = abs((machine_avg - all_avg) / all_avg * 100)
                opportunities.append(f"- **{indicador}**: {diff_pct:.1f}% por debajo del promedio")
    
    if opportunities:
        for o in opportunities:
            st.warning(o)
    else:
        st.info("No se identificaron áreas críticas de mejora")

# Recomendaciones específicas
st.markdown("**💡 Recomendaciones Accionables:**")

recommendations = []

# Análisis de turnos
for indicador, df in machine_data.items():
    if len(df) > 0 and df['turno'].nunique() > 1:
        turno_avg = df.groupby('turno')[indicador].mean()
        better = get_kpi_direction(indicador)
        
        if better == 'alto':
            best_turno = turno_avg.idxmax()
            worst_turno = turno_avg.idxmin()
        else:
            best_turno = turno_avg.idxmin()
            worst_turno = turno_avg.idxmax()
        
        diff = abs(turno_avg[best_turno] - turno_avg[worst_turno])
        if diff / turno_avg.mean() > 0.15:  # Más de 15% de diferencia
            recommendations.append(f"🔄 **{indicador}**: Turno {worst_turno} tiene {diff:.2f} puntos de diferencia vs {best_turno}. Revisar prácticas del turno {best_turno}")

# Análisis de operadores
for indicador, df in machine_data.items():
    if len(df) > 0:
        df_ops = df[df['operador'] != 'SIN_ASIGNAR']
        if len(df_ops) > 0 and df_ops['operador'].nunique() > 2:
            op_avg = df_ops.groupby('operador')[indicador].mean()
            better = get_kpi_direction(indicador)
            
            if better == 'alto':
                best_op = op_avg.idxmax()
                worst_op = op_avg.idxmin()
            else:
                best_op = op_avg.idxmin()
                worst_op = op_avg.idxmax()
            
            diff = abs(op_avg[best_op] - op_avg[worst_op])
            if diff / op_avg.mean() > 0.20:  # Más de 20% de diferencia
                recommendations.append(f"👷 **{indicador}**: Gran variabilidad entre operadores. {best_op} supera a {worst_op} por {diff:.2f}. Considerar entrenamiento cruzado")

# Análisis de variabilidad
for indicador, df in machine_data.items():
    if len(df) > 0:
        cv = (df[indicador].std() / df[indicador].mean()) * 100
        if cv > 30:  # Coeficiente de variación alto
            recommendations.append(f"📊 **{indicador}**: Alta variabilidad detectada (CV={cv:.1f}%). Investigar causas de inconsistencia")

if recommendations:
    for rec in recommendations:
        st.info(rec)
else:
    st.success("✅ La máquina opera de manera estable y consistente")

st.markdown("---")

# ============================================
# DATOS EXPORTABLES
# ============================================

st.subheader("📥 Exportar Datos de la Máquina")

# Selector de KPI para exportar
col_export_kpi, col_export_btn = st.columns([2, 1])

with col_export_kpi:
    export_kpi = st.selectbox(
        "Selecciona KPI para exportar:",
        options=list(machine_data.keys()),
        key='export_kpi'
    )

df_export = machine_data[export_kpi]

if len(df_export) > 0:
    # Preparar datos para exportar
    df_export_clean = df_export[[
        'fecha_str', 'turno', 'operador', 'coordinador', 
        export_kpi, 'week', 'mes_asignado'
    ]].copy()
    
    df_export_clean.columns = [
        'Fecha', 'Turno', 'Operador', 'Coordinador', 
        export_kpi, 'Week', 'Mes'
    ]
    
    # Convertir a CSV
    csv = df_export_clean.to_csv(index=False).encode('utf-8')
    
    with col_export_btn:
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv,
            file_name=f"{selected_machine}_{export_kpi}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
            use_container_width=True
        )
    
    # Preview de datos
    with st.expander("👀 Preview de datos a exportar"):
        st.dataframe(
            df_export_clean.head(20),
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Total de registros: {len(df_export_clean):,}")
else:
    st.info("No hay datos disponibles para exportar")

st.markdown("---")

# ============================================
# MÉTRICAS DE CALIDAD DE DATOS
# ============================================

st.subheader("📊 Calidad de Datos")

quality_cols = st.columns(4)

with quality_cols[0]:
    # Completitud de datos
    total_days = (fecha_fin - fecha_inicio).days + 1
    total_expected = total_days * len(selected_turnos)  # Registros esperados
    total_actual = sum(len(df) for df in machine_data.values()) / len(machine_data)
    completeness = (total_actual / total_expected * 100) if total_expected > 0 else 0
    
    st.metric(
        "Completitud de Datos",
        f"{completeness:.1f}%",
        delta="Excelente" if completeness > 90 else "Regular" if completeness > 70 else "Bajo"
    )

with quality_cols[1]:
    # Registros con operador asignado
    total_records = sum(len(df) for df in machine_data.values())
    assigned_records = sum(len(df[df['operador'] != 'SIN_ASIGNAR']) for df in machine_data.values())
    assignment_rate = (assigned_records / total_records * 100) if total_records > 0 else 0
    
    st.metric(
        "% Con Operador Asignado",
        f"{assignment_rate:.1f}%",
        delta="OK" if assignment_rate > 95 else "Revisar"
    )

with quality_cols[2]:
    # Outliers detectados
    total_outliers = 0
    for df in machine_data.values():
        if len(df) > 0:
            for indicador in df.columns:
                if indicador in INDICADORES:
                    df_temp = identify_outliers(df.copy(), indicador)
                    total_outliers += df_temp['is_outlier'].sum()
    
    outlier_rate = (total_outliers / total_records * 100) if total_records > 0 else 0
    
    st.metric(
        "% Valores Atípicos",
        f"{outlier_rate:.1f}%",
        delta="Normal" if outlier_rate < 5 else "Alto"
    )

with quality_cols[3]:
    # Consistencia de registros
    record_counts = [len(df) for df in machine_data.values() if len(df) > 0]
    if record_counts:
        consistency = (min(record_counts) / max(record_counts) * 100) if max(record_counts) > 0 else 0
    else:
        consistency = 0
    
    st.metric(
        "Consistencia entre KPIs",
        f"{consistency:.1f}%",
        delta="Balanceado" if consistency > 80 else "Desbalanceado"
    )

st.markdown("---")

# ============================================
# INSIGHTS AUTOMATIZADOS
# ============================================

st.subheader("🤖 Insights Automatizados")

insights = []

# Insight 1: Mejor y peor periodo
for indicador, df in machine_data.items():
    if len(df) > 0 and df['week'].nunique() > 2:
        week_avg = df.groupby('week')[indicador].mean()
        better = get_kpi_direction(indicador)
        
        if better == 'alto':
            best_week = week_avg.idxmax()
            worst_week = week_avg.idxmin()
            best_val = week_avg.max()
            worst_val = week_avg.min()
        else:
            best_week = week_avg.idxmin()
            worst_week = week_avg.idxmax()
            best_val = week_avg.min()
            worst_val = week_avg.max()
        
        improvement_potential = abs(best_val - worst_val)
        
        insights.append({
            'tipo': 'Variabilidad Temporal',
            'kpi': indicador,
            'mensaje': f"Week {best_week} tuvo el mejor performance ({best_val:.2f}). Week {worst_week} fue la peor ({worst_val:.2f}). Potencial de mejora: {improvement_potential:.2f}"
        })

# Insight 2: Operador más consistente
for indicador, df in machine_data.items():
    if len(df) > 0:
        df_ops = df[df['operador'] != 'SIN_ASIGNAR']
        if len(df_ops) > 0 and df_ops['operador'].nunique() > 2:
            op_stats = df_ops.groupby('operador')[indicador].agg(['mean', 'std', 'count'])
            op_stats = op_stats[op_stats['count'] >= 5]  # Solo operadores con suficientes datos
            
            if len(op_stats) > 0:
                # Operador más consistente (menor std)
                most_consistent = op_stats['std'].idxmin()
                consistency_val = op_stats.loc[most_consistent, 'std']
                
                insights.append({
                    'tipo': 'Consistencia de Operadores',
                    'kpi': indicador,
                    'mensaje': f"{most_consistent} es el operador más consistente en {indicador} (Desv.Est: {consistency_val:.2f})"
                })

# Insight 3: Correlaciones fuertes
if len(machine_data) >= 2:
    kpis = list(machine_data.keys())
    for i in range(len(kpis)):
        for j in range(i + 1, len(kpis)):
            kpi1, kpi2 = kpis[i], kpis[j]
            
            df1 = machine_data[kpi1][['fecha_str', 'turno', kpi1]]
            df2 = machine_data[kpi2][['fecha_str', 'turno', kpi2]]
            
            df_merged = pd.merge(df1, df2, on=['fecha_str', 'turno'], how='inner')
            
            if len(df_merged) > 10:
                corr = df_merged[kpi1].corr(df_merged[kpi2])
                
                if abs(corr) > 0.7:  # Correlación fuerte
                    direction = "positiva" if corr > 0 else "negativa"
                    insights.append({
                        'tipo': 'Correlación',
                        'kpi': f"{kpi1} & {kpi2}",
                        'mensaje': f"Correlación {direction} fuerte detectada ({corr:.2f}). Cuando {kpi1} cambia, {kpi2} tiende a cambiar en {'la misma' if corr > 0 else 'dirección opuesta'}"
                    })

# Mostrar insights
if insights:
    for idx, insight in enumerate(insights[:5]):  # Mostrar máximo 5 insights
        with st.expander(f"💡 Insight {idx + 1}: {insight['tipo']} - {insight['kpi']}", expanded=(idx == 0)):
            st.info(insight['mensaje'])
else:
    st.info("No se generaron insights automatizados para este periodo")

st.markdown("---")

# ============================================
# COMPARATIVA ANTES/DESPUÉS (si hay suficientes datos)
# ============================================

if (fecha_fin - fecha_inicio).days > 60:  # Solo si hay más de 2 meses de datos
    st.subheader("📅 Análisis Comparativo: Primera vs Segunda Mitad del Periodo")
    
    # Calcular punto medio - convertir a datetime
    mid_point = pd.to_datetime(fecha_inicio) + (pd.to_datetime(fecha_fin) - pd.to_datetime(fecha_inicio)) / 2
    
    col_before_after, col_empty3 = st.columns([1, 3])
    with col_before_after:
        ba_kpi = st.selectbox(
            "Selecciona KPI:",
            options=list(machine_data.keys()),
            key='ba_kpi'
        )
    
    df_ba = machine_data[ba_kpi]
    
    if len(df_ba) > 0:
        df_before = df_ba[df_ba['fecha'] < mid_point]
        df_after = df_ba[df_ba['fecha'] >= mid_point]
        
        if len(df_before) > 0 and len(df_after) > 0:
            avg_before = df_before[ba_kpi].mean()
            avg_after = df_after[ba_kpi].mean()
            
            change = avg_after - avg_before
            change_pct = (change / avg_before * 100) if avg_before != 0 else 0
            
            better = get_kpi_direction(ba_kpi)
            improved = (change > 0 and better == 'alto') or (change < 0 and better == 'bajo')
            
            col_ba1, col_ba2, col_ba3 = st.columns(3)
            
            with col_ba1:
                st.metric(
                    f"Primera Mitad ({fecha_inicio.strftime('%d/%m')} - {mid_point.strftime('%d/%m')})",
                    f"{avg_before:.2f}"
                )
            
            with col_ba2:
                st.metric(
                    f"Segunda Mitad ({mid_point.strftime('%d/%m')} - {fecha_fin.strftime('%d/%m')})",
                    f"{avg_after:.2f}"
                )
            
            with col_ba3:
                st.metric(
                    "Cambio",
                    f"{change:+.2f}",
                    delta=f"{change_pct:+.1f}% ({'Mejora' if improved else 'Empeoramiento'})"
                )
            
            # Interpretación
            if abs(change_pct) < 5:
                st.info("➡️ Performance estable entre ambos periodos")
            elif improved:
                st.success(f"📈 ¡Mejora del {abs(change_pct):.1f}%! La máquina ha mejorado su performance en la segunda mitad del periodo")
            else:
                st.warning(f"📉 Deterioro del {abs(change_pct):.1f}%. Se recomienda investigar causas del declive en performance")
        else:
            st.info("No hay suficientes datos en ambos periodos para comparar")
    else:
        st.info("No hay datos disponibles")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Análisis Detallado de Máquinas - Philip Morris International</p>
    <p>Máquina: {}<br>Datos actualizados al {}</p>
</div>
""".format(selected_machine, datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)