"""
Constantes globales para el dashboard de PMI
"""

# ============================================
# MÁQUINAS
# ============================================
MAQUINAS = [
    'KDF-7',
    'KDF-8',
    'KDF-9',
    'KDF-10',
    'KDF-11',
    'KDF-17'
]

# ============================================
# TURNOS
# ============================================
TURNOS = ['S1', 'S2', 'S3']

# ============================================
# INDICADORES (KPIs)
# ============================================
INDICADORES = {
    'MTBF': {
        'nombre': 'Mean Time Between Failures',
        'unidad': 'minutos',
        'mejor': 'alto',  # Más alto es mejor
        'descripcion': 'Tiempo promedio entre fallas de la máquina',
        'variantes': ['MTBF']  # Posibles nombres en archivos
    },
    'UPDT': {
        'nombre': 'Unplanned Downtime',
        'unidad': '%',
        'mejor': 'bajo',  # Más bajo es mejor
        'descripcion': 'Porcentaje de tiempo con paros no planeados',
        'variantes': ['UPDT', 'Unplanned Downtime']
    },
    'Reject Rate': {
        'nombre': 'Reject Rate',
        'unidad': '%',
        'mejor': 'bajo',  # Más bajo es mejor
        'descripcion': 'Porcentaje de producto rechazado/desperdicio',
        'variantes': ['Reject Rate', 'RejectRate'],
        'es_porcentaje_0_1': True  # Los datos vienen en escala 0-1, no 0-100
    },
    'Strategic PR': {
        'nombre': 'Strategic Performance Rate',
        'unidad': '%',
        'mejor': 'alto',  # Más alto es mejor
        'descripcion': 'Porcentaje de tiempo que la máquina funcionó correctamente',
        'variantes': ['Strategic PR', 'Stratergic PR', 'StrategicPR', 'StratergicPR']
    }
}

# ============================================
# LINE COORDINATORS
# ============================================
LINE_COORDINATORS = {
    'LC_1': {'nombre': 'Line Coordinator 1', 'operadores': []},  # Se llenará dinámicamente
    'LC_2': {'nombre': 'Line Coordinator 2', 'operadores': []},
    'LC_3': {'nombre': 'Line Coordinator 3', 'operadores': []}
}

# ============================================
# OPERADORES (Total: 15)
# ============================================
# Se cargarán dinámicamente del archivo de asignaciones
# Para referencia, se espera tener 15 operadores únicos

# ============================================
# PERIODO DE DATOS
# ============================================
FECHA_INICIO = '2025-01-13'  # 13 de Enero 2025
FECHA_FIN = '2025-10-19'     # 19 de Octubre 2025

# ============================================
# VALIDACIONES
# ============================================
# Fila donde empieza la tabla de datos en Excel
FILA_INICIO_DATOS = 2  # Índice 2 = fila 3 en Excel (0-indexed)

# Máximo permitido para UPDT (inconsistencias)
UPDT_MAX_THRESHOLD = 50.0  # %

# Formatos de fecha aceptados
FORMATO_FECHA_SHIFT = '%d-%m-%Y'  # DD-MM-YYYY

# Extensiones de archivo permitidas
EXTENSIONES_PERMITIDAS = ['.csv', '.xlsx', '.xls']

# ============================================
# COLORES PARA VISUALIZACIONES
# ============================================
COLOR_PALETTE = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#ff9800',
    'danger': '#d62728',
    'info': '#17becf',
    'maquinas': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
    'turnos': ['#3498db', '#e74c3c', '#f39c12'],  # S1, S2, S3
    'kpis': {
        'MTBF': '#2ecc71',
        'UPDT': '#e74c3c',
        'Reject Rate': '#e67e22',
        'Strategic PR': '#3498db'
    }
}

# ============================================
# MENSAJES
# ============================================
MENSAJES = {
    'bienvenida': '¡Bienvenido al Dashboard de Performance PMI!',
    'sin_datos': 'No hay datos cargados. Por favor sube los archivos en la sección "Carga de Datos".',
    'carga_exitosa': '✅ Datos cargados exitosamente',
    'error_validacion': '❌ Error en validación de datos',
    'procesando': '⏳ Procesando datos...'
}

# ============================================
# COLUMNAS ESPERADAS
# ============================================
COLUMNAS_ASIGNACIONES = [
    'Operador',
    'Coordinador',
    'Fecha_Inicio',
    'Fecha_Fin',
    'Turno',
    'Máquina'
]

COLUMNA_SHIFT = 'Shift'  # Columna común en todos los indicadores