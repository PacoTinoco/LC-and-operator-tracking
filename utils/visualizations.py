"""
Funciones de visualización reutilizables con Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import calendar
from Config.constants import COLOR_PALETTE, INDICADORES


def create_line_chart(df: pd.DataFrame, 
                     x_col: str, 
                     y_col: str,
                     color_col: Optional[str] = None,
                     title: str = "",
                     x_label: str = "",
                     y_label: str = "",
                     show_range_slider: bool = True) -> go.Figure:
    """
    Crea un line chart interactivo con Plotly
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para eje X
        y_col: Columna para eje Y
        color_col: Columna para colorear líneas (opcional)
        title: Título del gráfico
        x_label: Label eje X
        y_label: Label eje Y
        show_range_slider: Mostrar selector de rango
    
    Returns:
        Figura de Plotly
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={x_col: x_label, y_col: y_label},
        markers=True,
        color_discrete_sequence=COLOR_PALETTE['maquinas']
    )
    
    # Mejorar hover
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>' + 
                      y_label + ': %{y:.2f}<br>' +
                      '<extra></extra>'
    )
    
    # Range slider
    if show_range_slider:
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all", label="Todo")
                ])
            )
        )
    
    # Styling
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_bar_chart(df: pd.DataFrame,
                    x_col: str,
                    y_col: str,
                    color_col: Optional[str] = None,
                    title: str = "",
                    x_label: str = "",
                    y_label: str = "",
                    orientation: str = 'v') -> go.Figure:
    """
    Crea un bar chart interactivo
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para eje X
        y_col: Columna para eje Y
        color_col: Columna para colorear barras
        title: Título del gráfico
        x_label: Label eje X
        y_label: Label eje Y
        orientation: 'v' (vertical) o 'h' (horizontal)
    
    Returns:
        Figura de Plotly
    """
    fig = px.bar(
        df,
        x=x_col if orientation == 'v' else y_col,
        y=y_col if orientation == 'v' else x_col,
        color=color_col,
        title=title,
        labels={x_col: x_label, y_col: y_label},
        orientation=orientation,
        color_discrete_sequence=COLOR_PALETTE['maquinas']
    )
    
    fig.update_layout(
        template='plotly_white',
        height=500,
        showlegend=True if color_col else False
    )
    
    return fig


