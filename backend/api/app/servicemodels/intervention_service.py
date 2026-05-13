# Servicio para gestionar las intervenciones que puede generar la empresa

from typing import List, Dict

class InterventionService:
    """
    Motor de Reglas de Negocio para la Prevención de Burnout.
    Responsabilidad: Traducir diagnósticos técnicos en acciones preventivas.
    """

    @staticmethod
    def generate_suggestion(burnout_class: str, reasons: List[str], features: Dict) -> str:
        """
        Analiza el riesgo y las causas para proponer la mejor intervención.
        """
        suggestions = []

        # 1. Reglas Basadas en el Nivel de Riesgo (Score)
        if burnout_class == "Alto":
            suggestions.append("PRIORIDAD ALTA: Otorgar al menos 2 días de descanso remunerado de forma inmediata.")
        elif burnout_class == "Moderado" or burnout_class == "Medio":
            suggestions.append("PRIORIDAD MEDIA: Programar sesión de seguimiento con el equipo de bienestar.")

        # 2. Reglas Basadas en Causas Específicas (Razones de la IA)
        reasons_text = " ".join(reasons).lower()

        if "agotamiento emocional elevado" in reasons_text:
            suggestions.append("Bienestar: Revisión de límites de jornada laboral y desconexión digital.")
        
        if "despersonalizacion" in reasons_text:
            suggestions.append("Psicología: Sesión de acompañamiento para trabajar el propósito y la conexión emocional con el rol actual.")

        if "eficacia" in reasons_text or "logros profesionales" in reasons_text:
            suggestions.append("Mentoría: Programa de reconocimiento y asignación de un mentor para fortalecer la confianza y percepción de logro.")
        
        if "asignadas" in reasons_text or "tareas" in reasons_text:
            suggestions.append("Operativo: Reunión con líder directo para redistribución de carga de trabajo (Reducción sugerida: 20%).")
        
        if "llamados de atención" in reasons_text:
            suggestions.append("Consultar la causa detrás de cada llamado. "
                               "Gestión: Sesión de feedback constructivo y apoyo al desempeño para reducir presión percibida.")
        
        if "ausencias" in reasons_text:
            suggestions.append("Revisar la causa de las ausencias. " 
                               "Salud: En caso de ser necesario realizar una evaluación de salud ocupacional para identificar causas físicas del estrés.")

        # 3. Reglas Especiales (Seniority / Retención)
        if features.get("seniority_years", 0) >= 5 and burnout_class not in ["Muy Bajo", "Bajo"]:
            suggestions.append("PLAN DE RETENCIÓN: Entrevista para asegurar la permanencia del talento senior.")

        # 4. Caso por defecto, para riesgos bajos
        if not suggestions:
            if burnout_class in ["Muy Bajo", "Bajo"]:
                return "No se requiere intervención inmediata. Continuar con monitoreo preventivo."
            else:
                return "Monitoreo preventivo y entrevista de clima laboral individual."


        return "\n".join(suggestions)
