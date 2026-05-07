import uuid
from datetime import date
#fail
from app.dbmodels.ranks import Rank
from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.workers import Worker
from app.dbmodels.surveys import Surveys
from app.dbmodels.result import Result

from app.schemas.auth_scheme import CurrentUserData
from app.main import app
from app.deps.auth_deps import get_current_user


class TestResultEndpoints:

    def test_get_results_rrhh_success(self, client, db, rrhh_user):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="rrhh",
            level=3
        )

        area = Area(
            id=uuid.uuid4(),
            name="TI"
        )

        group = Group(
            id=uuid.uuid4(),
            name="Backend",
            id_area=area.id,
            id_leader=None
        )

        worker = Worker(
            id=uuid.uuid4(),
            name="Mario",
            last_names="Julio",
            age=20,
            gender="M",
            id_group=group.id,
            id_rank=rank.id,
            flag=False
        )

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        result = Result(
            id=uuid.uuid4(),
            burnout_score="medium",
            id_worker=worker.id,
            id_group=group.id,
            id_area=area.id,
            id_survey=survey.id,
            generation_date=date.today()
        )

        db.add_all([rank, area, group, worker, survey, result])
        db.commit()

        response = client.get("/results/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1

    def test_get_result_by_id_success(self, client, db):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="comun",
            level=1
        )

        area = Area(
            id=uuid.uuid4(),
            name="QA"
        )

        group = Group(
            id=uuid.uuid4(),
            name="QA Team",
            id_area=area.id,
            id_leader=None
        )

        worker = Worker(
            id=uuid.uuid4(),
            name="Ana",
            last_names="Meza",
            age=24,
            gender="F",
            id_group=group.id,
            id_rank=rank.id,
            flag=False
        )

        survey = Surveys(
            id=uuid.uuid4(),
            name="Stress",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        result = Result(
            id=uuid.uuid4(),
            burnout_score="low",
            id_worker=worker.id,
            id_group=group.id,
            id_area=area.id,
            id_survey=survey.id,
            generation_date=date.today()
        )

        db.add_all([rank, area, group, worker, survey, result])
        db.commit()

        def override_get_current_user():
            return CurrentUserData(
                auth_user_id=uuid.uuid4(),
                worker_id=worker.id,
                username="ana",
                rank_level=1,
                rank_name="comun",
                id_group=group.id
            )

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = client.get(f"/results/{result.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(result.id)

        app.dependency_overrides.clear()

    def test_get_result_not_found(self, client, rrhh_user):

        fake_id = uuid.uuid4()

        response = client.get(f"/results/{fake_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Resultado no encontrado"

    def test_create_result_success(self, client, db):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="lider",
            level=2
        )

        area = Area(
            id=uuid.uuid4(),
            name="DevOps"
        )

        group = Group(
            id=uuid.uuid4(),
            name="DevOps Team",
            id_area=area.id,
            id_leader=None
        )

        worker = Worker(
            id=uuid.uuid4(),
            name="Carlos",
            last_names="Perez",
            age=30,
            gender="M",
            id_group=group.id,
            id_rank=rank.id,
            flag=False
        )

        survey = Surveys(
            id=uuid.uuid4(),
            name="Burnout",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        db.add_all([rank, area, group, worker, survey])
        db.commit()

        def override_get_current_user():
            return CurrentUserData(
                auth_user_id=uuid.uuid4(),
                worker_id=worker.id,
                username="carlos",
                rank_level=2,
                rank_name="lider",
                id_group=group.id
            )

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = client.post(
            "/results/",
            data={
                "id_worker": str(worker.id),
                "id_group": str(group.id),
                "id_area": str(area.id),
                "id_survey": str(survey.id),
                "burnout_score": "high"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["burnout_score"] == "high"

        app.dependency_overrides.clear()