import sys
from typing import Any, cast

import structlog
from injector import inject

from biased.dtos.logging_params import LogFormatter, LoggingParams
from biased.logging.consts import HANDLER_NAME
from biased.logging.processors import (
    add_async_task_info,
    add_record_timestamp,
    merge_data_payload,
)
from biased.logging.utils import structlog_json_serializer


def get_logging_dict_config(params: LoggingParams) -> dict[str, Any]:
    """The one ``logging.config.dictConfig`` mapping: a single stderr handler
    whose ``ProcessorFormatter`` runs every record through the enrichment
    chain and then the renderer ``params.formatter`` selects.

    Existing loggers stay enabled — modules obtain theirs at import time,
    before this configuration is applied.
    """
    # Runs on stdlib records only, while the ``LogRecord`` is still attached:
    # the ``extra=`` fields are copied in and the ``data`` payload is lifted.
    payload_pre_chain = (
        structlog.stdlib.ExtraAdder(),
        merge_data_payload,
    )
    # Read from the record itself rather than from the frame that formats it.
    callsite_adder = structlog.processors.CallsiteParameterAdder(
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
    )

    # Shared by both renderers; the processor-meta keys are dropped last, right
    # before rendering, because ``add_logger_name`` and ``add_record_timestamp``
    # read the record.
    enrichment = (
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_record_timestamp,
    )
    stack_info = structlog.processors.StackInfoRenderer()

    colors = params.colors if params.colors is not None else sys.stderr.isatty()

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            LogFormatter.json.value: {
                "()": structlog.stdlib.ProcessorFormatter,
                "foreign_pre_chain": (*payload_pre_chain, callsite_adder),
                "processors": (
                    *enrichment,
                    add_async_task_info,
                    stack_info,
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
                # No callsite, process, thread or asyncio-task keys: on every
                # line they bury the event's own context, and the logger name
                # and the constant event name already lead a reader to the
                # call site. The JSON record keeps them for the log store.
                # Never added rather than removed afterwards, so a call
                # site's own key that shares one of their names still shows.
                "foreign_pre_chain": payload_pre_chain,
                "processors": (
                    *enrichment,
                    stack_info,
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

    loggers = cast(dict[str, dict[str, Any]], config["loggers"])
    for logger_name, level in params.levels.items():
        if logger_name in loggers:
            loggers[logger_name]["level"] = level
        else:
            loggers[logger_name] = {"level": level}
    return config


class LoggingDictConfig(dict):
    @inject
    def __init__(self, params: LoggingParams):
        super().__init__()
        self.update(get_logging_dict_config(params=params))
