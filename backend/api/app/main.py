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
from app.routes.survey_assignment_service import router as survey_assignment_router
from app.routes.workers_cr_service import router as worker_router
from app.routes.auth_service import router as auth_router
from app.routes.psicometric_value_r_service import router as psicometric_variable_router

# ─── App ──────────────────────────────────────────────────────────────────────
#
# Swagger security note
# ─────────────────────
# Protected endpoints use APIKeyCookie + HTTPBearer (see auth_deps.py).
# Swagger UI shows the padlock on every route that declares a Security()
# dependency.  To authenticate in Swagger:
#   1. POST /auth/login via the "Try it out" form.
#   2. Copy the access_token value from the response cookie (browser DevTools).
#   3. Click the padlock → paste the token as a Bearer value.
#
# We intentionally do NOT set swagger_ui_init_oauth / oauth2_redirect_url
# because this app does not use an OAuth2 flow.  Adding those keys causes
# FastAPI to inject an OAuth2 security requirement that conflicts with the
# cookie/Bearer scheme and silently drops the cookie from authenticated
# requests — which was the regression introduced in the previous commit.

app = FastAPI(
    title="BurnedOutDextor API",
    description="API para el proyecto BurnedOutDextor.",
    version="1.0.0",
    # persistAuthorization keeps Swagger's Bearer token across page reloads.
    # It is safe to keep; it only affects the Swagger UI state, not the app.
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
#
# allow_credentials=True is required so the browser forwards the HttpOnly
# access_token cookie on cross-origin requests.
# Wildcard origins ("*") are rejected by browsers when credentials are sent,
# so origins must be listed explicitly.

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(area_router)
app.include_router(answer_router)
app.include_router(company_router)
app.include_router(group_router)
app.include_router(question_router)
app.include_router(question_survey_router)
app.include_router(rank_router)
app.include_router(result_router)
app.include_router(survey_router)
app.include_router(survey_assignment_router)
app.include_router(worker_router)
app.include_router(auth_router)
app.include_router(psicometric_variable_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
