import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from biased.pydantic.frozen_map import FrozenMap


class Model(BaseModel):
    model_config = ConfigDict(frozen=True)

    counts: FrozenMap[str, int] = FrozenMap()


def test_validates_a_dict_into_a_frozen_map() -> None:
    model = Model(counts={"a": "1"})

    assert isinstance(model.counts, FrozenMap)
    assert model.counts == {"a": 1}


def test_rejects_invalid_values() -> None:
    with pytest.raises(ValidationError):
        Model(counts={"a": "one"})


def test_cannot_be_mutated() -> None:
    counts = Model(counts={"a": 1}).counts

    with pytest.raises(TypeError):
        counts["b"] = 2  # ty: ignore[invalid-assignment]


def test_makes_a_frozen_model_hashable() -> None:
    assert hash(Model(counts={"a": 1})) == hash(Model(counts={"a": 1}))


def test_round_trips_through_json_without_warnings(
    recwarn: pytest.WarningsRecorder,
) -> None:
    model = Model(counts={"a": 1})

    assert model.model_dump() == {"counts": {"a": 1}}
    assert Model.model_validate_json(model.model_dump_json()) == model
    assert Model.model_json_schema()["properties"]["counts"]["default"] == {}
    assert not recwarn.list
