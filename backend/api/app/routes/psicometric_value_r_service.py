from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.psicometric_variable_service import PsicometricVariableService
from app.schemas.psicometric_variable_scheme import PsicometricVariableResponse

router = APIRouter(prefix="/psicometric_variable", tags=["Psicometric Variable"])

@router.get("/", response_model=list[PsicometricVariableResponse], status_code=status.HTTP_200_OK)
# Obtiene todas las variables psicométricas predefinidas.
def read_psicometric_variables(db: Session = Depends(get_db)):
    service = PsicometricVariableService(db)
    return service.get_psicometric_variables()

