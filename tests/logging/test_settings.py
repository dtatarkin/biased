import logging
from pathlib import Path

import pytest

from biased.dtos.logging_params import LogFormatter
from biased.logging.settings import LoggingConfig, LoggingSettings
from biased.settings.env_file_paths import EnvFilePaths


class TestLoggingConfig:
    def test_defaults_to_json_at_info(self) -> None:
        config = LoggingConfig(_env_file=None)

        assert config.formatter is LogFormatter.json
        assert config.level == logging.INFO
        assert config.levels == {}

    def test_colors_are_left_unset_by_default(self) -> None:
        # Unset is a state of its own — the terminal decides — and not a
        # spelling of "off".
        assert LoggingConfig(_env_file=None).colors is None

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

    def test_logger_names_keep_their_case(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Logger names are case-sensitive: a folded name would address a
        # logger nobody uses.
        monkeypatch.setenv("LOG_LEVELS__MyLib.Sub", "DEBUG")
        # The prefix and field name are still read in any case.
        monkeypatch.setenv("log_levels__Other.Lib", "ERROR")

        config = LoggingConfig(_env_file=None)

        assert config.levels == {"MyLib.Sub": logging.DEBUG, "Other.Lib": logging.ERROR}

    def test_logger_names_keep_their_case_in_an_env_file(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("LOG_LEVELS__MyLib.Sub=DEBUG\nlog_level=warning\n")

        config = LoggingConfig(_env_file=env_file)

        assert config.levels == {"MyLib.Sub": logging.DEBUG}
        assert config.level == logging.WARNING


class TestLoggingSettings:
    def test_logger_names_keep_their_case(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("LOG_LEVELS__Other.Lib=ERROR\n")
        monkeypatch.setenv("LOG_LEVELS__MyLib.Sub", "DEBUG")

        settings = LoggingSettings(env_file_paths=EnvFilePaths(env_file))

        assert settings.levels == {
            "MyLib.Sub": logging.DEBUG,
            "Other.Lib": logging.ERROR,
        }
