import json
from datetime import UTC, datetime, time, timedelta

import pytest
from pydantic import AnyUrl, BaseModel, Field, PostgresDsn, field_serializer

from biased.utils.default_json_encoder import DefaultJsonEncoder


def _dumps(value) -> str:
    return json.dumps(value, cls=DefaultJsonEncoder)


def test_time_keeps_microseconds_like_datetime():
    assert _dumps(time(1, 2, 3, 456789)) == '"01:02:03.456789"'
    assert (
        _dumps(datetime(2026, 1, 1, 1, 2, 3, 456789, tzinfo=UTC))
        == '"2026-01-01T01:02:03.456789Z"'
    )


def test_aware_time_is_a_type_error():
    with pytest.raises(TypeError):
        _dumps(time(1, tzinfo=UTC))


def test_negative_timedelta():
    assert _dumps(timedelta(days=-1, seconds=5)) == '"-P0DT23H59M55S"'


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (AnyUrl("http://example.com"), "http://example.com/"),
        (PostgresDsn("postgres://user@h1,h2/db"), "postgres://user@h1,h2/db"),
    ],
)
def test_urls_encode_as_strings(url, expected):
    assert json.loads(_dumps(url)) == expected


class _Model(BaseModel):
    count: int = Field(alias="Count")
    when: datetime

    @field_serializer("when", when_used="json")
    def _serialize_when(self, value: datetime) -> str:
        return "json-only"


def test_model_honours_json_mode_serializers():
    model = _Model(Count=1, when=datetime(2026, 1, 1, tzinfo=UTC))
    assert json.loads(_dumps(model)) == {"count": 1, "when": "json-only"}
