from pathlib import Path

import pytest
from injector import Injector
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from biased.settings.env_file_paths import EnvFilePaths, EnvFilePathsSettings


class _Settings(EnvFilePathsSettings):
    model_config = SettingsConfigDict(env_prefix="TEST_EFP_")

    value: str = "default"


@pytest.fixture
def env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.delenv("TEST_EFP_VALUE", raising=False)
    path = tmp_path / "test.env"
    path.write_text("TEST_EFP_VALUE=from-file\n")
    return path


def test_reads_the_injected_env_file(env_file: Path) -> None:
    injector = Injector(
        lambda binder: binder.bind(EnvFilePaths, to=EnvFilePaths(env_file))
    )

    assert injector.get(_Settings).value == "from-file"


# The type checkers see the settings' synthesized ``__init__``, not the
# injected one that takes ``EnvFilePaths`` positionally.


def test_reads_an_env_file_passed_directly(env_file: Path) -> None:
    assert _Settings(EnvFilePaths(env_file)).value == "from-file"  # ty: ignore[invalid-argument-type]


def test_none_reads_no_env_file(env_file: Path) -> None:
    assert _Settings(EnvFilePaths(None)).value == "default"  # ty: ignore[invalid-argument-type]


def test_keyword_arguments_win_over_the_env_file(env_file: Path) -> None:
    settings = _Settings(EnvFilePaths(env_file), value="explicit")  # ty: ignore[invalid-argument-type]

    assert settings.value == "explicit"


def test_env_file_paths_are_frozen(env_file: Path) -> None:
    paths = EnvFilePaths(env_file)

    with pytest.raises(ValidationError):
        paths.root = None  # ty: ignore[invalid-assignment]
