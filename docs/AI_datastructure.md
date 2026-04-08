# Parámetros
1. Número de respuestas de la encuesta
2. Sexo del trabajador
3. Edad del trabajador
4. Número de tareas asignadas al trabajador
5. Número de tareas completadas en los últimos 7 días
6. Área a la que pertenece el trabajador (*puede llegar a sesgar el modelo*)
7. Cargo al que pertenece el trabajador
8. Fecha de ingreso a la empresa
9. Metodología de trabajo (*híbrida o virtual*)
10. En qué sede trabaja (*país donde trabaja*)
11. Cantidad de faltas en los últimos 2 meses
12. Llamados de atención del empleado en los últimos 2 meses
# Umbrales de riesgo de la IA (provisionales)
La IA arrojará resultados entre 0 y 1 donde:

| Puntaje  | Interpretación             |
| -------- | -------------------------- |
| 0-0.19   | Muy bajo riesgo de Burnout |
| 0.2-0.39 | Riesgo bajo de Burnout     |
| 0.4-0.59 | Riesgo medio de Burnout    |
| 0.6-0.79 | Riesgo de Burnout moderado |
| 0.8-1    | Riesgo alto de Burnout     |
