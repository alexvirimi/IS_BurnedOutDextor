#Endpoint para la creacion y consulta de detalles de trabajadores, solo RRHH puede crear, pero cualquiera puede consultar
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.company_service import CompanyService
from app.schemas.company_scheme import CompanyResponse, CompanyCreate
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from pydantic import ValidationError
from app.exceptions import BusinessValidationError
from uuid import UUID

router = APIRouter(prefix="/company", tags=["Company"])

@router.get("/", response_model=list[CompanyResponse])
# Obtiene la información de todos los trabajadores
def read_workers_info(db: Session = Depends(get_db)):
    service = CompanyService(db)
    return service.get_workers_info()

# Obtiene todos los detalles de un trabajador dada la id de sus detalles
@router.get("/{identifier}", response_model=CompanyResponse)
def read_worker_info(identifier: UUID, db: Session = Depends(get_db)):
    service = CompanyService(db)

    company = service.get_worker_info(identifier)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalles de trabajador no encontrados"
        )

    return company

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_worker_info(
    payload: CompanyCreate = Depends(CompanyCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = CompanyService(db)
    try:
        return service.create_worker_info(payload.model_dump())
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except (BusinessValidationError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )