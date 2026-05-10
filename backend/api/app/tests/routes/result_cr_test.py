import uuid
from datetime import date
#Individual pass
from app.dbmodels.ranks import Rank
from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.workers import Worker
from app.dbmodels.surveys import Surveys
from app.dbmodels.result import Result

from app.schemas.auth_scheme import CurrentUserData
from app.main import app
from app.deps.auth_deps import get_current_user
from app.tests.conftest import rrhh_user


class TestResultEndpoints:

    def test_get_results_rrhh_success(self, client, db, rrhh_user):

        def override_get_current_user():
            return rrhh_user

        app.dependency_overrides[get_current_user] = override_get_current_user

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

        db.add(rank)
        db.add(area)
        db.commit()  

        db.add(group) 
        db.commit()  

        db.add(worker) 
        db.commit() 

        db.add(survey) 
        db.commit() 

        db.add(result) 
        db.commit()

        response = client.get("/results/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1

        app.dependency_overrides.clear()

    