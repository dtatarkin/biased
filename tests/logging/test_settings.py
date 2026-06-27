import logging

import pytest

from biased.dtos.logging import LogFormatter
from biased.logging.settings import LoggingConfig

_LOG_ENV_KEYS = ("LOG_FORMATTER", "LOG_LEVEL", "LOG_COLORS", "LOG_LEVELS__a.b")


class TestLoggingConfig:
    @pytest.fixture(autouse=True)
    def _clear_log_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Isolate from any LOG_* the surrounding environment happens to set so a
        # stray export cannot mask the defaults under test.
        for key in _LOG_ENV_KEYS:
            monkeypatch.delenv(key, raising=False)

    def test_defaults_to_json_at_info(self) -> None:
        config = LoggingConfig(_env_file=None)

        assert config.formatter is LogFormatter.json
        assert config.level == logging.INFO
        assert config.levels == {}

    def test_binds_log_prefixed_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_FORMATTER", "human")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("LOG_LEVELS__a.b", "WARNING")

        config = LoggingConfig(_env_file=None)

        assert config.formatter is LogFormatter.human
        assert config.level == logging.DEBUG
        # The nested `LOG_LEVELS__<logger>` map binds a per-logger override, and
        # level names coerce to their stdlib integer values.
        assert config.levels == {"a.b": logging.WARNING}
