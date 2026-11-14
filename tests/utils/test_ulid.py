import pytest
from pydantic import ValidationError

from biased.utils.ulid import build_ulid_str, validate_ulid_str


def test_built_ulid_validates():
    value = build_ulid_str()
    assert validate_ulid_str(value) == value


def test_invalid_ulid_is_rejected():
    with pytest.raises(ValidationError):
        validate_ulid_str("not-a-ulid")
