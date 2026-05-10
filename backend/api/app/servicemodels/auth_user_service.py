# Módulo de servicios para autenticación y gestión de usuarios autenticados.
# Proporciona métodos para registrar nuevos usuarios, validar credenciales durante login
# y recuperar información del usuario autenticado.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels.auth_user import AuthUser
from app.dbmodels.workers import Worker
from sqlalchemy.orm import Session 
from sqlalchemy import and_
from uuid import UUID
import bcrypt

class AuthUserService:
    """
    Servicio para gestionar usuarios autenticados y operaciones de autenticación.
    Utiliza el repositorio universal para operaciones básicas de CRUD.
    """
    
    def __init__(self, db: Session) -> None:
        # Inicializa el repositorio universal para la tabla AuthUser
        self.repo = ur(AuthUser, db)
        # Almacena la sesión para consultas más complejas
        self.db = db
    
    def register_user(self, data: dict):
        # Hash before storing — never store raw password
        raw_password = data.pop("password")
        data["password"] = bcrypt.hashpw(
            raw_password.encode("utf-8"),
            bcrypt.gensalt(rounds=12)  # 12 rounds is the production-safe minimum
        ).decode("utf-8")
        return self.repo.create(data)

    def login_user(self, username: str, password: str):
        auth_user = self.db.query(AuthUser).filter(
            AuthUser.username == username
        ).first()
        if not auth_user:
            # Always run the check to prevent timing attacks
            bcrypt.checkpw(b"dummy", b"$2b$12$dummy_hash_to_waste_time_xxxxxxxxx")
            return None
        if not bcrypt.checkpw(password.encode("utf-8"), auth_user.password.encode("utf-8")):
            return None
        return auth_user
    
    def get_auth_user_by_id(self, auth_user_id: UUID):
        """
        Obtiene un usuario autenticado por su ID.
        Utiliza el repositorio para buscar en la tabla auth_user.
        """
        return self.repo.get_by_id(auth_user_id)
    
    def get_auth_user_with_worker_info(self, auth_user_id: UUID):
        """
        Obtiene la información completa de un usuario autenticado incluyendo datos del trabajador y su rango.
        Realiza un JOIN con las tablas Worker y Rank para obtener toda la información necesaria.
        Retorna un diccionario con auth_user_id, worker_id, username, rank_level, rank_name e id_group.
        """
        # Consulta compleja que une AuthUser, Worker y Rank
        result = self.db.query(
            AuthUser.id.label('auth_user_id'),
            AuthUser.worker_id,
            AuthUser.username,
            Worker.id_rank,
            Worker.id_group
        ).join(Worker, AuthUser.worker_id == Worker.id).filter(
            AuthUser.id == auth_user_id
        ).first()
        
        if not result:
            return None
        
        # Obtiene la información del rango
        worker = self.db.query(Worker).filter(Worker.id == result.worker_id).first()
        if not worker or not worker.rank:
            return None
        
        # Retorna un diccionario con toda la información
        return {
            'auth_user_id': result.auth_user_id,
            'worker_id': result.worker_id,
            'username': result.username,
            'rank_level': worker.rank.level,
            'rank_name': worker.rank.rank_name,
            'id_group': result.id_group
        }
    
    def username_exists(self, username: str) -> bool:
        """
        Verifica si un username ya existe en la base de datos.
        Realiza una búsqueda rápida para evitar registros duplicados.
        """
        return self.db.query(AuthUser).filter(AuthUser.username == username).first() is not None
