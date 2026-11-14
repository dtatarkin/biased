from datetime import UTC, datetime

from pydantic import BaseModel, field_serializer

from biased.django.models.pydantic_model_field import PydanticModelField


class _Stamped(BaseModel):
    when: datetime

    @field_serializer("when", when_used="json")
    def _serialize_when(self, value: datetime) -> str:
        return "json-only"


def test_prep_value_dumps_in_json_mode():
    field = PydanticModelField(_Stamped)
    assert field.get_prep_value(_Stamped(when=datetime(2026, 1, 1, tzinfo=UTC))) == {
        "when": "json-only"
    }
