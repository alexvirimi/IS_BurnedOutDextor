from typing import List, Dict

def explain_burnout_reasons(features: Dict, burnout_class: str) -> List[str]:
    """
    Analiza los features de entrada y la predicción para generar 
    explicaciones en lenguaje natural para RRHH.
    """
    reasons = []

    # 1. Análisis de Variables Psicométricas (MBI)
    # Basado en los umbrales estándar del Inventario de Burnout de Maslach
    if features.get("avg_agotamiento", 1.0) >= 3.5:
        reasons.append(
            f"Detección de agotamiento emocional elevado "
            f"({features['avg_agotamiento']:.2f}/5.0)."
        )
    
    if features.get("avg_despersonalizacion", 1.0) >= 3.5:
        reasons.append(
            f"Presencia de despersonalización alta "
            f"({features['avg_despersonalizacion']}/5.0)."
        )
    
    if features.get("eficacia_invertida", 1.0) >= 3.5:
        reasons.append(
            f"Baja percepción de eficacia y logros profesionales "
            f"({features['eficacia_invertida']}/5.0)"
        )

    # 2. Análisis de Desempeño y Carga
    if features.get("completion_rate", 1.0) < 0.6:
        reasons.append(
            f"Tasa de cumplimiento de tareas baja "
            f"({features['completion_rate']*100:.0f}%) — posible sobrecarga."
        )
    
    if features.get("assigned_tasks", 0) > 15:
        reasons.append(
            f"Volumen de tareas asignadas por encima del promedio saludable ({features['assigned_tasks']} tareas)."
        )

    # 3. Indicadores de Alerta Temprana (Ausentismo)
    if features.get("absences", 0) >= 5:
        reasons.append(
            f"Alto número de ausencias ({features['absences']} días)."
        )
    
    if features.get("employee_calls", 0) >= 3:
        reasons.append(
            f"Alta cantidad de llamados de atención ({features['employee_calls']} llamados)."
        )
 
    # 4. Caso por defecto si el modelo predice riesgo pero los features individuales no superan umbrales
    if not reasons and burnout_class not in ["Muy Bajo", "Bajo", "Medio"]:
        reasons.append(
            "El modelo detectó una combinación multivariable de riesgo, aunque los indicadores individuales están en rangos moderados."
        )

    return reasons
