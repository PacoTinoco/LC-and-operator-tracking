"""
Análisis de Line Coordinators - Performance de Equipos
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
    calculate_trend,
    create_line_chart,
    create_bar_chart,
    create_box_plot,
    create_heatmap,
    create_sunburst_chart,
    create_animated_bar_chart,
    create_multi_line_comparison
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Line Coordinators - PMI",
    page_icon="👔",
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
st.title("👔 Análisis de Line Coordinators")
st.markdown("### Performance de Equipos y Supervisión")

st.markdown("---")

# ============================================
# OBTENER LISTA DE LCs Y SUS OPERADORES
# ============================================

# Obtener todos los LCs únicos
all_lcs = set()
for df in data.values():
    lcs = df[df['coordinador'] != 'SIN_ASIGNAR']['coordinador'].unique()
    all_lcs.update(lcs)

all_lcs = sorted(list(all_lcs))

if len(all_lcs) == 0:
    st.error("❌ No hay Line Coordinators asignados en los datos cargados")
    st.stop()

# Construir diccionario de LC -> operadores
lc_teams = {}
for lc in all_lcs:
    operadores = set()
    for df in data.values():
        ops = df[df['coordinador'] == lc]['operador'].unique()
        operadores.update(ops)
    lc_teams[lc] = sorted(list(operadores))

# ============================================
# FILTROS EN SIDEBAR
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

# Aplicar filtros
filtered_data = {}
for indicador, df in data.items():
    df_filtered = df[
        (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
        (df['fecha'] <= pd.to_datetime(fecha_fin)) &
        (df['maquina'].isin(selected_maquinas)) &
        (df['turno'].isin(selected_turnos)) &
        (df['coordinador'] != 'SIN_ASIGNAR')
    ].copy()
    filtered_data[indicador] = df_filtered

st.sidebar.markdown("---")
st.sidebar.info(f"📅 Periodo: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")

# ============================================
# VISTA GENERAL DE LINE COORDINATORS
# ============================================

st.subheader("📊 Comparativa General de Line Coordinators")

# Calcular métricas por LC
lc_metrics = []

for lc in all_lcs:
    lc_row = {'LC': lc}
    
    # Contar operadores en el equipo
    lc_row['Operadores'] = len(lc_teams[lc])
    
    # Calcular promedios por KPI
    for indicador, df in filtered_data.items():
        df_lc = df[df['coordinador'] == lc]
        if len(df_lc) > 0:
            lc_row[f'{indicador}_avg'] = df_lc[indicador].mean()
            lc_row[f'{indicador}_count'] = len(df_lc)
        else:
            lc_row[f'{indicador}_avg'] = None
            lc_row[f'{indicador}_count'] = 0
    
    lc_metrics.append(lc_row)

df_lc_metrics = pd.DataFrame(lc_metrics)

# Mostrar cards de resumen
lc_cols = st.columns(len(all_lcs))

for idx, lc in enumerate(all_lcs):
    with lc_cols[idx]:
        st.markdown(f"### {lc}")
        
        lc_data = df_lc_metrics[df_lc_metrics['LC'] == lc].iloc[0]
        
        st.metric("Operadores en Equipo", int(lc_data['Operadores']))
        
        # Mostrar promedio de cada KPI
        for indicador in filtered_data.keys():
            avg_col = f'{indicador}_avg'
            if pd.notna(lc_data[avg_col]):
                unidad = INDICADORES[indicador]['unidad']
                st.metric(
                    indicador,
                    f"{lc_data[avg_col]:.2f} {unidad}",
                    delta=f"{int(lc_data[f'{indicador}_count'])} reg"
                )
            else:
                st.metric(indicador, "Sin datos")
        
        # Mostrar operadores del equipo
        with st.expander("👥 Ver operadores"):
            for op in lc_teams[lc]:
                st.caption(f"• {op}")

st.markdown("---")

# ============================================
# COMPARATIVA DE KPIs ENTRE LCs
# ============================================

st.subheader("📈 Comparativa de KPIs entre Line Coordinators")

# Selector de KPI
col_kpi_selector, col_empty = st.columns([1, 3])
with col_kpi_selector:
    selected_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(filtered_data.keys())
    )

# Preparar datos para comparación
lc_comparison = []
for lc in all_lcs:
    df_lc = filtered_data[selected_kpi][filtered_data[selected_kpi]['coordinador'] == lc]
    if len(df_lc) > 0:
        lc_comparison.append({
            'LC': lc,
            'Promedio': df_lc[selected_kpi].mean(),
            'Desv_Est': df_lc[selected_kpi].std(),
            'Min': df_lc[selected_kpi].min(),
            'Max': df_lc[selected_kpi].max(),
            'Registros': len(df_lc)
        })

if lc_comparison:
    df_comparison = pd.DataFrame(lc_comparison)
    
    col_bar, col_box = st.columns([2, 1])
    
    with col_bar:
        # Gráfico de barras comparativo
        fig = create_bar_chart(
            df=df_comparison,
            x_col='LC',
            y_col='Promedio',
            title=f"Comparativa de {selected_kpi} por Line Coordinator",
            x_label="Line Coordinator",
            y_label=selected_kpi
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_box:
        # Box plot para ver distribución
        df_box = filtered_data[selected_kpi][filtered_data[selected_kpi]['coordinador'].isin(all_lcs)]
        
        fig_box = create_box_plot(
            df=df_box,
            y_col=selected_kpi,
            x_col='coordinador',
            title=f"Distribución de {selected_kpi}",
            y_label=selected_kpi
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Tabla detallada
    st.markdown("**📋 Estadísticas Detalladas:**")
    st.dataframe(
        df_comparison.style.background_gradient(subset=['Promedio'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )
    
    # Identificar mejor LC
    better_direction = get_kpi_direction(selected_kpi)
    if better_direction == 'alto':
        best_lc = df_comparison.loc[df_comparison['Promedio'].idxmax(), 'LC']
    else:
        best_lc = df_comparison.loc[df_comparison['Promedio'].idxmin(), 'LC']
    
    st.success(f"🏆 **Mejor Performance en {selected_kpi}**: {best_lc}")
else:
    st.info("No hay datos suficientes para comparar")

st.markdown("---")

# ============================================
# EVOLUCIÓN TEMPORAL POR LC
# ============================================

st.subheader("📊 Evolución Temporal de Performance")

col_evolution_kpi, col_empty2 = st.columns([1, 3])
with col_evolution_kpi:
    evolution_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(filtered_data.keys()),
        key='evolution_kpi'
    )

# Calcular promedio por week para cada LC
evolution_data = []

for lc in all_lcs:
    df_lc = filtered_data[evolution_kpi][filtered_data[evolution_kpi]['coordinador'] == lc]
    if len(df_lc) > 0:
        week_avg = df_lc.groupby('week')[evolution_kpi].mean().reset_index()
        week_avg['LC'] = lc
        evolution_data.append(week_avg)

if evolution_data:
    df_evolution = pd.concat(evolution_data, ignore_index=True)
    
    # Gráfico de líneas comparativo
    fig = create_line_chart(
        df=df_evolution,
        x_col='week',
        y_col=evolution_kpi,
        color_col='LC',
        title=f"Evolución de {evolution_kpi} por Week - Comparativa LCs",
        x_label="Week",
        y_label=evolution_kpi,
        show_range_slider=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de tendencias
    st.markdown("**📈 Análisis de Tendencias:**")
    
    trend_cols = st.columns(len(all_lcs))
    
    for idx, lc in enumerate(all_lcs):
        with trend_cols[idx]:
            df_lc = filtered_data[evolution_kpi][filtered_data[evolution_kpi]['coordinador'] == lc]
            if len(df_lc) > 1:
                tendencia = calculate_trend(df_lc, evolution_kpi)
                
                if tendencia == "mejorando":
                    st.success(f"**{lc}**: 📈 Mejorando")
                elif tendencia == "empeorando":
                    st.error(f"**{lc}**: 📉 Empeorando")
                else:
                    st.info(f"**{lc}**: ➡️ Estable")
            else:
                st.caption(f"**{lc}**: Sin datos suficientes")
else:
    st.info("No hay datos suficientes para analizar evolución")

st.markdown("---")

# ============================================
# ANÁLISIS DE EQUIPOS (OPERADORES POR LC)
# ============================================

st.subheader("👥 Análisis de Equipos de Operadores")

# Tabs para cada LC
team_tabs = st.tabs([f"{lc}" for lc in all_lcs])

for idx, lc in enumerate(all_lcs):
    with team_tabs[idx]:
        st.markdown(f"### Equipo de {lc}")
        
        # Selector de KPI para este análisis
        team_kpi = st.selectbox(
            "Selecciona KPI:",
            options=list(filtered_data.keys()),
            key=f'team_kpi_{lc}'
        )
        
        # Obtener datos del equipo
        df_team = filtered_data[team_kpi][filtered_data[team_kpi]['coordinador'] == lc]
        
        if len(df_team) > 0:
            # Calcular promedio por operador
            op_stats = df_team.groupby('operador').agg({
                team_kpi: ['mean', 'std', 'count'],
                'maquina': lambda x: x.nunique()
            }).reset_index()
            
            op_stats.columns = ['Operador', 'Promedio', 'Desv_Est', 'Registros', 'Máquinas']
            op_stats = op_stats.sort_values('Promedio', ascending=False)
            
            col_team_chart, col_team_table = st.columns([2, 1])
            
            with col_team_chart:
                # Gráfico de barras del equipo
                fig = create_bar_chart(
                    df=op_stats,
                    x_col='Operador',
                    y_col='Promedio',
                    title=f"Performance del Equipo - {team_kpi}",
                    x_label="Operador",
                    y_label=team_kpi,
                    orientation='v'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col_team_table:
                st.markdown("**📊 Estadísticas:**")
                
                # Promedio del equipo
                team_avg = df_team[team_kpi].mean()
                st.metric("Promedio del Equipo", f"{team_avg:.2f}")
                
                # Mejor operador
                best_op = op_stats.iloc[0]['Operador']
                best_val = op_stats.iloc[0]['Promedio']
                st.metric("Mejor Operador", best_op, delta=f"{best_val:.2f}")
                
                # Variabilidad
                team_std = df_team[team_kpi].std()
                st.metric("Variabilidad (Desv.Est)", f"{team_std:.2f}")
                
                # Consistencia
                cv = (team_std / team_avg) * 100 if team_avg != 0 else 0
                st.metric("Coef. Variación", f"{cv:.1f}%")
            
            # Tabla detallada del equipo
            st.markdown("**📋 Detalle de Operadores:**")
            st.dataframe(
                op_stats.style.background_gradient(subset=['Promedio'], cmap='RdYlGn'),
                use_container_width=True,
                hide_index=True
            )
            
            # Identificar oportunidades
            st.markdown("**💡 Observaciones:**")
            
            # Calcular brecha entre mejor y peor
            if len(op_stats) > 1:
                best_val = op_stats.iloc[0]['Promedio']
                worst_val = op_stats.iloc[-1]['Promedio']
                gap = abs(best_val - worst_val)
                gap_pct = (gap / team_avg * 100) if team_avg != 0 else 0
                
                st.info(f"📊 **Brecha de performance**: {gap:.2f} ({gap_pct:.1f}%) entre mejor y peor operador")
                
                # Identificar operadores bajo promedio
                below_avg = op_stats[op_stats['Promedio'] < team_avg]
                if len(below_avg) > 0:
                    st.warning(f"⚠️ **{len(below_avg)} operador(es)** por debajo del promedio del equipo")
        else:
            st.info(f"No hay datos disponibles para el equipo de {lc}")

st.markdown("---")

# ============================================
# GRÁFICO ANIMADO POR WEEK
# ============================================

st.subheader("🎬 Evolución Animada por Week")

col_anim_kpi, col_empty4 = st.columns([1, 3])
with col_anim_kpi:
    animated_kpi = st.selectbox(
        "Selecciona KPI:",
        options=list(filtered_data.keys()),
        key='animated_kpi'
    )

# Preparar datos por week
anim_data = []
for lc in all_lcs:
    df_lc = filtered_data[animated_kpi][filtered_data[animated_kpi]['coordinador'] == lc]
    if len(df_lc) > 0:
        week_data = df_lc.groupby('week')[animated_kpi].mean().reset_index()
        week_data['LC'] = lc
        anim_data.append(week_data)

if anim_data:
    df_anim = pd.concat(anim_data, ignore_index=True)
    
    fig = create_animated_bar_chart(
        df=df_anim,
        x_col='LC',
        y_col=animated_kpi,
        animation_frame='week',
        color_col='LC',
        title=f"Evolución de {animated_kpi} por Week"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("▶️ **Presiona Play** para ver la evolución semana a semana")
else:
    st.info("No hay datos suficientes para generar la animación")

st.markdown("---")

# ============================================
# RANKING Y CONCLUSIONES
# ============================================

st.subheader("🏆 Ranking General de Line Coordinators")

# Calcular ranking ponderado (promedio de todos los KPIs normalizados)
ranking_data = []

for lc in all_lcs:
    lc_scores = {}
    
    for indicador, df in filtered_data.items():
        df_lc = df[df['coordinador'] == lc]
        if len(df_lc) > 0:
            avg_lc = df_lc[indicador].mean()
            
            # Normalizar según dirección del KPI
            all_values = df[indicador].values
            min_val = all_values.min()
            max_val = all_values.max()
            
            if max_val != min_val:
                normalized = (avg_lc - min_val) / (max_val - min_val)
                
                # Invertir si "bajo es mejor"
                if get_kpi_direction(indicador) == 'bajo':
                    normalized = 1 - normalized
                
                lc_scores[indicador] = normalized * 100
            else:
                lc_scores[indicador] = 50.0
    
    if lc_scores:
        ranking_data.append({
            'LC': lc,
            'Score_Global': np.mean(list(lc_scores.values())),
            **lc_scores
        })

if ranking_data:
    df_ranking = pd.DataFrame(ranking_data)
    df_ranking = df_ranking.sort_values('Score_Global', ascending=False)
    
    # Mostrar podio
    col_rank1, col_rank2, col_rank3 = st.columns(3)
    
    for idx in range(min(3, len(df_ranking))):
        with [col_rank1, col_rank2, col_rank3][idx]:
            lc = df_ranking.iloc[idx]['LC']
            score = df_ranking.iloc[idx]['Score_Global']
            
            medal = ["🥇", "🥈", "🥉"][idx]
            
            st.markdown(f"### {medal} Lugar {idx + 1}")
            st.metric(lc, f"{score:.1f} pts")
            
            # Mostrar scores por KPI
            with st.expander("Ver detalle"):
                for indicador in filtered_data.keys():
                    if indicador in df_ranking.columns:
                        ind_score = df_ranking.iloc[idx][indicador]
                        st.progress(ind_score / 100)
                        st.caption(f"{indicador}: {ind_score:.1f}")
    
    # Tabla completa
    st.markdown("**📊 Ranking Detallado:**")
    st.dataframe(
        df_ranking.style.background_gradient(subset=['Score_Global'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption("💡 **Metodología**: Score Global calculado como promedio de KPIs normalizados (0-100)")
else:
    st.info("No hay datos suficientes para calcular ranking")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Análisis de Line Coordinators - Philip Morris International</p>
    <p>Datos actualizados al {}</p>
</div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)