def create_animated_bar_chart(df: pd.DataFrame,
                              x_col: str,
                              y_col: str,
                              animation_frame: str,
                              color_col: Optional[str] = None,
                              title: str = "") -> go.Figure:
    """
    Crea un bar chart animado (por week, mes, etc.)
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para eje X
        y_col: Columna para eje Y
        animation_frame: Columna para animar (ej: 'week', 'mes')
        color_col: Columna para colorear
        title: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        animation_frame=animation_frame,
        title=title,
        range_y=[0, df[y_col].max() * 1.1],  # Eje Y fijo
        color_discrete_sequence=COLOR_PALETTE['maquinas']
    )
    
    fig.update_layout(
        template='plotly_white',
        height=600
    )
    
    return fig


def create_histogram(df: pd.DataFrame,
                    column: str,
                    title: str = "",
                    x_label: str = "",
                    bins: int = 30,
                    color: Optional[str] = None) -> go.Figure:
    """
    Crea un histograma para analizar distribución
    
    Args:
        df: DataFrame con los datos
        column: Columna a analizar
        title: Título del gráfico
        x_label: Label eje X
        bins: Número de bins
        color: Color de las barras
    
    Returns:
        Figura de Plotly
    """
    fig = px.histogram(
        df,
        x=column,
        title=title,
        labels={column: x_label},
        nbins=bins,
        marginal="box",  # Agregar boxplot arriba
        color_discrete_sequence=[color or COLOR_PALETTE['primary']]
    )
    
    # Agregar línea de promedio
    mean_val = df[column].mean()
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Promedio: {mean_val:.2f}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig


def create_box_plot(df: pd.DataFrame,
                   y_col: str,
                   x_col: Optional[str] = None,
                   title: str = "",
                   y_label: str = "") -> go.Figure:
    """
    Crea un box plot para comparar distribuciones
    
    Args:
        df: DataFrame con los datos
        y_col: Columna con valores
        x_col: Columna para agrupar (opcional)
        title: Título del gráfico
        y_label: Label eje Y
    
    Returns:
        Figura de Plotly
    """
    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        title=title,
        labels={y_col: y_label},
        color=x_col,
        color_discrete_sequence=COLOR_PALETTE['maquinas'],
        points="outliers"  # Mostrar solo outliers
    )
    
    fig.update_layout(
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig


def create_heatmap(df: pd.DataFrame,
                  x_col: str,
                  y_col: str,
                  value_col: str,
                  title: str = "",
                  colorscale: str = 'RdYlGn') -> go.Figure:
    """
    Crea un heatmap (matriz de calor)
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para eje X
        y_col: Columna para eje Y
        value_col: Columna con valores
        title: Título del gráfico
        colorscale: Escala de color ('RdYlGn', 'Blues', etc.)
    
    Returns:
        Figura de Plotly
    """
    # Pivotear datos para crear matriz
    pivot_df = df.pivot_table(
        index=y_col,
        columns=x_col,
        values=value_col,
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale=colorscale,
        hovertemplate='%{y} - %{x}<br>Valor: %{z:.2f}<extra></extra>',
        colorbar=dict(title=value_col)
    ))
    
    fig.update_layout(
        title=title,
        template='plotly_white',
        height=500,
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    
    return fig


def create_scatter_plot(df: pd.DataFrame,
                       x_col: str,
                       y_col: str,
                       color_col: Optional[str] = None,
                       size_col: Optional[str] = None,
                       title: str = "",
                       x_label: str = "",
                       y_label: str = "") -> go.Figure:
    """
    Crea un scatter plot con opciones de color y tamaño
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para eje X
        y_col: Columna para eje Y
        color_col: Columna para colorear puntos
        size_col: Columna para tamaño de puntos
        title: Título del gráfico
        x_label: Label eje X
        y_label: Label eje Y
    
    Returns:
        Figura de Plotly
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        title=title,
        labels={x_col: x_label, y_col: y_label},
        color_discrete_sequence=COLOR_PALETTE['maquinas'],
        hover_data=df.columns
    )
    
    fig.update_layout(
        template='plotly_white',
        height=500
    )
    
    return fig


def create_gauge_chart(value: float,
                      title: str = "",
                      min_val: float = 0,
                      max_val: float = 100,
                      threshold_red: float = 33,
                      threshold_yellow: float = 66) -> go.Figure:
    """
    Crea un gauge chart (velocímetro) para mostrar KPI
    
    Args:
        value: Valor actual
        title: Título del gráfico
        min_val: Valor mínimo
        max_val: Valor máximo
        threshold_red: Umbral para zona roja
        threshold_yellow: Umbral para zona amarilla
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        delta={'reference': (max_val + min_val) / 2},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, threshold_red], 'color': "lightcoral"},
                {'range': [threshold_red, threshold_yellow], 'color': "lightyellow"},
                {'range': [threshold_yellow, max_val], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold_yellow
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        template='plotly_white'
    )
    
    return fig


def create_multi_line_comparison(df: pd.DataFrame,
                                 date_col: str,
                                 value_cols: List[str],
                                 title: str = "",
                                 y_label: str = "") -> go.Figure:
    """
    Crea gráfico de líneas múltiples para comparar varios KPIs
    
    Args:
        df: DataFrame con los datos
        date_col: Columna de fecha
        value_cols: Lista de columnas a graficar
        title: Título del gráfico
        y_label: Label eje Y
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    colors = COLOR_PALETTE['maquinas']
    
    for idx, col in enumerate(value_cols):
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df[col],
            mode='lines+markers',
            name=col,
            line=dict(color=colors[idx % len(colors)], width=2),
            hovertemplate=f'<b>{col}</b><br>Fecha: %{{x}}<br>Valor: %{{y:.2f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title=y_label,
        template='plotly_white',
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(rangeslider_visible=True)
    
    return fig


