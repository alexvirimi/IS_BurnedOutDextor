# Módulo de servicios para autenticación y gestión de usuarios autenticados.
# Proporciona métodos para registrar nuevos usuarios, validar credenciales durante login
# y recuperar información del usuario autenticado.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels.auth_user import AuthUser
from app.dbmodels.workers import Worker

from sqlalchemy.orm import Session

from uuid import UUID

import bcrypt


class AuthUserService:

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
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        return self.repo.create(data)

    def login_user(self, username: str, password: str):

        auth_user = self.db.query(AuthUser).filter(
            AuthUser.username == username
        ).first()

        if not auth_user:
            return None

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            auth_user.password.encode("utf-8")
        ):
            return None

        return auth_user

    def get_auth_user_by_id(self, auth_user_id: UUID):

        return self.repo.get_by_id(auth_user_id)

    def get_auth_user_with_worker_info(self, auth_user_id: UUID):

        # Consulta compleja que une AuthUser y Worker
        result = self.db.query(
            AuthUser.worker_id,
            AuthUser.username,
            Worker.id_group
        ).join(
            Worker,
            AuthUser.worker_id == Worker.id
        ).filter(
            AuthUser.id == auth_user_id
        ).first()

        if not result:
            return None

        # Obtiene la información del rango
        worker = self.db.query(Worker).filter(
            Worker.id == result.worker_id
        ).first()

        if not worker or not worker.rank:
            return None

        # Payload final del JWT
        return {
            "worker_id": result.worker_id,
            "username": result.username,
            "rank_level": worker.rank.level,
            "rank_name": worker.rank.rank_name,
            "id_group": result.id_group
        }

    def username_exists(self, username: str) -> bool:

        return self.db.query(AuthUser).filter(
            AuthUser.username == username
        ).first() is not None