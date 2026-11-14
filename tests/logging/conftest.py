import io
import logging
import sys
from collections.abc import Callable, Iterator

import pytest

_LOG_ENV_KEYS = (
    "LOG_FORMATTER",
    "LOG_LEVEL",
    "LOG_COLORS",
    "LOG_LEVELS__a.b",
    "LOG_LEVELS__tests.biased.logging",
    "LOG_LEVELS__MyLib.Sub",
    "log_levels__Other.Lib",
)


@pytest.fixture(autouse=True)
def _clear_log_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Isolate from any LOG_* the surrounding environment happens to set so a
    # stray export cannot mask the defaults under test.
    for key in _LOG_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def pristine_root_logger() -> Iterator[logging.Logger]:
    """The root logger, restored to its prior handlers and level afterwards:
    ``dictConfig`` is process-wide, and a handler bound to a captured stream
    must not outlive the test that captured it."""
    root = logging.getLogger()
    handlers, level = list(root.handlers), root.level
    yield root
    for handler in list(root.handlers):
        root.removeHandler(handler)
    for handler in handlers:
        root.addHandler(handler)
    root.setLevel(level)


class _Stderr(io.StringIO):
    """Stands in for standard error: keeps what is written to it, and is a
    terminal or not as it was told to be."""

    def __init__(self, *, terminal: bool) -> None:
        super().__init__()
        self._terminal = terminal

    def isatty(self) -> bool:
        return self._terminal


@pytest.fixture
def stderr_builder(monkeypatch: pytest.MonkeyPatch) -> Callable[..., io.StringIO]:
    """Puts a stream in place of ``sys.stderr`` for the rest of the test — a
    terminal or not, as asked — and returns it to be read back. Call it before
    configuring: that is when ``sys.stderr`` is looked at, both to decide on
    color and to bind the handler."""

    def build(*, terminal: bool) -> io.StringIO:
        stream = _Stderr(terminal=terminal)
        monkeypatch.setattr(sys, "stderr", stream)
        return stream

    return build
