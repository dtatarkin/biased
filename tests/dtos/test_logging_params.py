import logging

import pytest
from pydantic import ValidationError

from biased.dtos.logging_params import LoggingParams
from biased.logging.settings import LoggingConfig


def test_is_hashable() -> None:
    params = LoggingParams(levels={"a.b": "WARNING"})

    assert hash(params) == hash(LoggingParams(levels={"a.b": logging.WARNING}))


def test_levels_cannot_be_mutated() -> None:
    with pytest.raises(TypeError):
        LoggingParams().levels["a.b"] = logging.DEBUG  # ty: ignore[invalid-assignment]


def test_rejects_an_unknown_field() -> None:
    with pytest.raises(ValidationError):
        LoggingParams(colour=True)  # ty: ignore[unknown-argument]


def test_settings_still_ignore_unknown_fields() -> None:
    # One environment carries knobs for several settings classes.
    assert LoggingConfig(_env_file=None, colour=True).colors is None  # ty: ignore[unknown-argument]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("debug", logging.DEBUG),
        (" info ", logging.INFO),
        ("10", 10),
        (5, 5),
        (0, logging.NOTSET),
    ],
)
def test_accepts_a_level(value: int | str, expected: int) -> None:
    assert LoggingParams(level=value).level == expected


@pytest.mark.parametrize("value", ["verbose", "", True, False, -5, 1.5])
def test_rejects_an_invalid_level(value: object) -> None:
    with pytest.raises(ValidationError):
        LoggingParams(level=value)  # ty: ignore[invalid-argument-type]
