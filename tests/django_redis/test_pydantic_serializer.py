import uuid
from datetime import datetime

import pytest
from pydantic import BaseModel, Field

from biased.django_redis.pydantic_serializer import PydanticSerializer
from biased.utils.time import build_now


class Record(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=build_now)
    count: int = 0
    name: str


@pytest.fixture
def serializer() -> PydanticSerializer:
    return PydanticSerializer({})


class TestPydanticSerializer:
    def test_round_trip_keeps_default_factory_fields(
        self, serializer: PydanticSerializer
    ):
        record = Record(name="a")
        raw = serializer.loads(serializer.dumps(record))
        assert Record.model_validate_json(raw) == record

    def test_loads_returns_raw_bytes(self, serializer: PydanticSerializer):
        raw = serializer.dumps(Record(name="a"))
        assert serializer.loads(raw) is raw

    @pytest.mark.parametrize(
        "value", ["text", None, True, 1.5, {"name": "a"}, [Record(name="a")]]
    )
    def test_dumps_rejects_non_models(
        self, serializer: PydanticSerializer, value: object
    ):
        with pytest.raises(TypeError, match="pydantic models only"):
            serializer.dumps(value)
