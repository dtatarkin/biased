from collections.abc import Callable
from typing import Any

_MISSING = object()


def _is_own_miss(error: AttributeError, obj: Any, name: str) -> bool:
    # An error that names another object or attribute was raised inside the lookup,
    # e.g. by a property, and is a bug to surface. One naming nothing — a custom
    # ``__getattr__``, Django's ``RelatedObjectDoesNotExist`` — counts as a miss.
    if error.obj is None and error.name is None:
        return True
    return error.obj is obj and error.name == name


def _resolve(obj: Any, path: str) -> Any:
    for name in path.split("."):
        try:
            obj = getattr(obj, name)
        except AttributeError as e:
            if _is_own_miss(e, obj, name):
                return _MISSING
            raise
    return obj


def attrgetter_default(*attrs: str, default: Any = None) -> Callable[[Any], Any]:
    """Like ``operator.attrgetter``, returning ``default`` when an attribute is missing."""

    def wrapper(obj: Any) -> Any:
        values = []
        for attr in attrs:
            value = _resolve(obj, attr)
            if value is _MISSING:
                return default
            values.append(value)
        return values[0] if len(values) == 1 else tuple(values)

    return wrapper
