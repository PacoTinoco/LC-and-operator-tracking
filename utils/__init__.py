"""
Utils package - Funciones de utilidad para el dashboard PMI
"""

from .data_loader import (
    load_excel_file,
    process_indicator_file,
    load_asignaciones_csv,
    merge_with_asignaciones,
    consolidate_all_data,
    save_to_session_state,
    load_from_session_state
)

from .validators import (
    validate_filename,
    validate_file_structure,
    validate_shift_format,
    validate_machine_name,
    check_data_completeness,
    generate_validation_report
)

from .calculations import (
    parse_shift_column,
    get_pmi_week_number,
    calculate_week_average,
    calculate_month_average,
    process_updt_file,
    get_kpi_direction,
    calculate_percentile_rank,
    identify_outliers,
    calculate_trend
)

from .visualizations import (
    create_line_chart,
    create_bar_chart,
    create_animated_bar_chart,
    create_histogram,
    create_box_plot,
    create_heatmap,
    create_scatter_plot,
    create_gauge_chart,
    create_multi_line_comparison,
    create_sunburst_chart,
    create_week_performance_chart,
    create_operator_ranking
)

__all__ = [
    # Data Loaders
    'load_excel_file',
    'process_indicator_file',
    'load_asignaciones_csv',
    'merge_with_asignaciones',
    'consolidate_all_data',
    'save_to_session_state',
    'load_from_session_state',
    
    # Validators
    'validate_filename',
    'validate_file_structure',
    'validate_shift_format',
    'validate_machine_name',
    'check_data_completeness',
    'generate_validation_report',
    
    # Calculations
    'parse_shift_column',
    'get_pmi_week_number',
    'calculate_week_average',
    'calculate_month_average',
    'process_updt_file',
    'get_kpi_direction',
    'calculate_percentile_rank',
    'identify_outliers',
    'calculate_trend',
    
    # Visualizations
    'create_line_chart',
    'create_bar_chart',
    'create_animated_bar_chart',
    'create_histogram',
    'create_box_plot',
    'create_heatmap',
    'create_scatter_plot',
    'create_gauge_chart',
    'create_multi_line_comparison',
    'create_sunburst_chart',
    'create_week_performance_chart',
    'create_operator_ranking'
]