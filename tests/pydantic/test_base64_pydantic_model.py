from datetime import datetime

from biased.pydantic.base64_pydantic_model import Base64PydanticModel
from biased.utils.time import build_now
from pydantic import BaseModel


class Payload(BaseModel):
    id: int
    time: datetime


class Model(BaseModel):
    payload: Base64PydanticModel[Payload]


def test_base64_pydantic_model():
    now = build_now()
    payload = Payload(id=42, time=now)
    model = Model(payload=payload)
    json_str = model.model_dump_json()
    model2 = Model.model_validate_json(json_str)
    assert model2 == model
    assert model2.payload.time == now
