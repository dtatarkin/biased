from pydantic import TypeAdapter
from ulid import ULID

from biased.types import UlidStr

_ULID_STR_ADAPTER: TypeAdapter[UlidStr] = TypeAdapter(UlidStr)


def build_ulid_str() -> UlidStr:
    return str(ULID())


def validate_ulid_str(value: str) -> UlidStr:
    return _ULID_STR_ADAPTER.validate_python(value)
