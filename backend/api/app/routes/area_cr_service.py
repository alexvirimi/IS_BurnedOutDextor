from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.area_service import AreaService
from app.schemas.area_scheme import AreaResponse, AreaCreate
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

router = APIRouter(prefix="/areas", tags=["Areas"])

@router.get("/", response_model=list[AreaResponse])
# Endpoint que recibe en .JSON todas las areas usando la conexion con el servicio dispuesto
def read_areas(db: Session = Depends(get_db)):
    service = AreaService(db)
    return service.get_areas()

@router.get("/{area_id}", response_model=AreaResponse)
# Endpoint que recibe un area especifica usando su universal unique identifier (UUID) y la trae a su swagger
def read_area(area_id: UUID, db: Session = Depends(get_db)):
    service = AreaService(db)
    area = service.get_area_by_id(area_id)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área no encontrada")
    return area

@router.post("/", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
# Endpoint que crea un área. Solo RRHH puede crear áreas.
def create_area(
    payload: AreaCreate = Depends(AreaCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = AreaService(db)
    return service.create_area(payload.model_dump())