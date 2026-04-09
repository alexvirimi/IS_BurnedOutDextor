from app.unirepository import UniversalRepository as ur
from app.models import Area
from sqlalchemy.orm import Session
import uuid

#En la tabla area solo se pueden realizar las lecturas de la misma.
class AreaService ():
    
    def __init__(self, db: Session): #Se inyecta la sesión de la base de datos al servicio
        self.db = ur(AreaService)
        
    def get_areas (self): #Se llama al metodo get_all del archivo UniversalRepository
        return self.db.get_all(Area)
    
    def get_area_by_id (self, id: uuid.UUID): #Se llama al metodo get_by_id del archivo UniversalRepository
        return self.db.get_by_id(Area, id)