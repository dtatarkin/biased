from pydantic import HttpUrl, SecretStr
from pydantic_settings import SettingsConfigDict

from biased.dtos.base import BaseDto
from biased.settings.env_file_paths import EnvFilePathsSettings


class TemporalClientParams(BaseDto):
    target_host: str
    namespace: str = "default"
    api_key: SecretStr | None = None
    identity: str | None = None
    lazy: bool = True


class TemporalClientSettings(EnvFilePathsSettings, TemporalClientParams):
    model_config = SettingsConfigDict(extra="ignore", env_prefix="TEMPORAL_CLIENT_")


class TemporalParams(BaseDto):
    ui_base_url: HttpUrl


class TemporalSettings(EnvFilePathsSettings, TemporalParams):
    model_config = SettingsConfigDict(extra="ignore", env_prefix="TEMPORAL_")
