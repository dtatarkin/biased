"""A pydantic model carried as Base64-encoded JSON, e.g. an opaque pagination cursor.

`Base64PydanticModel[T]` validates from:

- a Base64 string of the model's JSON — standard or URL-safe alphabet, padded or
  not, so a value read back from a URL survives either encoding;
- a model instance or a mapping, validated as `T` itself, so code can build the
  field without encoding first.

It serializes to URL-safe Base64 without padding in **both** dump modes, so
`model_dump()` yields the string too: the field is opaque wherever it travels.
The payload is dumped by alias, so it validates back under the model's default
config, and the outer dump's `include`/`exclude`, `exclude_*`, `round_trip`,
`serialize_as_any` and `context` reach the payload.
"""

import base64
import json
from typing import Annotated, Any, TypeVar, cast

from pydantic import (
    BaseModel,
    BeforeValidator,
    GetJsonSchemaHandler,
    SerializationInfo,
    WrapSerializer,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic.main import IncEx
from pydantic_core import CoreSchema

T = TypeVar("T", bound=BaseModel)

_URL_SAFE_TO_STANDARD = str.maketrans("-_", "+/")


def _decode_b64_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    # A ValueError is reported by pydantic as a `value_error` naming the cause;
    # binascii.Error, UnicodeDecodeError and JSONDecodeError are all ValueErrors.
    try:
        padded = value.translate(_URL_SAFE_TO_STANDARD) + "=" * (-len(value) % 4)
        return json.loads(base64.b64decode(padded, validate=True).decode())
    except ValueError as exc:
        msg = f"invalid Base64-encoded JSON: {exc}"
        raise ValueError(msg) from exc


def _encode_b64_json(value: Any, _handler: Any, info: SerializationInfo) -> str:
    if not isinstance(value, BaseModel):
        # Only reachable past validation (model_construct, unvalidated
        # assignment); encoding its repr would emit a value nothing can read.
        msg = f"Base64PydanticModel expects a BaseModel instance, got {type(value).__name__}"
        raise TypeError(msg)
    # pydantic-core types the info's include/exclude more loosely than
    # pydantic's own `IncEx`; they are the same nested sets and dicts.
    payload = value.model_dump_json(
        include=cast("IncEx | None", info.include),
        exclude=cast("IncEx | None", info.exclude),
        by_alias=True,
        exclude_unset=info.exclude_unset,
        exclude_defaults=info.exclude_defaults,
        exclude_none=info.exclude_none,
        round_trip=info.round_trip,
        serialize_as_any=info.serialize_as_any,
        context=info.context,
    )
    return base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")


class _Base64JsonSchema:
    """Describe the field as the string it is on the wire, the model as its content."""

    def __get_pydantic_json_schema__(
        self, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        schema: JsonSchemaValue = {
            "type": "string",
            "contentEncoding": "base64url",
            "contentMediaType": "application/json",
        }
        # In serialization mode the handler answers with the serializer's `str`
        # return type, not the model, so there is no content schema to give.
        if handler.mode == "validation":
            schema["contentSchema"] = handler(core_schema)
        return schema


Base64PydanticModel = Annotated[
    T,
    BeforeValidator(_decode_b64_json),
    WrapSerializer(_encode_b64_json, return_type=str),
    _Base64JsonSchema(),
]
