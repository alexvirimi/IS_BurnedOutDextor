Para este proyecto se usa un modelo de árbol de decisiones, debido a que este responde a las restricciones técnicas, organizacionales, éticas y de negocio que tiene TalentoHumano Corp. S.A.S. \[TC Corp.]
# Interpretabilidad (transparencia y trazabilidad)
Se alinea con la naturaleza del problema, porque RRHH necesita entender por qué un empleado es clasificado en riesgo. Este modelo permite genera reglas explícitas tipo:
```
SI (tareas_completadas < X) && (faltas > Y) -> Riesgo alto
```
Por lo que da lugar a auditoría del modelo y transparencia frente a RRHH y los empleados.

# Tipo de variables
El modelo mezcla variables heterogéneas:
- Variables numéricas (edad, tareas)
- Categóricas (sexo, área, metodología)
- Temporales (fecha ingreso)
- Conductuales (faltas, llamados de atención)

El árbol de decisiones maneja naturalmente estos tipos de variables, lo que reduce la complejidad de procesamiento y la necesidad de modelos avanzados.

Para más información respecto a los parámetros de entrada de la IA, véase [Estructura de datos para la IA](AI_datastructure.md).
# Bajo costo computacional (restricción) y flujo de datos
La propuesta de solución debe operar en un entorno de bajo costo (véanse [Requerimientos](requirements.md)), en ese sentido, el árbol de decisiones permite un entrenamiento rápido sin uso de GPU

## Sobre los datasets a usar
De momento se usarán datos simulados para el entrenamiento, por lo que no existe un histórico real robusto. Los modelos complejos (deep learning) sobreajustan y requieren grandes volúmenes de datos, mientras que el árbol sigue manteniendo la ventaja por emplear reglas lógicas simples pero útiles.

El burnout no es lineal. Muchas tareas no implican burnout per se, mientras que pocas tareas + muchas faltas puede indicar un posible problema.

Además, el árbol produce probabilidades (resultados entre 0 y 1), lo que facilita la interpretación de los resultados dentro de la lógica de negocio
# Riesgos
## Sesgos
El modelo puede llegar a sesgarse por las siguientes variables sensibles:
- Área
- Sexo
- País
Sin embargo, este sesgo es un riesgo a tomar debido a la lógica de negocio y como trabaja TC Corp (área y país), mientras que el sexo es una variable necesaria dentro del estudio puesto que el burnout se presenta con diferencias en los síntomas más pronunciados entre hombres y mujeres (sexo).
## Sobreajuste
El modelo puede llegar a tener ajustes erróneos o exagerados (entendiéndose como sesgos que no tienen sentido o no aportan valor estratégico. los sesgos mencionados en el anterior inciso pueden llegar a indicar áreas con mayor riesgo o una metodología asociada a la fatiga) respecto a otras variables. Para esto es necesaria la intervención de RRHH con validación cruzada.
## Precisión limitada vs modelos complejos
Se prioriza interpretabilidad sobre complejidad. El modelo es un MVP y no indica producto final.


