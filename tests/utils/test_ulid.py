import pytest
from pydantic import TypeAdapter, ValidationError

from biased.consts import ULID_PATTERN
from biased.types import UlidStr
from biased.utils.ulid import build_ulid_str, validate_ulid_str


def test_built_ulid_validates():
    value = build_ulid_str()
    assert validate_ulid_str(value) == value


def test_invalid_ulid_is_rejected():
    with pytest.raises(ValidationError):
        validate_ulid_str("not-a-ulid")


def test_lower_case_ulid_validates_to_upper_case():
    value = build_ulid_str()
    assert validate_ulid_str(f" {value.lower()} ") == value


def test_ulid_json_schema_pattern_is_case_sensitive_ulid_pattern():
    assert TypeAdapter(UlidStr).json_schema()["pattern"] == ULID_PATTERN
