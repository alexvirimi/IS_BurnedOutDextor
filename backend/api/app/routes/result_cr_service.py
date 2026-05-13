from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.auth_scheme import CurrentUserData

from app.schemas.result_scheme import (
    ResultResponse,
    ResultCreate,
    UpdateFlagRequest
)

from app.servicemodels.result_service import ResultService

from app.deps.auth_deps import (
    get_current_user
)

from app.deps.internal_deps import (
    verify_internal_api_key
)

router = APIRouter(
    prefix="/results",
    tags=["Results"]
)


@router.post(
    "/",
    response_model=ResultResponse,
    status_code=status.HTTP_201_CREATED
)
def create_result(
    payload: ResultCreate,
    _: None = Depends(
        verify_internal_api_key
    ),
    db: Session = Depends(get_db)
):

    service = ResultService(db)

    return service.create_result(
        payload.model_dump()
    )

@router.get(
    "/",
    response_model=list[ResultResponse]
)
def read_results(
    current_user: CurrentUserData = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    service = ResultService(db)

    if current_user.rank_level == 1:

        return service.get_results_by_worker(
            current_user.worker_id
        )

    elif current_user.rank_level == 2:

        return service.get_results_by_group(
            current_user.id_group
        )

    elif current_user.rank_level == 3:

        return service.get_results()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para ver resultados"
    )


@router.get(
    "/{result_id}",
    response_model=ResultResponse
)
def read_result(
    result_id: UUID,
    current_user: CurrentUserData = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    service = ResultService(db)

    result = service.get_result_by_id(
        result_id
    )

    if not result:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado no encontrado"
        )

    if current_user.rank_level == 1:

        if result.id_worker != current_user.worker_id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este resultado"
            )

    elif current_user.rank_level == 2:

        if result.id_group != current_user.id_group:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este resultado"
            )

    return result

# Mapeo canónico: clase → valor numérico para graficar
_CLASS_TO_SCORE: dict[str, int] = {
    "Muy Bajo": 1,
    "Bajo": 2,
    "Medio": 3,
    "Moderado": 4,
    "Alto": 5,
}

@router.get(
    "/my-progress",
    response_model=list[dict],
    status_code=status.HTTP_200_OK
)
def get_my_progress(
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Devuelve el historial de resultados del usuario autenticado,
    con fecha y valor numérico (1-5) para graficar.
    Ordenados por fecha ascendente.
    """
    service = ResultService(db)
    results = service.get_results_by_worker(current_user.worker_id)

    data = []
    for r in sorted(results, key=lambda x: x.generation_date):
        data.append({
            "fecha": r.generation_date.isoformat(),
            "clase": r.burnout_class,
            "valor": _CLASS_TO_SCORE.get(r.burnout_class, 0),
            "confianza": float(r.burnout_confidence),
            "encuesta_id": str(r.id_survey),
        })

    return data

@router.patch(
    "/{result_id}/flag",
    response_model=ResultResponse,
    status_code=status.HTTP_200_OK
)
def update_result_flag(
    result_id: UUID,
    payload: UpdateFlagRequest,
    current_user: CurrentUserData = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    service = ResultService(db)

    if current_user.rank_level == 3:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="RRHH no puede modificar flags"
        )

    if current_user.rank_level != 2:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo líderes pueden modificar flags"
        )

    result = service.get_result_by_id(
        result_id
    )

    if not result:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado no encontrado"
        )

    if result.id_group != current_user.id_group:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes modificar resultados de tu grupo"
        )

    return service.update_result_flag(
        result_id,
        payload.flag
    )
