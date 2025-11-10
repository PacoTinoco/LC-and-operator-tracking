# PMI Operators Dashboard

Dashboard de análisis de performance para operadores y máquinas KDF de Philip Morris International.

## 🚀 Instalación

1. Clona el repositorio
2. Instala dependencias:
```bash
pip install -r requirements.txt
```

3. Coloca el archivo `asignaciones_operadores.csv` en la carpeta `data/`

4. Ejecuta la aplicación:
```bash
streamlit run Home.py
```

## 📊 Características

- **Carga y validación** de datos Excel/CSV
- **Dashboard General** con vista ejecutiva de KPIs
- **Análisis de Operadores** individual
- **Análisis de Line Coordinators** y equipos
- **Análisis de Máquinas** detallado
- **Visualizaciones interactivas** con Plotly
- **Exportación de datos** procesados

## 📁 Estructura
```
pmi-operators-dashboard/
├── Home.py
├── pages/
│   ├── 1_📤_Carga_de_Datos.py
│   ├── 2_📊_Dashboard_General.py
│   ├── 3_👷_Análisis_Operadores.py
│   ├── 4_👔_Análisis_LC.py
│   └── 5_⚙️_Análisis_Máquinas.py
├── utils/
├── config/
└── data/
```

## 🔧 Uso

1. **Carga de Datos**: Sube archivos Excel de indicadores (MTBF, UPDT, Reject Rate, Strategic PR)
2. **Validación automática**: El sistema valida formatos y cruza con asignaciones
3. **Análisis**: Explora las diferentes páginas de visualización

## 📝 Formato de Datos

Los archivos deben:
- Empezar con el nombre del indicador
- Tener columna `Shift` con formato: `S[1-3] DD-MM-YYYY`
- Datos desde la fila 3

## 📧 Contacto

Para soporte, contacta al equipo de desarrollo.