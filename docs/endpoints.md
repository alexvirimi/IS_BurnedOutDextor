Sujeto a cambios mientras tenemos retroalimentación del docente
# Tabla Answer
Solo Create + Read, aún no necesita Delete ni Update en el MVP. Testing

| Método | Endpoint                  | Descripción                                                              | Parámetros           |
| ------ | ------------------------- | ------------------------------------------------------------------------ | -------------------- |
| `POST` | /answers                  | Registra una respuesta individual de encuesta                            | -                    |
| `GET`  | /answers/user/{user_id}   | Obtiene todas las respuestas de un usuario para construcción de features | `user_id`            |
| `GET`  | /answers/aggregate        | Obtiene métricas agregadas de respuestas por área o grupo                | `area_id` `group_id` |

Es la **fuente principal de datos para el modelo de IA**

# Tabla Area
Read only

| Método | Endpoint         | Descripción                       | Parámetros |
| ------ | ---------------- | --------------------------------- | ---------- |
| `GET`  | /areas           | Obtiene todas las áreas           | -          |
| `GET`  | /areas/{id}      | Obtiene la información de un área | `id`       |
| `GET`  | /areas/{id}/info |                                   | -          |
# Integración con IA
no es una tabla pero puede que se necesite para conectar las anteriores. es un punto de integración entre Answer y Company

| Método | Endpoint   | Descripción                                                    | Parámetros |
| ------ | ---------- | -------------------------------------------------------------- | ---------- |
| `POST` | /ml/predit | Ejecuta predicción de riesgo de burnout con datos consolidados | -          |

Todas estas tablas de aquí en adelante son Read Only para no meternos con lógica de empresa

# Tabla Rank
Read only

| Método | Endpoint          | Descripción                                                  | Parámetros  |
| ------ | ----------------- | ------------------------------------------------------------ | ----------- |
| `GET`  | /rank             | Obtiene la lista de todos los rangos presentes en la empresa | -           |
| `GET`  | /rank/{user_id} | Obtiene el rango al que pertenece un usuario                 | `user_id` |
# Tabla Worker
Read only (AI purposes), no nos vamos a meter con la lógica de la empresa

| Método | Endpoint            | Descripción                                                         | Parámetros  |
| ------ | ------------------- | ------------------------------------------------------------------- | ----------- |
| `GET`  | /worker/{user_id} | Obtiene todos los campos del trabajador menos el nombre y apellidos | `user_id` |
# Tabla Company

| Método | Endpoint             | Descripción                                                                                                     | Parámetros  |
| ------ | -------------------- | --------------------------------------------------------------------------------------------------------------- | ----------- |
| `GET`  | /company/{user_id} | Obtiene todos los campos del trabajador respecto a la tabla company, tales como tareas, faltas, ubicación, etc. | `user_id` |
# Tabla Group

| Método | Endpoint          | Descripción                                                                       | Parámetros |
| ------ | ----------------- | --------------------------------------------------------------------------------- | ---------- |
| `GET`  | /group            | Obtiene todos los grupos                                                          | -          |
| `GET`  | /group/{group_id} | Obtiene el `leader_id` del líder del grupo y `area_id`  del área al que pertenece | `group_id` |
# Tabla Result
| Método | Endpoint             | Descripción                                                            | Parámetros                                                    |
| ------ | -------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------- |
| `POST` | /result              | Sube los resultados del análisis de IA para el usuario                 | `burnout_score` `hash_user` `id_group` `ìd_area` `id_surveys` |
| `PUT`  | /result/{id}/{campo} | Actualiza un campo a la vez del resultado del análisis de una encuesta | `id` `campo a actualizar`                                     |
| `GET`  | /result/{id}         | Obtiene todos campos de un resultado de IA, incluyendo el usuario      | `id`                                                          |
