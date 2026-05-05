"""
Este módulo implementa la lógica de servicios para autenticación y gestión de usuarios autenticados.
Proporciona métodos para registrar nuevos usuarios (crear registros AuthUser), validar credenciales
durante el login y recuperar información del usuario autenticado. El servicio actúa como intermediario
entre las rutas de autenticación y el repositorio universal, encapsulando toda la lógica de negocio
relacionada con autenticación. Todos los métodos operan directamente sobre la base de datos a través
de la sesión SQLAlchemy proporcionada.
"""

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels.auth_user import AuthUser
from app.dbmodels.workers import Worker
from sqlalchemy.orm import Session 
from sqlalchemy import and_
from uuid import UUID

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
        """
        Registra un nuevo usuario autenticado.
        Crea un nuevo registro en la tabla auth_user con el worker_id, username y password.
        El password se almacena en texto plano como se requirió.
        """
        return self.repo.create(data)
    
    def login_user(self, username: str, password: str):
        """
        Valida las credenciales de un usuario durante el login.
        Busca un usuario con el username exacto y verifica si el password coincide (comparación simple).
        Retorna el registro AuthUser si las credenciales son válidas, None en caso contrario.
        """
        # Consulta la base de datos para encontrar el usuario por username
        auth_user = self.db.query(AuthUser).filter(AuthUser.username == username).first()
        
        # Si el usuario no existe, retorna None
        if not auth_user:
            return None
        
        # Valida el password (comparación de texto plano)
        if auth_user.password != password:
            return None
        
        # Retorna el usuario si las credenciales son correctas
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
