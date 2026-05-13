# AI Service

Servicio de inferencia de burnout basado en un modelo de árbol de decisiones.

## Descripción

Este servicio ofrece predicciones de riesgo de burnout en colaboradores. Recibe datos laborales, personales y psicométricos, ejecuta un pipeline de `scikit-learn` y retorna la clase de riesgo junto a una explicación de los factores más relevantes.

## Endpoints

- `GET /health` - Verifica que el servicio esté activo y que el modelo haya sido cargado.
- `POST /predict` - Recibe un JSON con los datos de un trabajador y devuelve la predicción de burnout.

## Instalación

```bash
cd backend/ai-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecución

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Carpetas importantes

- `backend/ai-service/app/` - Código del servicio.
- `backend/ai-service/models/` - Artefactos del modelo (`burnout_pipeline.pkl`, `burnout_labels.pkl`).
- `backend/ai-service/requirements.txt` - Dependencias del servicio.
