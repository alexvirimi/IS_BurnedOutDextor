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

# Mapeo canónico compartido (ya existe en el archivo, referenciado aquí)
_CLASS_TO_SCORE: dict[str, int] = {
    "Muy Bajo": 1,
    "Bajo": 2,
    "Medio": 3,
    "Moderado": 4,
    "Alto": 5,
}
 
 
@router.get(
    "/group/{group_id}/progress",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
)
def get_group_progress(
    group_id: UUID,
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Aggregated burnout progress for a group.
    Returns the average burnout score per survey date across all workers in the group.
    Accessible by leaders (rank 2) of that group and all HR (rank 3).
    """
    # Access control
    if current_user.rank_level == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver resultados de grupo",
        )
    if current_user.rank_level == 2 and current_user.id_group != group_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes ver resultados de tu propio grupo",
        )
 
    from app.dbmodels import Result
    from sqlalchemy import func
 
    # Fetch all results for this group
    results = (
        db.query(Result)
        .filter(Result.id_group == group_id)
        .order_by(Result.generation_date)
        .all()
    )
 
    return _aggregate_results_by_date(results)
 
 
@router.get(
    "/area/{area_id}/progress",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
)
def get_area_progress(
    area_id: UUID,
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Aggregated burnout progress for an area.
    Returns the average burnout score per survey date across all workers in the area.
    HR only.
    """
    if current_user.rank_level != 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo RRHH puede ver resultados por área",
        )
 
    from app.dbmodels import Result
 
    results = (
        db.query(Result)
        .filter(Result.id_area == area_id)
        .order_by(Result.generation_date)
        .all()
    )
 
    return _aggregate_results_by_date(results)
 
 
@router.get(
    "/worker/{worker_id}/progress",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
)
def get_worker_progress(
    worker_id: UUID,
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Burnout progress for a specific worker.
    Leaders can view workers in their group. HR can view any worker.
    """
    if current_user.rank_level == 1 and current_user.worker_id != worker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver resultados de otro trabajador",
        )
 
    from app.dbmodels import Result, Worker
 
    # Leaders: verify the target worker belongs to their group
    if current_user.rank_level == 2:
        target = db.query(Worker).filter(Worker.id == worker_id).first()
        if not target or target.id_group != current_user.id_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El trabajador no pertenece a tu grupo",
            )
 
    service = ResultService(db)
    results = service.get_results_by_worker(worker_id)
 
    data = []
    for r in sorted(results, key=lambda x: x.generation_date):
        data.append(
            {
                "fecha": r.generation_date.isoformat(),
                "clase": r.burnout_class,
                "valor": _CLASS_TO_SCORE.get(r.burnout_class, 0),
                "confianza": float(r.burnout_confidence),
                "encuesta_id": str(r.id_survey),
            }
        )
    return data
 
 
# ── Private helper ─────────────────────────────────────────────────────────────
 
 
def _aggregate_results_by_date(results) -> list[dict]:
    """
    Groups results by generation_date, averages the burnout scores,
    and returns a chart-ready list ordered by date ascending.
 
    Each point represents one 'survey round' on that date:
    - valor:     mean of numeric scores (rounded to 1 decimal)
    - confianza: mean confidence
    - clase:     label closest to the mean valor
    - workers:   number of workers whose results contributed
    """
    from collections import defaultdict
 
    _SCORE_TO_CLASS = {
        1: "Muy Bajo",
        2: "Bajo",
        3: "Medio",
        4: "Moderado",
        5: "Alto",
    }
 
    by_date: dict[str, list] = defaultdict(list)
    for r in results:
        key = r.generation_date.isoformat()
        score = _CLASS_TO_SCORE.get(r.burnout_class, 0)
        if score > 0:  # skip results with unknown class
            by_date[key].append(
                {
                    "valor": score,
                    "confianza": float(r.burnout_confidence),
                    "survey_id": str(r.id_survey),
                }
            )
 
    data = []
    for fecha in sorted(by_date.keys()):
        points = by_date[fecha]
        if not points:
            continue
        avg_valor = sum(p["valor"] for p in points) / len(points)
        avg_confianza = sum(p["confianza"] for p in points) / len(points)
        # Round to nearest integer for label, keep float for chart position
        nearest_class = _SCORE_TO_CLASS.get(round(avg_valor), "Medio")
        data.append(
            {
                "fecha": fecha,
                "clase": nearest_class,
                "valor": round(avg_valor, 2),
                "confianza": round(avg_confianza, 4),
                "workers": len(points),
                # Use the most common survey_id on that date (first as tie-break)
                "encuesta_id": points[0]["survey_id"],
            }
        )
 
    return data

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
