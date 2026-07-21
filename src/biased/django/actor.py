from collections.abc import Iterator
from contextlib import contextmanager
from typing import cast

from asgiref.local import Local
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser

_storage = Local()


def get_current_actor() -> AbstractBaseUser | None:
    """Return the authenticated user bound to the current context, or None (= the system).

    Resolves lazy user objects (e.g. `request.user`) on access — callers should only
    invoke this at the moment attribution is actually needed.
    """
    user = getattr(_storage, "actor", None)
    if user is None or not user.is_authenticated:
        return None
    return cast(AbstractBaseUser, user)


@contextmanager
def actor(user: AbstractBaseUser | AnonymousUser | None) -> Iterator[None]:
    """Bind `user` as the current actor for the duration of the block.

    Nested blocks apply innermost-wins; the previous binding is restored on exit,
    including on exception. `actor(None)` forces system attribution.
    """
    had_previous = hasattr(_storage, "actor")
    previous = getattr(_storage, "actor", None)
    _storage.actor = user
    try:
        yield
    finally:
        if had_previous:
            _storage.actor = previous
        else:
            del _storage.actor
