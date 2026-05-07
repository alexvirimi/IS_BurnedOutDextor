import uuid
#individual pass
from app.dbmodels.ranks import Rank


class TestRankEndpoints:

    def test_get_ranks_success(self, client, db):

        rank1 = Rank(
            id=uuid.uuid4(),
            rank_name="comun",
            level=1
        )

        rank2 = Rank(
            id=uuid.uuid4(),
            rank_name="lider",
            level=2
        )

        db.add_all([rank1, rank2])
        db.commit()

        response = client.get("/rank/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2

    def test_get_rank_by_id_success(self, client, db):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="rrhh",
            level=3
        )

        db.add(rank)
        db.commit()

        response = client.get(f"/rank/{rank.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(rank.id)
        assert data["rank_name"] == "rrhh"
        assert data["level"] == 3

    def test_get_rank_not_found(self, client):

        fake_id = uuid.uuid4()

        response = client.get(f"/rank/{fake_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Rango no encontrado"

    def test_create_rank_success(self, client, rrhh_user):

        response = client.post(
            "/rank/",
            data={
                "rank_name": "lider",
                "level": 2
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["rank_name"] == "lider"
        assert data["level"] == 2