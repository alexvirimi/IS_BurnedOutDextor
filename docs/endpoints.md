# Endpoints del proyecto

Este documento describe los endpoints del backend principal y del AI Service. El objetivo es consolidar los recursos disponibles y mostrar los puntos de acceso para la lógica de negocio y la inferencia de burnout.

## Índice

- [Areas](#tabla-areas)
- [Answers](#tabla-answers)
- [Company](#tabla-company)
- [Groups](#tabla-groups)
- [Question](#tabla-question)
- [QuestionSurvey](#tabla-questionsurvey)
- [Rank](#tabla-rank)
- [Results](#tabla-results)
- [Survey](#tabla-survey)
- [Worker](#tabla-worker)
- [AI Service](#ai-service)

> Aún no se cuenta con un endpoint que mande los datos de `Answers` al modelo de IA y otro que retorne los resultados de la IA a la tabla `Results`, pero se tiene pensado incluirse a futuro.

# Tabla Areas
Create + Read

| Método | Endpoint         | Descripción                                       | Parámetros |
| ------ | ---------------- | ------------------------------------------------- | ---------- |
| `GET`  | /areas           | Obtiene todas las áreas                           | -          |
| `POST` | /areas/          | Crea un área de acuerdo a la información brindada | -          |
| `GET`  | /areas/{area_id} | Obtiene la información de un área                 | `area_id`  |

# Tabla Answers
Create + Read

| Método | Endpoint             | Descripción                                      | Parámetros  |
| ------ | -------------------- | ------------------------------------------------ | ----------- |
| `GET`  | /answers/            | Obtiene todas las respuestas registradas         | -           |
| `POST` | /answers/            | Registra una respuesta individual de encuesta    | -           |
| `GET`  | /answers/{answer_id} | Obtiene los datos de una respuesta en particular | `answer_id` |

Es la **fuente principal de datos para el modelo de IA**.

# Tabla Company
Create + Read

| Método | Endpoint                  | Descripción                                                      | Parámetros       |
| ------ | ------------------------- | ---------------------------------------------------------------- | ---------------- |
| `GET`  | /company/                 | Obtiene toda la información de todos los trabajadores            | -                |
| `POST` | /company/                 | Crea los detalles de un trabajador                               | -                |
| `GET`  | /company/{worker_info_id} | Obtiene los detalles de un trabajador dado el ID de sus detalles | `worker_info_id` |

# Tabla Groups
Create + Read.

| Método  | Endpoint                 | Descripción                                        | Parámetros |
| ------- | ------------------------ | -------------------------------------------------- | ---------- |
| `GET`   | /group/                  | Obtiene todos los grupos                           | -          |
| `POST`  | /group/                  | Crea un grupo de acuerdo a su información          | -          |
| `PATCH` | /group/{group_id}/leader | Asigna un líder a un grupo[^1]                     | `group_id` |
| `GET`   | /group/{group_id}        | Obtiene toda la información de un grupo dado su id | `group_id` |

# Tabla Question
CRUD completo

| Método   | Endpoint                | Descripción                                     | Parámetros    |
| -------- | ----------------------- | ----------------------------------------------- | ------------- |
| `GET`    | /question/              | Obtiene todas las preguntas                     | -             |
| `POST`   | /question/              | Crea una pregunta                               | -             |
| `GET`    | /question/{question_id} | Obtiene los datos de una pregunta dada su ID    | `question_id` |
| `PUT`    | /question/{question_id} | Actualiza los campos de una pregunta dada su ID | `question_id` |
| `DELETE` | /question/{question_id} | Elimina una pregunta dada su ID                 | `question_id` |

# Tabla QuestionSurvey
CRUD completo. Esta tabla maneja las relaciones entre preguntas y encuestas.

| Método   | Endpoint                              | Descripción                                                    | Parámetros           |
| -------- | ------------------------------------- | -------------------------------------------------------------- | -------------------- |
| `GET`    | /question_survey/                     | Obtiene todas las relaciones encuesta-pregunta                 | -                    |
| `POST`   | /question_survey/                     | Crea una relación encuesta-pregunta                            | -                    |
| `GET`    | /question_survey/{question_survey_id} | Obtiene los datos de una relación encuesta-pregunta dada su ID | `question_survey_id` |
| `PUT`    | /question_survey/{question_survey_id} | Actualiza la relación encuesta-pregunta dada su ID             | `question_survey_id` |
| `DELETE` | /question_survey/{question_survey_id} | Elimina una relación encuesta-pregunta dada su ID              | `question_survey_id` |
| `POST`   | /question_survey/assign               | Asigna varias preguntas a una sola encuesta                    | -                    |

# Tabla Rank
Create + Read

| Método | Endpoint        | Descripción                              | Parámetros |
| ------ | --------------- | ---------------------------------------- | ---------- |
| `GET`  | /rank           | Obtiene la lista de todos los rangos     | -          |
| `POST` | /rank/          | Crea un rango                            | -          |
| `GET`  | /rank/{rank_id} | Obtiene los datos de un rango dado su ID | `rank_id`  |

# Tabla Results
Create + Read

| Método | Endpoint             | Descripción                                                          | Parámetros  |
| ------ | -------------------- | -------------------------------------------------------------------- | ----------- |
| `GET`  | /results/            | Obtiene todos los resultados generados por la IA                     | -           |
| `POST` | /results/            | Crea el registro de los resultados de un usuario generados por la IA | -           |
| `GET`  | /results/{result_id} | Obtiene los detalles de un resultado generado por la IA dado su ID   | `result_id` |

# Tabla Survey
Create + Read

| Método | Endpoint                      | Descripción                                          | Parámetros  |
| ------ | ----------------------------- | ---------------------------------------------------- | ----------- |
| `GET`  | /survey/                      | Obtiene todas las encuestas creadas                  | -           |
| `POST` | /survey/                      | Crea una encuesta                                    | -           |
| `GET`  | /survey/{survey_id}           | Obtiene los detalles de una encuesta dada su ID      | `survey_id` |
| `GET`  | /survey/{survey_id}/questions | Obtiene todas las preguntas asociadas a una encuesta | `survey_id` |

# Tabla Worker
Create + Read

| Método | Endpoint                    | Descripción                                                           | Parámetros  |
| ------ | --------------------------- | --------------------------------------------------------------------- | ----------- |
| `GET`  | /worker/                    | Obtiene la información básica de cada trabajador                      | -           |
| `POST` | /worker/                    | Crea la información básica de un trabajador                           | -           |
| `GET`  | /worker/{worker_id}         | Obtiene la información básica de un trabajador dada su ID             | `worker_id` |
| `GET`  | /worker/{worker_id}/details | Obtiene los datos completos (con nombres) de un trabajador dado su ID | `worker_id` |

# AI Service

Este servicio de inferencia está implementado en `backend/ai-service/` y expone los endpoints del modelo.

| Método | Endpoint | Descripción |
| ------ | -------- | ----------- |
| `GET`  | /health  | Comprueba que el servicio esté activo y que el modelo esté cargado. |
| `POST` | /predict | Recibe datos de un trabajador y devuelve la predicción de riesgo de burnout. |

## Ejemplo de uso de `POST /predict`

```json
{
  "worker_id": "00000000-0000-0000-0000-000000000000",
  "survey_id": "00000000-0000-0000-0000-000000000000",
  "assigned_tasks": 20,
  "completed_tasks": 15,
  "absences": 2,
  "employee_calls": 1,
  "completion_rate": 0.75,
  "seniority_years": 2.5,
  "age": 29,
  "gender_enc": 1,
  "worker_type_enc": 0,
  "location_enc": 0,
  "avg_agotamiento": 4.0,
  "avg_despersonalizacion": 3.2,
  "eficacia_invertida": 2.8
}
```

# Integración con IA

Este prototipo contempla la integración de los datos de negocio con el servicio de IA. Actualmente no hay un endpoint final en el backend principal que envíe automáticamente `Answers` al servicio de IA, ni que persista los `Results` retornados.

[^1]: Se requiere del Patch para corregir una limitación con la base de datos, por lo que se crea primero el grupo sin líder para que luego se le pueda asignar. Esto también cubre la posibilidad de que un grupo pueda cambiar de líder.
