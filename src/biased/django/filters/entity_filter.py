from enum import StrEnum, auto, unique

from django.db.models import Q, Value
from pydantic import ValidationError

from biased.django.filters.input_filter import (
    CommaSeparatedInputFilter,
    parse_int_token,
)
from biased.types import UlidStr
from biased.utils.ulid import validate_ulid_str


@unique
class ValueType(StrEnum):
    none = auto()
    int = auto()
    ulid = auto()
    str = auto()


def _parse_value(value: str) -> tuple[ValueType, int | UlidStr | str]:
    number = parse_int_token(value)
    if number is not None:
        return ValueType.int, number
    try:
        return ValueType.ulid, validate_ulid_str(value)
    except ValidationError:
        pass
    return ValueType.str, value.strip('"')


class EntityFilter(CommaSeparatedInputFilter):
    def int_value_to_filter(self, value: int) -> Q:
        return Q(Value(False))

    def ulid_value_to_filter(self, value: UlidStr) -> Q:
        return Q(Value(False))

    def str_value_to_filter(self, value: str) -> Q:
        return Q(Value(False))

    def value_to_filter(self, value: str) -> Q:
        value_type, parsed_value = _parse_value(value=value)
        if value_type == ValueType.int:
            # Each assert narrows the union: `_parse_value`'s tag fixes the value's type.
            assert isinstance(parsed_value, int)  # nosec B101  # noqa: S101
            return self.int_value_to_filter(value=parsed_value)
        if value_type == ValueType.ulid:
            assert isinstance(parsed_value, str)  # nosec B101  # noqa: S101
            return self.ulid_value_to_filter(value=parsed_value)
        if value_type == ValueType.str:
            assert isinstance(parsed_value, str)  # nosec B101  # noqa: S101
            return self.str_value_to_filter(value=parsed_value)
        raise NotImplementedError(f"{value_type} is not supported")
