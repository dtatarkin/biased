from collections.abc import Iterable, Iterator, Mapping
from typing import Any, get_args

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class FrozenMap[K, V](Mapping[K, V]):
    """An immutable, hashable mapping that validates and serializes as a dict.

    The mapping a frozen pydantic model can hold: a ``dict`` field leaves the
    model mutable through the dict and makes it unhashable.
    """

    __slots__ = ("_data", "_hash")

    def __init__(self, data: Mapping[K, V] | Iterable[tuple[K, V]] = ()) -> None:
        self._data: dict[K, V] = dict(data)
        self._hash: int | None = None

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self._data.items()))
        return self._hash

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._data!r})"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        key_type, value_type = get_args(source) or (Any, Any)
        dict_schema = core_schema.dict_schema(
            handler.generate_schema(key_type), handler.generate_schema(value_type)
        )
        return core_schema.no_info_after_validator_function(
            cls,
            dict_schema,
            serialization=core_schema.wrap_serializer_function_ser_schema(
                lambda value, serialize: serialize(dict(value)),
                schema=dict_schema,
            ),
        )
