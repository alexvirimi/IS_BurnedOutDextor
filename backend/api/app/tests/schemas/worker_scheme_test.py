import uuid

from app.schemas.workers_scheme import (
    WorkerCreate,
    WorkerResponse,
    WorkerDetailResponse
)


class TestWorkerSchemas:

    def test_worker_create(self):

        worker = WorkerCreate(
            name="Mario",
            last_names="Julio",
            age=20,
            gender="M",
            id_group=uuid.uuid4(),
            id_rank=uuid.uuid4()
        )

        assert worker.name == "Mario"
        assert worker.age == 20

    def test_worker_response(self):

        worker = WorkerResponse(
            id=uuid.uuid4(),
            name="Ana",
            last_names="Meza",
            age=21,
            gender="F",
            flag=False,
            id_group=uuid.uuid4(),
            id_rank=uuid.uuid4()
        )

        assert worker.flag is False
        assert worker.gender == "F"

    def test_worker_detail_response(self):

        worker = WorkerDetailResponse(
            id=uuid.uuid4(),
            name="Carlos",
            last_names="Perez",
            age=30,
            gender="M",
            flag=True,
            id_group=uuid.uuid4(),
            id_rank=uuid.uuid4(),
            group="Backend",
            rank="Lider"
        )

        assert worker.flag is True
        assert worker.group == "Backend"
        assert worker.rank == "Lider"

    def test_worker_detail_response_optional_fields(self):

        worker = WorkerDetailResponse(
            id=uuid.uuid4(),
            name="Luis",
            last_names="Gonzalez",
            age=28,
            gender="M",
            flag=False
        )

        assert worker.group is None
        assert worker.rank is None