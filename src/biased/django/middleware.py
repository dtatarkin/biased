from collections.abc import Callable

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.http import HttpRequest, HttpResponse

from biased.django.actor import actor


class CurrentActorMiddleware:
    """Binds `request.user` as the current actor for the duration of each request.

    Must be placed after `django.contrib.auth.middleware.AuthenticationMiddleware`.
    The lazy `request.user` is stored unresolved — no session/user query happens
    unless something actually reads the actor during the request.

    Both sync- and async-capable: a sync-only middleware would split the chain's
    async region and force an extra async_to_sync boundary (which can deadlock
    under a sync entry point such as the test client).
    """

    sync_capable = True
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self._is_async = iscoroutinefunction(get_response)
        if self._is_async:
            markcoroutinefunction(self)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._is_async:
            return self.__acall__(request)  # type: ignore[return-value]
        with actor(request.user):
            return self.get_response(request)

    async def __acall__(self, request: HttpRequest) -> HttpResponse:
        with actor(request.user):
            return await self.get_response(request)  # type: ignore[misc]
