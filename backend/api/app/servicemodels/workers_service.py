# Este módulo implementa la lógica de servicios para gestionar trabajadores.
# Proporciona métodos para crear, consultar y actualizar trabajadores. El servicio actúa como intermediario
# entre las rutas de trabajadores y el repositorio universal, encapsulando toda la lógica de negocio
# relacionada con la gestión de trabajadores. Los métodos aquí incluyen operaciones básicas de CRUD
# y operaciones específicas como la actualización del campo flag (bandera de control).

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Worker
from sqlalchemy.orm import Session 
from uuid import UUID

# C + R básico
class WorkerService:
    def __init__(self, db: Session) -> None:
        # Inicializa el repositorio universal para la tabla Worker
        self.repo = ur(Worker, db)
        # Almacena la sesión para operaciones complejas
        self.db = db
    
    def get_workers(self):
        # Consigue todos los trabajadores
        return self.repo.get_all()
    
    def get_worker(self, id: UUID):
        # Busca la información básica de un trabajador dado su UUID
        return self.repo.get_by_id(id)
    
    def create_worker(self, data: dict):
        # Crea un trabajador con su información básica dado un diccionario
        return self.repo.create(data)
    
    def update_worker_flag(self, worker_id: UUID, flag: bool):
        # Actualiza el campo flag (bandera) de un trabajador.
        # Este método es utilizado por líderes para marcar trabajadores que necesitan atención.
        worker = self.get_worker(worker_id)
        if not worker:
            return None
        
        # Actualiza el flag
        worker.flag = flag
        self.db.commit()
        self.db.refresh(worker)
        
        return worker
    
    def get_workers_by_group(self, group_id: UUID):
        # Obtiene todos los trabajadores de un grupo específico.
        # Utilizado por líderes para gestionar su equipo.
        return self.db.query(Worker).filter(Worker.id_group == group_id).all()