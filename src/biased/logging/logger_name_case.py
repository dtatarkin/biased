from collections.abc import Mapping

from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)

# The ``LoggingParams`` field whose keys are logger names.
_LEVELS_FIELD = "levels"


class KeepsLoggerNameCase(BaseSettings):
    """Keep the case of the logger name in a ``<prefix>LEVELS__<logger>``
    variable.

    A case-insensitive settings class folds every variable name to lowercase
    before it is split, and logger names are case-sensitive: without this,
    ``LOG_LEVELS__MyLib=DEBUG`` would set a level on a ``mylib`` logger nobody
    uses, and the override would be lost without an error. The rest of each
    variable name is still read in any case.
    """

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        for source in (env_settings, dotenv_settings):
            # The dotenv source is a subclass of the env one.
            if isinstance(source, EnvSettingsSource) and not source.case_sensitive:
                _reload_keeping_logger_name_case(source)
        return init_settings, env_settings, dotenv_settings, file_secret_settings


def _reload_keeping_logger_name_case(source: EnvSettingsSource) -> None:
    # ``_load_env_vars`` is private to pydantic-settings, and the one place
    # that reads the variables before their names are folded; the tests over
    # mixed-case logger names pin this against an upgrade.
    source.case_sensitive = True
    try:
        verbatim = source._load_env_vars()
    finally:
        source.case_sensitive = False
    head = f"{source.env_prefix}{_LEVELS_FIELD}{source.env_nested_delimiter}"
    source.env_vars = _fold_all_but_logger_names(verbatim, head.lower())


def _fold_all_but_logger_names(
    env_vars: Mapping[str, str | None], head: str
) -> dict[str, str | None]:
    folded: dict[str, str | None] = {}
    for name, value in env_vars.items():
        lowered = name.lower()
        if lowered.startswith(head):
            folded[head + name[len(head) :]] = value
        else:
            folded[lowered] = value
    return folded
