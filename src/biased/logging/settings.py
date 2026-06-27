from pydantic_settings import BaseSettings, SettingsConfigDict

from biased.dtos.env_file_paths import EnvFilePathsSettings
from biased.dtos.logging import LoggingParams


class LoggingConfig(LoggingParams, BaseSettings):
    """Bind the logging parameters to ``LOG_``-prefixed environment variables.

    A dependency-injection-free ``BaseSettings`` that any process — including a
    web framework's settings module — can construct directly, with no injector
    container and no externally supplied env-file paths. It inherits the
    ``LoggingParams`` fields (root ``level``, ``formatter``, per-logger
    ``levels`` overrides, console ``colors``) and reads them from the
    environment under the neutral ``LOG_`` prefix, e.g. ``LOG_LEVEL=DEBUG`` or
    ``LOG_FORMATTER=human``. The nested per-logger ``levels`` map uses a ``__``
    delimiter (``LOG_LEVELS__some.logger=WARNING``). A ``.env`` file is read when
    present in the working directory; unknown ``LOG_``-prefixed keys are ignored
    so a single environment may carry knobs for several settings classes.
    """

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


class LoggingSettings(LoggingParams, EnvFilePathsSettings):
    """Bind the logging parameters with env-file paths supplied via a container.

    The dependency-injection counterpart to :class:`LoggingConfig`: it composes
    the same ``LoggingParams`` over :class:`EnvFilePathsSettings`, so the
    env-file path(s) it reads are provided by an injector container rather than
    hard-coded. Prefer :class:`LoggingConfig` in a plain settings module; reach
    for this when the env-file location is itself resolved through dependency
    injection. Both classes share the ``LOG_`` prefix and the same
    ``LoggingParams`` fields, so the renderer configuration stays single-sourced.
    """

    model_config = SettingsConfigDict(
        extra="ignore", env_prefix="LOG_", env_nested_delimiter="__"
    )
