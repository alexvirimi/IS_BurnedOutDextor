import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.dbmodels.base import Base
from app.routes.area_cr_service import router as area_router
from app.routes.answer_cr_service import router as answer_router
from app.routes.company_cr_service import router as company_router
from app.routes.group_cr_service import router as group_router
from app.routes.question_surveys_crud_service import router as question_survey_router
from app.routes.questions_crud_service import router as question_router
from app.routes.rank_cr_service import router as rank_router
from app.routes.result_cr_service import router as result_router
from app.routes.surveys_cr_service import router as survey_router
from app.routes.workers_cr_service import router as worker_router

# Inicializa la aplicación FastAPI
app = FastAPI(
    title="BurnedOutDextor API",
    description="API para el proyecto BurnedOutDextor. Gestiona encuestas, preguntas, respuestas, trabajadores, empresas, áreas, grupos, rangos y resultados.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


app.include_router(area_router)
app.include_router(answer_router)
app.include_router(company_router)
app.include_router(group_router)
app.include_router(question_router)
app.include_router(question_survey_router)
app.include_router(rank_router)
app.include_router(result_router)
app.include_router(survey_router)
app.include_router(worker_router)


static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Forgive me Father, for I have sinned. I will now atone for my sins. - Juanca