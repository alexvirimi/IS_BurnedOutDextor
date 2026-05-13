# Inbudex API

API principal del proyecto `IS_BurnedOutDextor`.

## Overview

- ⚡ [FastAPI](https://fastapi.tiangolo.com)
- 🧰 SQLAlchemy como ORM
- 🔍 Pydantic para validación y esquemas
- 📦 Poetry para la gestión de dependencias

## Estado del proyecto

> **Fase:** En desarrollo

## Requisitos

- Python 3.12+
- Poetry
- PostgreSQL (local o via Docker)

## Instalación local

```bash
cd backend/api
poetry install
```

## Ejecución local

```bash
cd backend/api
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

La documentación automática queda disponible en `http://localhost:8001/docs`.

## Variables de entorno

- `DATABASE_URL`: cadena de conexión a PostgreSQL.
- `JWT_SECRET_KEY`: clave secreta para tokens JWT.
- `SQLALCHEMY_ECHO`: `true`/`false` para el log de SQL.
- `ALLOWED_ORIGINS`: orígenes permitidos para CORS.

## Con Docker Compose

Desde la raíz del repo:

```bash
docker compose up --build
```

## Documentación relevante

- `docs/endpoints.md`
- `backend/api/pyproject.toml`
- `backend/api/app/main.py`

## Notas

El backend principal expone múltiples rutas para la gestión de áreas, trabajadores, encuestas, preguntas, resultados y autenticación.
