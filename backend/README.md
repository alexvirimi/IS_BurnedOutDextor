# Backend

Este directorio contiene los servicios backend del proyecto `IS_BurnedOutDextor`.

## Contenido

- `backend/api/` - Servicio principal de API REST en FastAPI.
- `backend/ai-service/` - Servicio de inferencia de burnout en FastAPI.

## Ejecución local

### API principal

```bash
cd backend/api
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### AI Service

```bash
cd backend/ai-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Documentación adicional

- `backend/api/pyproject.toml`
- `backend/ai-service/requirements.txt`
- `docs/endpoints.md`
