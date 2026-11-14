from typing import Any

from injector import inject
from pydantic import ConfigDict, RootModel
from pydantic_settings import BaseSettings
from pydantic_settings.sources import DotenvType


class EnvFilePaths(RootModel[DotenvType | None]):
    """The env file(s) an :class:`EnvFilePathsSettings` reads, bound in the
    injector; ``None`` reads none, overriding any ``env_file`` in the
    subclass's ``model_config``."""

    model_config = ConfigDict(frozen=True)


class EnvFilePathsSettings(BaseSettings):
    @inject
    def __init__(self, env_file_paths: EnvFilePaths, **kwargs: Any) -> None:
        super().__init__(_env_file=env_file_paths.root, **kwargs)
