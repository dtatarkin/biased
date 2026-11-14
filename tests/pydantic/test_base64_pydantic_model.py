import base64
import json
from datetime import datetime

import pytest
from pydantic import BaseModel, Field, ValidationError
from pydantic_core import PydanticSerializationError

from biased.pydantic.base64_pydantic_model import Base64PydanticModel
from biased.utils.time import build_now


class Payload(BaseModel):
    id: int
    time: datetime


class Model(BaseModel):
    payload: Base64PydanticModel[Payload]


class Aliased(BaseModel):
    user_id: int = Field(alias="userId")


class AliasedModel(BaseModel):
    payload: Base64PydanticModel[Aliased]


class Sparse(BaseModel):
    a: int | None = None
    b: int = 0


class SparseModel(BaseModel):
    payload: Base64PydanticModel[Sparse]


class Text(BaseModel):
    text: str


class TextModel(BaseModel):
    payload: Base64PydanticModel[Text]


def _decode(value: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)))


class TestRoundTrip:
    def test_through_json(self) -> None:
        now = build_now()
        model = Model(payload=Payload(id=42, time=now))

        model2 = Model.model_validate_json(model.model_dump_json())

        assert model2 == model
        assert model2.payload.time == now

    def test_through_python_dump(self) -> None:
        model = Model(payload=Payload(id=42, time=build_now()))

        assert Model.model_validate(model.model_dump()) == model

    def test_with_field_aliases(self) -> None:
        model = AliasedModel(payload=Aliased(userId=1))

        assert AliasedModel.model_validate_json(model.model_dump_json()) == model


class TestSerialization:
    def test_emits_url_safe_unpadded_base64_in_both_modes(self) -> None:
        model = TextModel(payload=Text(text="~~~???"))
        assert set("+/=") <= set(base64.b64encode(b'{"text":"~~~???"}').decode())

        for dumped in (
            model.model_dump()["payload"],
            json.loads(model.model_dump_json())["payload"],
        ):
            assert isinstance(dumped, str)
            assert not set(dumped) & set("+/=")
            assert _decode(dumped) == {"text": "~~~???"}

    def test_honours_outer_exclude_none(self) -> None:
        model = SparseModel(payload=Sparse(a=None, b=1))

        assert _decode(model.model_dump(exclude_none=True)["payload"]) == {"b": 1}

    def test_honours_nested_exclude(self) -> None:
        model = SparseModel(payload=Sparse(a=1, b=2))

        assert _decode(model.model_dump(exclude={"payload": {"b"}})["payload"]) == {
            "a": 1
        }

    def test_refuses_a_value_that_is_not_a_model(self) -> None:
        model = SparseModel.model_construct(payload={"a": 1})

        with pytest.raises(
            PydanticSerializationError, match="expects a BaseModel instance"
        ):
            model.model_dump()


class TestValidation:
    @pytest.mark.parametrize(
        "encode",
        [
            base64.b64encode,
            base64.urlsafe_b64encode,
            lambda raw: base64.b64encode(raw).rstrip(b"="),
        ],
        ids=["standard", "url-safe", "unpadded"],
    )
    def test_accepts_base64_variants(self, encode) -> None:
        value = encode(b'{"a":1,"b":2}').decode()

        assert SparseModel.model_validate({"payload": value}).payload == Sparse(
            a=1, b=2
        )

    def test_accepts_a_mapping(self) -> None:
        assert SparseModel(payload={"a": 3}).payload == Sparse(a=3)

    @pytest.mark.parametrize(
        "value",
        [
            "!!" + base64.b64encode(b'{"a":1}').decode(),
            "abcde",
            "é",
            base64.b64encode(b"\xff").decode(),
            base64.b64encode(b"{not json").decode(),
        ],
        ids=["non-alphabet", "bad-length", "non-ascii", "non-utf8", "non-json"],
    )
    def test_rejects_malformed_input_naming_the_cause(self, value: str) -> None:
        with pytest.raises(ValidationError, match="invalid Base64-encoded JSON"):
            SparseModel.model_validate({"payload": value})

    def test_rejects_json_that_is_not_an_object(self) -> None:
        with pytest.raises(
            ValidationError, match="valid dictionary or instance of Sparse"
        ):
            SparseModel.model_validate({"payload": base64.b64encode(b"42").decode()})


class TestJsonSchema:
    def test_describes_a_string_carrying_the_model(self) -> None:
        schema = SparseModel.model_json_schema()["properties"]["payload"]

        assert schema["type"] == "string"
        assert schema["contentEncoding"] == "base64url"
        assert schema["contentSchema"] == {"$ref": "#/$defs/Sparse"}

    def test_serialization_schema_is_a_string(self) -> None:
        schema = SparseModel.model_json_schema(mode="serialization")["properties"][
            "payload"
        ]

        assert schema["type"] == "string"
        assert "contentSchema" not in schema
