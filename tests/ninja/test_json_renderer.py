import json
from datetime import UTC, datetime
from enum import Enum
from ipaddress import IPv4Address

import pytest
from django.http import HttpRequest
from django.utils.functional import lazy
from ulid import ULID

from biased.ninja.json_renderer import BiasedNinjaJsonEncoder, BiasedNinjaJsonRenderer
from biased.utils.default_json_encoder import DefaultJsonEncoder


class Color(Enum):
    RED = 1


def dumps(value):
    return json.dumps(value, cls=BiasedNinjaJsonEncoder)


@pytest.mark.parametrize(
    "value",
    [
        Color.RED,
        datetime(2026, 1, 1, 12, 0, 0, 123456, tzinfo=UTC),
        ULID(),
        b"abc",
    ],
    ids=["enum", "datetime", "ulid", "bytes"],
)
def test_matches_default_json_encoder(value):
    assert dumps(value) == json.dumps(value, cls=DefaultJsonEncoder)


def test_ninja_only_type_falls_through():
    assert dumps(IPv4Address("10.0.0.1")) == '"10.0.0.1"'


def test_django_only_type_falls_through():
    assert dumps(lazy(lambda: "lazy", str)()) == '"lazy"'


def test_unknown_type_raises_type_error():
    with pytest.raises(TypeError):
        dumps(object())


def test_renderer_uses_the_encoder():
    rendered = BiasedNinjaJsonRenderer().render(
        HttpRequest(), {"color": Color.RED}, response_status=200
    )
    assert rendered == '{"color": 1}'


def test_misspelled_import_path_still_works():
    from biased.ninja import json_renderrer

    assert json_renderrer.BiasedNinjaJsonRenderer is BiasedNinjaJsonRenderer
    assert json_renderrer.BiasedNinjaJsonEncoder is BiasedNinjaJsonEncoder
