import json
from typing import Any

from biased.utils.default_json_encoder import DefaultJsonEncoder


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


def structlog_json_serializer(*args: Any, **kwargs: Any) -> str:
    # ``JSONRenderer`` passes its own ``default``; dropped, because a
    # ``default`` given to ``json.dumps`` replaces the encoder's ``default``
    # method and would bypass ``StructlogJsonEncoder`` entirely.
    kwargs.pop("default", None)
    kwargs.update(
        {"cls": StructlogJsonEncoder, "sort_keys": True, "separators": (",", ":")}
    )
    return json.dumps(*args, **kwargs)
