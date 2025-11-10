"""
Estilos CSS personalizados para el dashboard PMI
Colores corporativos Philip Morris International
"""

import base64
from pathlib import Path

# Colores corporativos PMI
PMI_BLUE = '#4A90E2'
PMI_DARK_BLUE = '#2E5C8A'
PMI_LIGHT_BLUE = '#E3F2FD'

# Template de CSS con variables
CSS_TEMPLATE = """
<style>
/* Importar fuente corporativa */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

* {
    font-family: 'Roboto', sans-serif;
}

/* Animación de gradiente */
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Fondo principal */
.stApp {
    background: linear-gradient(135deg, %(bg_color1)s, %(bg_color2)s, %(bg_color3)s);
    background-size: 200%% 200%%;
    animation: gradient 15s ease infinite;
}

/* Contenedor principal */
.main .block-container {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 12px;
    padding: 2rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 40px rgba(74, 144, 226, 0.1);
    border: 1px solid rgba(74, 144, 226, 0.1);
}

/* Headers */
h1 {
    color: %(header_color)s;
    font-weight: 700;
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

h2 {
    color: %(subheader_color)s;
    font-weight: 600;
    font-size: 1.8rem;
    margin-top: 2rem;
}

h3 {
    color: %(subheader_color)s;
    font-weight: 500;
    font-size: 1.3rem;
}

/* Métricas */
[data-testid="stMetricValue"] {
    font-size: 2.2rem;
    font-weight: 700;
    color: %(metric_color)s;
}

[data-testid="stMetricLabel"] {
    font-size: 0.9rem;
    font-weight: 500;
    color: #546E7A;
    text-transform: uppercase;
}

/* Botones */
.stButton>button {
    background: linear-gradient(135deg, %(button_bg)s, %(button_bg_hover)s);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(74, 144, 226, 0.3);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, %(sidebar_top)s, %(sidebar_bottom)s);
    border-right: 2px solid rgba(74, 144, 226, 0.2);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: white;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background-color: rgba(74, 144, 226, 0.05);
    border-radius: 10px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.8rem 1.5rem;
    background-color: transparent;
    color: %(tab_color)s;
    font-weight: 500;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: %(tab_active_bg)s;
    color: white;
    box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

/* Expandables */
.streamlit-expanderHeader {
    border-radius: 8px;
    background-color: rgba(74, 144, 226, 0.05);
    border: 1px solid rgba(74, 144, 226, 0.1);
    font-weight: 500;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(74, 144, 226, 0.3);
    border-radius: 10px;
    background-color: rgba(74, 144, 226, 0.02);
}

/* Alerts */
.stSuccess {
    background-color: rgba(76, 175, 80, 0.1);
    border-left: 4px solid #4CAF50;
    border-radius: 8px;
}

.stInfo {
    background-color: rgba(74, 144, 226, 0.1);
    border-left: 4px solid %(info_border)s;
    border-radius: 8px;
}

.stWarning {
    background-color: rgba(255, 152, 0, 0.1);
    border-left: 4px solid #FF9800;
    border-radius: 8px;
}

.stError {
    background-color: rgba(244, 67, 54, 0.1);
    border-left: 4px solid #F44336;
    border-radius: 8px;
}

/* Gráficos */
.js-plotly-plot {
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(74, 144, 226, 0.08);
    background: white;
}

/* Dataframes */
.stDataFrame {
    border-radius: 8px;
    border: 1px solid rgba(74, 144, 226, 0.1);
}
</style>
"""

