from pydantic import TypeAdapter
from ulid import ULID

from biased.types import UlidStr


def build_ulid_str() -> UlidStr:
    return str(ULID())


def validate_ulid_str(value: str) -> UlidStr:
    return TypeAdapter(type=UlidStr).validate_python(value)
