# Servicio para gestionar operaciones de áreas.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Area
from sqlalchemy.orm import Session
from uuid import UUID

class AreaService:
    # Solo operaciones de lectura y creación permitidas
    def __init__(self, db: Session):
        self.repo = ur(Area, db)

    def get_areas(self):
        # Obtener todas las áreas
        return self.repo.get_all()

    def get_area_by_id(self, id: UUID):
        # Obtener área por ID
        return self.repo.get_by_id(id)

    def create_area(self, data: dict):
        # Crear nueva área
        return self.repo.create(data)