# Configuración de colores por página
PAGE_THEMES = {
    'home': {
        'bg_color1': '#FFFFFF',
        'bg_color2': '#E3F2FD',
        'bg_color3': '#BBDEFB',
        'header_color': '#4A90E2',
        'subheader_color': '#2E5C8A',
        'metric_color': '#4A90E2',
        'button_bg': '#4A90E2',
        'button_bg_hover': '#2E5C8A',
        'sidebar_top': '#4A90E2',
        'sidebar_bottom': '#2E5C8A',
        'tab_color': '#2E5C8A',
        'tab_active_bg': '#4A90E2',
        'info_border': '#4A90E2',
    },
    'carga_datos': {
        'bg_color1': '#FFFFFF',
        'bg_color2': '#E8F5E9',
        'bg_color3': '#C8E6C9',
        'header_color': '#2E7D32',
        'subheader_color': '#1B5E20',
        'metric_color': '#388E3C',
        'button_bg': '#4CAF50',
        'button_bg_hover': '#388E3C',
        'sidebar_top': '#4CAF50',
        'sidebar_bottom': '#2E7D32',
        'tab_color': '#2E7D32',
        'tab_active_bg': '#4CAF50',
        'info_border': '#4CAF50',
    },
    'dashboard_general': {
        'bg_color1': '#FFFFFF',
        'bg_color2': '#FFF3E0',
        'bg_color3': '#FFE0B2',
        'header_color': '#E65100',
        'subheader_color': '#BF360C',
        'metric_color': '#F57C00',
        'button_bg': '#FF9800',
        'button_bg_hover': '#F57C00',
        'sidebar_top': '#FF9800',
        'sidebar_bottom': '#E65100',
        'tab_color': '#E65100',
        'tab_active_bg': '#FF9800',
        'info_border': '#FF9800',
    },
    'analisis_operadores': {
        'bg_color1': '#FFFFFF',
        'bg_color2': '#E1F5FE',
        'bg_color3': '#B3E5FC',
        'header_color': '#0277BD',
        'subheader_color': '#01579B',
        'metric_color': '#0288D1',
        'button_bg': '#03A9F4',
        'button_bg_hover': '#0288D1',
        'sidebar_top': '#03A9F4',
        'sidebar_bottom': '#0277BD',
        'tab_color': '#0277BD',
        'tab_active_bg': '#03A9F4',
        'info_border': '#03A9F4',
    },
    'analisis_lc': {
        'bg_color1': '#FFFFFF',
        'bg_color2': '#F3E5F5',
        'bg_color3': '#E1BEE7',
        'header_color': '#6A1B9A',
        'subheader_color': '#4A148C',
        'metric_color': '#7B1FA2',
        'button_bg': '#9C27B0',
        'button_bg_hover': '#7B1FA2',
        'sidebar_top': '#9C27B0',
        'sidebar_bottom': '#6A1B9A',
        'tab_color': '#6A1B9A',
        'tab_active_bg': '#9C27B0',
        'info_border': '#9C27B0',
    },
    'analisis_maquinas': {
        'bg_color1': '#FFFFFF',
        'bg_color2': '#E0F2F1',
        'bg_color3': '#B2DFDB',
        'header_color': '#00695C',
        'subheader_color': '#004D40',
        'metric_color': '#00796B',
        'button_bg': '#009688',
        'button_bg_hover': '#00796B',
        'sidebar_top': '#009688',
        'sidebar_bottom': '#00695C',
        'tab_color': '#00695C',
        'tab_active_bg': '#009688',
        'info_border': '#009688',
    }
}


def get_full_page_style(page_name: str) -> str:
    """
    Obtiene el estilo CSS completo para una página
    
    Args:
        page_name: Nombre de la página ('home', 'carga_datos', etc.)
    
    Returns:
        HTML con CSS para inyectar en la página
    """
    theme = PAGE_THEMES.get(page_name, PAGE_THEMES['home'])
    
    # Usar % formatting para evitar problemas con {}
    return CSS_TEMPLATE % theme


def get_pmi_logo_html():
    """
    Genera HTML para mostrar el logo de PMI
    Intenta cargar desde assets/, si falla usa URL de respaldo
    """
    try:
        # Ruta relativa a la imagen
        logo_path = Path(__file__).parent.parent / "assets" / "PMI-LOGO.png"
        
        if logo_path.exists():
            # Leer y convertir a base64
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            
            return f"""
            <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
                <img src="data:image/png;base64,{logo_data}" 
                     alt="Philip Morris International" 
                     style="max-width: 400px; width: 100%; height: auto;">
            </div>
            """
        else:
            # Fallback a URL de internet
            return """
            <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Philip_Morris_International_logo.svg/2560px-Philip_Morris_International_logo.svg.png" 
                     alt="Philip Morris International" 
                     style="max-width: 400px; width: 100%; height: auto;">
            </div>
            """
    except Exception as e:
        # Si hay cualquier error, usar URL de internet
        return """
        <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Philip_Morris_International_logo.svg/2560px-Philip_Morris_International_logo.svg.png" 
                 alt="Philip Morris International" 
                 style="max-width: 400px; width: 100%; height: auto;">
        </div>
        """