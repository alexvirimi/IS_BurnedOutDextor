# IS_BurnedOutDextor

![GitHub](https://img.shields.io/badge/GitHub-IS_BurnedOutDextor-black?logo=github)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Docker](https://img.shields.io/badge/docker-supported-blue)

Proyecto de Ingeniería de Software de la Universidad Tecnológica de Bolívar.

---

## Descripción

`IS_BurnedOutDextor` es un prototipo para la detección temprana de riesgo de burnout en colaboradores. Combina una interfaz web, una API REST y un servicio de IA basado en un modelo de árbol de decisiones que produce clasificaciones y explicaciones interpretables.

## Arquitectura

El sistema está compuesto por:

- `frontend/`: Aplicación web en Next.js + React.
- `backend/api/`: API principal en FastAPI con lógica de negocio, autenticación y persistencia en PostgreSQL.
- `backend/ai-service/`: Servicio de inferencia de burnout en FastAPI que expone `/health` y `/predict`.
- `docker-compose.yml`: Orquestación de PostgreSQL, Adminer, API, AI Service y frontend.

## Servicios principales

| Servicio | Ruta local | Comentario |
| --- | --- | --- |
| Frontend | `http://localhost:3000` | UI y dashboard |
| API principal | `http://localhost:8001` | Backend REST |
| AI Service | `http://localhost:8000` | Inferencia de burnout |
| Adminer | `http://localhost:8080` | Gestión de PostgreSQL |

## Instalación rápida con Docker

```bash
docker compose up --build
```

Este comando iniciará todos los servicios y la base de datos del proyecto.

## Desarrollo local

### Backend API

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

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## Variables de entorno

El proyecto usa variables de entorno para la configuración de la base de datos y la API.

### `backend/api`

- `DATABASE_URL`: URL de conexión a PostgreSQL.
- `JWT_SECRET_KEY`: clave secreta para tokens.
- `SQLALCHEMY_ECHO`: `true`/`false` para logging SQL.
- `ALLOWED_ORIGINS`: orígenes permitidos para CORS.

### `backend/ai-service`

- `API_BASE_URL`: URL base hacia el API principal (opcional).
- `API_KEY`: clave para autenticación de integración (opcional).

## Documentación

- `docs/endpoints.md` - Endpoints del backend y del AI Service.
- `docs/AI_datastructure.md` - Estructura de datos para la IA.
- `docs/AI_model.md` - Diseño y justificación del modelo.
- `docs/ARQUITECTURA_BD.md` - Arquitectura de la base de datos.

## Licencia

Este proyecto se distribuye bajo la licencia MIT.