def create_sunburst_chart(df: pd.DataFrame,
                         path_cols: List[str],
                         value_col: str,
                         title: str = "") -> go.Figure:
    """
    Crea un sunburst chart (gráfico jerárquico circular)
    
    Args:
        df: DataFrame con los datos
        path_cols: Lista de columnas que forman la jerarquía
        value_col: Columna con valores
        title: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    fig = px.sunburst(
        df,
        path=path_cols,
        values=value_col,
        title=title,
        color_discrete_sequence=COLOR_PALETTE['maquinas']
    )
    
    fig.update_layout(
        template='plotly_white',
        height=600
    )
    
    return fig


def create_week_performance_chart(df: pd.DataFrame,
                                  kpi_col: str,
                                  kpi_name: str,
                                  better_direction: str = 'alto') -> go.Figure:
    """
    Crea gráfico de performance por week con zonas de color
    
    Args:
        df: DataFrame con columnas 'week' y KPI
        kpi_col: Nombre de la columna del KPI
        kpi_name: Nombre del KPI para display
        better_direction: 'alto' o 'bajo' (qué dirección es mejor)
    
    Returns:
        Figura de Plotly
    """
    # Calcular promedio por week
    week_avg = df.groupby('week')[kpi_col].mean().reset_index()
    week_avg.columns = ['week', 'promedio']
    
    # Calcular percentiles para zonas
    p25 = week_avg['promedio'].quantile(0.25)
    p75 = week_avg['promedio'].quantile(0.75)
    
    fig = go.Figure()
    
    # Línea principal
    fig.add_trace(go.Scatter(
        x=week_avg['week'],
        y=week_avg['promedio'],
        mode='lines+markers',
        name=kpi_name,
        line=dict(color=COLOR_PALETTE['primary'], width=3),
        marker=dict(size=8)
    ))
    
    # Línea de promedio general
    overall_mean = week_avg['promedio'].mean()
    fig.add_hline(
        y=overall_mean,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Promedio: {overall_mean:.2f}",
        annotation_position="right"
    )
    
    # Zonas de color (basado en better_direction)
    if better_direction == 'alto':
        # Verde arriba, rojo abajo
        fig.add_hrect(y0=p75, y1=week_avg['promedio'].max(), 
                     fillcolor="lightgreen", opacity=0.2, line_width=0)
        fig.add_hrect(y0=week_avg['promedio'].min(), y1=p25, 
                     fillcolor="lightcoral", opacity=0.2, line_width=0)
    else:
        # Rojo arriba, verde abajo
        fig.add_hrect(y0=p75, y1=week_avg['promedio'].max(), 
                     fillcolor="lightcoral", opacity=0.2, line_width=0)
        fig.add_hrect(y0=week_avg['promedio'].min(), y1=p25, 
                     fillcolor="lightgreen", opacity=0.2, line_width=0)
    
    fig.update_layout(
        title=f"Performance por Week - {kpi_name}",
        xaxis_title="Week",
        yaxis_title=kpi_name,
        template='plotly_white',
        height=500,
        hovermode='x'
    )
    
    return fig


def create_operator_ranking(df: pd.DataFrame,
                           kpi_col: str,
                           kpi_name: str,
                           top_n: int = 10) -> go.Figure:
    """
    Crea gráfico de ranking de operadores
    
    Args:
        df: DataFrame con columna 'operador' y KPI
        kpi_col: Nombre de la columna del KPI
        kpi_name: Nombre del KPI para display
        top_n: Número de operadores a mostrar
    
    Returns:
        Figura de Plotly
    """
    # Promedio por operador
    op_avg = df.groupby('operador')[kpi_col].mean().reset_index()
    op_avg = op_avg.sort_values(kpi_col, ascending=False).head(top_n)
    
    # Crear colores basados en ranking
    colors = ['green' if i < 3 else 'steelblue' for i in range(len(op_avg))]
    
    fig = go.Figure(go.Bar(
        x=op_avg[kpi_col],
        y=op_avg['operador'],
        orientation='h',
        marker=dict(color=colors),
        text=op_avg[kpi_col].round(2),
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f"Top {top_n} Operadores - {kpi_name}",
        xaxis_title=kpi_name,
        yaxis_title="Operador",
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig