# Este módulo define los endpoints para gestionar resultados de encuestas.
# Los resultados representan los puntajes de burnout obtenidos por trabajadores al completar encuestas.
# Implementa control de acceso basado en roles:
# - Nivel 1 (común): Solo ve sus propios resultados
# - Nivel 2 (líder): Ve resultados de su grupo
# - Nivel 3 (RRHH): Ve todos los resultados

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.result_service import ResultService
from app.schemas.result_scheme import ResultResponse, ResultCreate
from app.deps.auth_deps import get_current_user, require_role
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/", response_model=list[ResultResponse])
def read_results(
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Endpoint para obtener resultados según el rol del usuario.
    # Nivel 1 retorna solo sus resultados, nivel 2 retorna su grupo, nivel 3 retorna todos.
    service = ResultService(db)
    
    # Si el usuario es de nivel 1 (común), retorna solo sus propios resultados
    if current_user.rank_level == 1:
        return service.get_results_by_worker(current_user.worker_id)
    
    # Si el usuario es de nivel 2 (líder), retorna resultados de su grupo
    elif current_user.rank_level == 2:
        return service.get_results_by_group(current_user.id_group)
    
    # Si el usuario es de nivel 3 (RRHH), retorna todos los resultados
    elif current_user.rank_level == 3:
        return service.get_results()
    
    # Por seguridad, si no es ninguno de estos niveles, lanza excepción
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para ver resultados"
    )

@router.get("/{result_id}", response_model=ResultResponse)
def read_result(
    result_id: UUID,
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Endpoint para obtener un resultado específico.
    # Valida permisos según el rol del usuario.
    service = ResultService(db)
    result = service.get_result_by_id(result_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado no encontrado")
    
    # Valida permisos según el rol
    if current_user.rank_level == 1:
        # Nivel 1: Solo puede ver sus propios resultados
        if result.id_worker != current_user.worker_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este resultado"
            )
    elif current_user.rank_level == 2:
        # Nivel 2: Solo puede ver resultados de su grupo
        if result.id_group != current_user.id_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este resultado. Es de otro grupo."
            )
    # Nivel 3 (RRHH): Puede ver cualquier resultado
    
    return result

@router.post("/", response_model=ResultResponse, status_code=status.HTTP_201_CREATED)
def create_result(
    payload: ResultCreate = Depends(ResultCreate.as_form),
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para crear un nuevo resultado.
    Solo usuarios de nivel 2 (líderes) y 3 (RRHH) pueden crear resultados.
    """
    # Valida que el usuario tenga permiso para crear resultados
    if current_user.rank_level not in [2, 3]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear resultados. Solo líderes y RRHH pueden crear resultados."
        )
    
    service = ResultService(db)
    return service.create_result(payload.model_dump())