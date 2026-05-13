# Flujo de Predicción Automática de Burnout

## Descripción General

Cuando un trabajador completa una encuesta (responde todas las preguntas), el sistema automáticamente:
1. Crea las respuestas en la BD
2. Detecta que la encuesta está completa
3. Dispara la predicción de burnout en background
4. Genera resultados automáticamente
5. Guarda los resultados en la tabla `result`

## Cambios Realizados

### Backend: `answer_service.py`

Se agregaron dos nuevas funciones auxiliares y se modificaron dos métodos principales:

#### 1. `_check_survey_completion(db, worker_id, survey_id)`
- **Propósito**: Verifica si un trabajador ha respondido TODAS las preguntas de una encuesta
- **Lógica**:
  - Cuenta total de preguntas en la encuesta
  - Cuenta respuestas del trabajador para esa encuesta
  - Retorna `True` si respuestas >= total de preguntas
- **Manejo de errores**: Retorna `False` si hay algún error, sin bloquear el flujo

#### 2. `_trigger_burnout_prediction(db, worker_id, survey_id)`
- **Propósito**: Ejecuta la predicción de burnout de forma asincrónica
- **Proceso**:
  1. Llama a `BurnoutService.predict_worker_burnout()`
  2. La predicción obtiene features del trabajador desde la vista `vw_worker_burnout_features`
  3. Envía features al AI Service (puerto 8001)
  4. Recibe predicción con clase, confianza y razones
  5. Genera sugerencias de intervención
  6. Guarda resultado en tabla `result`
- **Manejo de errores**: Captura todas las excepciones y las loguea sin bloquear

#### 3. `create_bulk_answers()` - Modificado
```python
# Después de crear todas las respuestas:
if _check_survey_completion(self.db, worker_id, survey_id):
    asyncio.create_task(
        _trigger_burnout_prediction(self.db, worker_id, survey_id)
    )
```
- La predicción se ejecuta en **background** (no bloquea la respuesta HTTP)
- La respuesta al cliente retorna inmediatamente
- La predicción se ejecuta en paralelo

#### 4. `create_answer_from_user()` - Modificado
- Igual lógica: detecta completitud después de cada respuesta
- Dispara predicción cuando se completa

## Flujo de Ejecución

```
Usuario responde encuesta
     ↓
[POST] /answers/bulk o /answers/respond
     ↓
AnswerService.create_bulk_answers()
     ↓
Valida datos y crea respuestas
     ↓
_check_survey_completion()
     ↓
¿Todas las preguntas respondidas?
     ├─ NO → Retorna respuesta al cliente ✅
     └─ SÍ → asyncio.create_task(_trigger_burnout_prediction())
              ↓
              Retorna respuesta al cliente ✅
              ↓
              [En background]
              BurnoutService.predict_worker_burnout()
              ├─ get_worker_features()
              ├─ [POST] http://localhost:8001/predict
              ├─ InterventionService.generate_suggestion()
              └─ BurnoutService._save_result()
                  └─ UPDATE/INSERT en tabla result
```

## Impacto en el Frontend

### Antes (sin automatización)
1. Usuario responde encuesta
2. Respuestas se guardan
3. Usuario debe hacer algo manual para ver resultados
4. Gráfica no se actualiza automáticamente

### Ahora (con automatización)
1. Usuario responde encuesta
2. Respuestas se guardan
3. Sistema automáticamente genera predicción
4. Resultados se guardan en BD
5. Si el frontend hace polling de `/results`, verá datos actualizados

### Recomendaciones para Frontend

#### Opción 1: Polling (Simple)
```javascript
// Consulta resultados cada 5 segundos
setInterval(async () => {
  const results = await fetch('/api/results');
  updateChart(results);
}, 5000);
```

#### Opción 2: WebSocket (Mejor en Tiempo Real)
```javascript
// Escucha eventos de cambios en resultados
const ws = new WebSocket('ws://localhost:8000/ws/results');
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  updateChart(result);
};
```

#### Opción 3: Query Manual Post-Respuesta
```javascript
// Después de enviar respuesta, espera un poco y consulta
async function submitSurvey(answers) {
  await fetch('/api/answers/bulk', { method: 'POST', body: answers });
  
  // Espera 2-3 segundos a que se genere la predicción
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Consulta resultados actualizados
  const results = await fetch('/api/results');
  updateChart(results);
}
```

## Estructura de Datos en BD

### Tabla `result`
Después de la predicción, se crea/actualiza un registro:

```sql
{
  id: UUID,
  id_worker: UUID,
  id_group: UUID,
  id_area: UUID,
  id_survey: UUID,
  burnout_class: STRING ('Bajo' | 'Medio' | 'Alto'),
  burnout_confidence: FLOAT (0-1),
  burnout_reasons: TEXT (razones separadas por \n),
  suggested_intervention: TEXT,
  intervention_status: STRING ('Pendiente' | 'En Proceso' | 'Completada'),
  generation_date: DATE,
  flag: BOOLEAN
}
```

## Logging y Debugging

Se agregan logs en cada paso:

```
INFO: Survey completion check - Worker: {worker_id}, Survey: {survey_id}, Total: 22, Answered: 22
INFO: Survey {survey_id} completed by worker {worker_id}. Triggering burnout prediction...
INFO: Triggering burnout prediction for worker {worker_id}, survey {survey_id}
INFO: Burnout prediction completed successfully for worker {worker_id}: Class=Medio, Confidence=0.75
```

Para ver los logs:
- **Docker**: `docker logs api_container`
- **Local**: Ver stdout del proceso FastAPI

## Casos Edge

### ¿Qué pasa si la predicción falla?
- La respuesta HTTP se retorna exitosamente (status 201)
- Se loguea el error
- El usuario no recibe error
- Puede reintentar manualmente con `/burnout/predict`

### ¿Qué pasa si el AI Service no está disponible?
- Se loguea error: "AI Service no disponible"
- Las respuestas se guardan de todas formas
- Cuando AI Service esté disponible, puede reintentar

### ¿Qué pasa si hay respuestas duplicadas?
- Si ya existe resultado para hoy con mismo worker+survey, se actualiza (UPDATE)
- Si es nueva fecha, se inserta (INSERT)

## Performance

- **Tiempo de respuesta HTTP**: No se ve afectado (predicción es async)
- **Carga en BD**: Mínima (solo SELECT COUNT y INSERT/UPDATE por encuesta completada)
- **Carga en AI Service**: Se ejecuta una vez por encuesta completada por worker
- **Escalabilidad**: Bien, cada predicción es independiente

## Próximos Pasos (Opcional)

1. **Cache de features**: Cachear `vw_worker_burnout_features` para encuestas recientes
2. **Batch predictions**: Agrupar predicciones si múltiples workers terminan simultáneamente
3. **WebSocket real-time**: Implementar en frontend para actualización instantánea
4. **Retry automático**: Si predicción falla, reintentar cada 60 segundos hasta 3 veces
