import logging
from enum import StrEnum, auto, unique

from pydantic import ConfigDict

from biased.dtos.base import BaseDto
from biased.pydantic.frozen_map import FrozenMap
from biased.types import LogLevel


@unique
class LogFormatter(StrEnum):
    json = auto()
    human = auto()


class LoggingParams(BaseDto):
    # A misspelt knob would otherwise leave logging silently at its default.
    # The settings classes built on this one re-open it to ``ignore``.
    model_config = ConfigDict(extra="forbid")

    level: LogLevel = logging.INFO
    formatter: LogFormatter = LogFormatter.json
    levels: FrozenMap[str, LogLevel] = FrozenMap()
    # ``None`` follows the terminal: colored when stderr is a TTY, plain when
    # piped or captured. Set it explicitly to force either.
    colors: bool | None = None
