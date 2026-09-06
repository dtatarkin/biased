import logging
from collections.abc import Iterator

import pytest

_LOG_ENV_KEYS = (
    "LOG_FORMATTER",
    "LOG_LEVEL",
    "LOG_COLORS",
    "LOG_LEVELS__a.b",
    "LOG_LEVELS__tests.biased.logging",
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
