from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.rank_service import RankService
from app.schemas.rank_scheme import RankResponse, RankCreate
from uuid import UUID

router = APIRouter(prefix="/rank", tags=["Rank"])

@router.get("/", response_model=list[RankResponse]) # endpoint que recibe en .JSON todas los rangos (ranks) usando la conexión con el servicio dispuesto
def read_ranks(db: Session = Depends(get_db)):
    service = RankService(db)
    return service.get_ranks()



@router.get("/{rank_id}", response_model=RankResponse) # endpoint que recibe un ID de rank y lo trae
def read_rank(rank_id: UUID, db: Session = Depends(get_db)):
    service = RankService(db)
    rank = service.get_rank_by_id(rank_id)
    if not rank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rango no encontrado")
    return rank

@router.post("/", response_model=RankResponse, status_code=status.HTTP_201_CREATED) # endpoint que crea un rank una vez que se le da
def create_rank(payload: RankCreate, db: Session = Depends(get_db)):
    service = RankService(db)
    return service.create_rank(payload.model_dump())

# mi primer endpoint, le dedico este logro a Mario - Juanca 10/04/2026