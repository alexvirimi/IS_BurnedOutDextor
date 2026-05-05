from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Result
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from app.dbmodels import Group, Worker, Area, Surveys

#En la tabla area solo se pueden realizar las lecturas de la misma.
class ResultService:
    def __init__(self, db: Session):
        self.repo = ur(Result, db)
        self.db = db         

    def get_results(self):
        return self.repo.get_all()       

    def get_result_by_id(self, id: UUID):
        return self.repo.get_by_id(id)
    
    def get_results_by_worker(self, worker_id: UUID):
        """
        Obtiene todos los resultados de un trabajador específico.
        Utilizado por trabajadores comunes para ver sus propios resultados.
        """
        return self.db.query(Result).filter(Result.id_worker == worker_id).all()
    
    def get_results_by_group(self, group_id: UUID):
        """
        Obtiene todos los resultados de los trabajadores de un grupo específico.
        Utilizado por líderes para ver resultados de su grupo.
        """
        return self.db.query(Result).filter(Result.id_group == group_id).all()

    def create_result(self, data: dict): 
        #En este create se hace la validación de que existan el grupo, el trabajador, el área y la encuesta antes de crear el resultado, porque si no existen no se puede crear el resultado
        #si se intenta crear un resultado con un grupo, trabajador, área o encuesta que no existe, se lanza una excepción con el mensaje de que no existe.
        group = ur(Group, self.db).get_by_id(data["id_group"])
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El grupo no existe"
            )
        worker = ur(Worker, self.db).get_by_id(data["id_worker"])
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe"
            )
        area = ur(Area, self.db).get_by_id(data["id_area"])
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El área no existe"
            )
        surveys = ur(Surveys, self.db).get_by_id(data["id_survey"])
        if not surveys:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta no existe"
            )    
        return self.repo.create(data)
