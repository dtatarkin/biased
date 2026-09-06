import sys
from typing import cast

import structlog
from injector import inject

from biased.dtos.logging import LogFormatter, LoggingParams
from biased.logging.consts import HANDLER_NAME
from biased.logging.processors import merge_data_payload
from biased.logging.utils import structlog_json_serializer
from biased.structlog.processors import AsyncTaskInfoAdder


def get_logging_dict_config(params: LoggingParams) -> dict:
    """The one ``logging.config.dictConfig`` mapping: a single stderr handler
    whose ``ProcessorFormatter`` runs every record through the enrichment
    chain and then the renderer ``params.formatter`` selects.

    Existing loggers stay enabled — modules obtain theirs at import time,
    before this configuration is applied.
    """
    # Runs on stdlib records only, while the ``LogRecord`` is still attached:
    # the ``extra=`` fields are copied in, the ``data`` payload is lifted, and
    # the callsite is read from the record itself rather than from the frame
    # that formats it.
    foreign_pre_chain = (
        structlog.stdlib.ExtraAdder(),
        merge_data_payload,
        structlog.processors.CallsiteParameterAdder(
            parameters=(
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.PROCESS,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
                structlog.processors.CallsiteParameter.THREAD,
                structlog.processors.CallsiteParameter.THREAD_NAME,
            )
        ),
    )

    # Shared by both renderers; the processor-meta keys are dropped last, right
    # before rendering, because ``add_logger_name`` needs the record.
    enrichment = (
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        AsyncTaskInfoAdder(),
        structlog.processors.StackInfoRenderer(),
    )

    colors = params.colors if params.colors is not None else sys.stderr.isatty()

    config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            LogFormatter.json.value: {
                "()": structlog.stdlib.ProcessorFormatter,
                "foreign_pre_chain": foreign_pre_chain,
                "processors": (
                    *enrichment,
                    # A traceback string serialises; an ``exc_info`` tuple
                    # does not.
                    structlog.processors.format_exc_info,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(
                        serializer=structlog_json_serializer
                    ),
                ),
            },
            LogFormatter.human.value: {
                "()": structlog.stdlib.ProcessorFormatter,
                "foreign_pre_chain": foreign_pre_chain,
                "processors": (
                    *enrichment,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    # Renders ``exc_info`` itself. The plain formatter, not
                    # the Rich one structlog picks when Rich is importable:
                    # that one prints every frame's locals, which puts
                    # whatever a process holds in memory onto stderr.
                    structlog.dev.ConsoleRenderer(
                        colors=colors,
                        exception_formatter=structlog.dev.plain_traceback,
                    ),
                ),
            },
        },
        "handlers": {
            HANDLER_NAME: {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "formatter": params.formatter,
            },
        },
        "loggers": {
            "root": {
                "level": params.level,
                "handlers": [HANDLER_NAME],
            },
        },
    }

    loggers = cast(dict, config["loggers"])
    for logger_name, level in params.levels.items():
        if logger_name in loggers:
            loggers[logger_name]["level"] = level
        else:
            loggers[logger_name] = dict(level=level)
    return config


class LoggingDictConfig(dict):
    @inject
    def __init__(self, params: LoggingParams):
        super().__init__()
        self.update(get_logging_dict_config(params=params))
