## Estado actual
- No se tiene sistema estructurado para detectar señales de burnout
- Se realizan encuestas anuales
- Dependen de reportes subjetivos
- No se tienen métricas cruzadas
- No dispone de herramientas analíticas que permitan visualizar tendencias en tiempo real
- Gestión de talentos es ficticio, solo importa la contribución a la empresa
- Costos adicionales deberán estar fundamentados.
## Tensión entre áreas
- **Gerencia general:** exige una herramienta predictiva para intervenir antes de perder talento
- **RRHH:** Respetar confidencialidad y no generar sensación de vigilancia
- **Área jurídica**: debe cumplir estándares de protección y privacidad laboral
- **Área de tecnología:** arquitectura modular
- **Colaboradores:** expresan preocupación por posibles malinterpretaciones automatizadas de su estado emocional. (precisión)
## Necesidad (supuesta)
Se busca lo siguiente:
- Analice variables relacionadas con carga laboral, desempeño, ausentismo y resultados de micro-encuestas internas
- Identifique patrones que indiquen riesgo potencial de burnout
- Genere alertas tempranas con niveles de riesgo estimado.
- Permita validación humana por parte de Recursos Humanos.
- Ofrezca visualización consolidada para toma de decisiones estratégicas. Sea escalable y técnicamente sostenible
## Expectativas
Se espera lo siguiente:
- Recopilar datos periódicamente
- Procesar indicadores individuales y colectivos
- Estimar un nivel de riesgo individual y colectivo
- Permitir que RRHH pueda revisar las alertas
- Implementar intervenciones preventivas (ajuste de carga, acompañamiento y redistribución de tareas)
- Presentar dashboard con tendencias mensuales y comparativas por área
## Restricciones técnicas
- Operar en entorno académico o infraestructura de bajo costo
- No usar plataformas empresariales externas
- Los datos de entrenamiento pueden ser simulados
- El modelo deberá predecir con exactitud ($\geq90\%$)
- Extensión del proyecto: 3 meses
- Documentación técnica
## Riesgos 
- Que se perciba el sistema como mecanismo de vigilancia
- Sesgos algorítmicos (relacionado a la exactitud)
- Limitaciones de datos disponibles
- Expectativas irreales
- Manejar los datos con discreción
## Entregables esperados
Se deberá evidenciar:
- Análisis y levantamiento formal (*este documento*).
	- Restricciones
	- Necesidades
	- Actores clave
	- Riesgos
	- Evidencias de trazabilidad (Git)
- Modelado del sistema (Diagramas *de lo que está escrito aquí*).
	- Interacción entre actores y sistema.
	- Comportamiento esperado del sistema.
	- Estructura interna de componentes.
	- Arquitectura general adoptada.
- Diseño arquitectónico.
	- Separación de responsabilidades.
	- Modularidad.
	- Desacoplamiento del módulo de IA
	- Escalable a futuro
- Desarrollo e implementación.
	- Justificación del algoritmo de IA.
	- Explicación del conjunto de datos utilizado.
	- Métricas de desempeño (accuracy, precision, recall, no sé).
	- Análisis de resultados.
- Validación y pruebas.
	- Tests que validen el funcionamiento.
	- Tests del comportamiento del modelo predictivo.
- Análisis de los riesgos (*ya está hecho aquí*)
- Presentación
