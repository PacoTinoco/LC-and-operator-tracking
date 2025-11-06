import pandas as pd
import plotly.express as px

def filtrar_y_visualizar(df, indicador, lcs_seleccionados, operadores_seleccionados, maquinas_seleccionadas, fecha_inicio, fecha_fin):
    # Filtrar por rango de fechas
    df_filtrado = df[(df['Fecha'] >= fecha_inicio) & (df['Fecha'] <= fecha_fin)]

    # Filtrar por LC, operador y máquina
    df_filtrado = df_filtrado[
        df_filtrado['Coordinador'].isin(lcs_seleccionados) &
        df_filtrado['Operador'].isin(operadores_seleccionados) &
        df_filtrado['Maquina'].isin(maquinas_seleccionadas)
    ]

    # Determinar columna de valores
    valor_col = 'UPDT_Total' if indicador == 'UPDT Categories' else indicador

    # Agrupación por operador y turno
    por_turno = df_filtrado.groupby(['Operador', 'Turno', 'Mes', 'Año'])[valor_col].mean().reset_index()

    # Agrupación combinada (todos los turnos juntos)
    combinado = df_filtrado.groupby(['Operador', 'Mes', 'Año'])[valor_col].mean().reset_index()

    # Comparación por LC
    comparacion_lc = df_filtrado.groupby(['Coordinador'])[valor_col].mean().reset_index()

    # Visualizaciones
    fig_turno = px.line(por_turno, x='Mes', y=valor_col, color='Operador', line_dash='Turno', title='Performance por Turno')
    fig_combinado = px.line(combinado, x='Mes', y=valor_col, color='Operador', title='Performance Combinado por Mes')
    fig_lc = px.bar(comparacion_lc, x='Coordinador', y=valor_col, title='Comparación de Performance por LC')

    # Retornar dataframes y figuras
    return {
        'por_turno': por_turno,
        'combinado': combinado,
        'comparacion_lc': comparacion_lc,
        'fig_turno': fig_turno,
        'fig_combinado': fig_combinado,
        'fig_lc': fig_lc
    }