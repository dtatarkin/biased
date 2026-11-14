import json
import reprlib
from collections.abc import Mapping
from typing import Any

from biased.utils.default_json_encoder import DefaultJsonEncoder

# What ``json.dumps`` itself fails on before ``default`` sees anything: keys it
# cannot encode or sort (a tuple key, ``1`` beside ``"b"``), a reference cycle,
# nesting deeper than the interpreter's recursion limit.
_DUMP_ERRORS = (TypeError, ValueError, RecursionError)


def _structlog_fallback(o: Any) -> Any:
    """What structlog's own JSON renderer does with an object it cannot
    encode: the object's ``__structlog__()`` when it defines one, else its
    ``repr``. Reimplemented rather than imported — structlog's version is
    private."""
    to_structlog = getattr(o, "__structlog__", None)
    if not callable(to_structlog):
        return repr(o)
    try:
        return to_structlog()
    except Exception:  # noqa: BLE001 — a broken hook must not lose the line either
        return repr(o)


class StructlogJsonEncoder(DefaultJsonEncoder):
    """``DefaultJsonEncoder`` for log events: a value it rejects falls back to
    structlog's rendering instead of raising.

    Any exception is caught, not only ``TypeError``: encoding a value can
    raise others (a pydantic model whose serializer fails raises a
    ``ValueError``), and an exception while formatting makes ``logging`` drop
    the whole record — a log line must never be lost to one of its fields.
    """

    def default(self, o: Any) -> Any:
        try:
            return super().default(o)
        except Exception:  # noqa: BLE001 — see the class docstring
            return _structlog_fallback(o)


def _json_key(key: object) -> str:
    if isinstance(key, str):
        return key
    if key is None or isinstance(key, int | float):
        # The text ``json`` itself writes for such a key: ``1``, ``true``, ``null``.
        return json.dumps(key)
    return repr(key)


def _with_str_keys(value: Any, path: frozenset[int]) -> Any:
    """``value`` with every dict key a string and every cycle cut, the
    containers ``json`` encodes natively walked, anything else left to the
    encoder."""
    if not isinstance(value, dict | list | tuple):
        return value
    if id(value) in path:
        return "<circular reference>"
    path |= {id(value)}
    if isinstance(value, dict):
        return {_json_key(k): _with_str_keys(v, path) for k, v in value.items()}
    return [_with_str_keys(item, path) for item in value]


def _safe_repr(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return repr(value)
    except Exception:  # noqa: BLE001 — the last resort must not raise
        # Depth- and size-bounded, and survives a ``__repr__`` that raises.
        return reprlib.repr(value)


def _flattened(obj: Any) -> Any:
    if isinstance(obj, Mapping):
        return {_json_key(k): _safe_repr(v) for k, v in obj.items()}
    return _safe_repr(obj)


def structlog_json_serializer(obj: Any, *args: Any, **kwargs: Any) -> str:
    """Render a log event as compact JSON with sorted keys, never raising.

    An event ``json`` cannot dump as it stands is retried with its dict keys
    turned into strings and its cycles cut, and failing that with every
    top-level value rendered by ``repr``.
    """
    # ``JSONRenderer`` passes its own ``default``; dropped, because a
    # ``default`` given to ``json.dumps`` replaces the encoder's ``default``
    # method and would bypass ``StructlogJsonEncoder`` entirely.
    kwargs.pop("default", None)
    kwargs.update(
        {"cls": StructlogJsonEncoder, "sort_keys": True, "separators": (",", ":")}
    )
    try:
        return json.dumps(obj, *args, **kwargs)
    except _DUMP_ERRORS:
        pass
    try:
        return json.dumps(_with_str_keys(obj, frozenset()), *args, **kwargs)
    except _DUMP_ERRORS:
        return json.dumps(_flattened(obj), *args, **kwargs)
