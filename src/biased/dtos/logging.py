import logging
from enum import StrEnum, auto, unique

from biased.dtos.base import BaseDto
from biased.types import LogLevel


@unique
class LogFormatter(StrEnum):
    json = auto()
    human = auto()


class LoggingParams(BaseDto):
    level: LogLevel = logging.INFO
    formatter: LogFormatter = LogFormatter.json
    # A pydantic field, copied per instance: ruff cannot see BaseDto is a BaseModel.
    levels: dict[str, LogLevel] = {}  # noqa: RUF012
    # ``None`` follows the terminal: colored when stderr is a TTY, plain when
    # piped or captured. Set it explicitly to force either.
    colors: bool | None = None
