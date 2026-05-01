from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Area
from sqlalchemy.orm import Session
from uuid import UUID

#En la tabla area solo se pueden realizar las lecturas de la misma.
class AreaService:
    def __init__(self, db: Session):
        self.repo = ur(Area, db)         # modelo + sesión

    def get_areas(self):
        return self.repo.get_all()       # sin parámetros, ya sabe el modelo

    def get_area_by_id(self, id:UUID):
        return self.repo.get_by_id(id)

    def create_area(self, data: dict):
        return self.repo.create(data)