from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.rank_service import RankService
from app.schemas.rank_scheme import RankResponse, RankCreate
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

router = APIRouter(prefix="/rank", tags=["Rank"])

@router.get("/", response_model=list[RankResponse])
# Endpoint que recibe en .JSON todos los rangos (ranks) usando la conexión con el servicio dispuesto
def read_ranks(db: Session = Depends(get_db)):
    service = RankService(db)
    return service.get_ranks()

@router.get("/{rank_id}", response_model=RankResponse)
# Endpoint que recibe un ID de rank y lo trae
def read_rank(rank_id: UUID, db: Session = Depends(get_db)):
    service = RankService(db)
    rank = service.get_rank_by_id(rank_id)
    if not rank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rango no encontrado")
    return rank

@router.post("/", response_model=RankResponse, status_code=status.HTTP_201_CREATED)
# Endpoint que crea un rank. Solo RRHH puede crear rangos.
def create_rank(
    payload: RankCreate = Depends(RankCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = RankService(db)
    return service.create_rank(payload.model_dump())

# Mi primer endpoint, le dedico este logro a Mario - Juanca 10/04/2026