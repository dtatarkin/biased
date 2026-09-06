import logging.config

from biased.dtos.logging import LoggingParams
from biased.logging.dict_config import get_logging_dict_config
from biased.logging.settings import LoggingConfig


def configure_logging(params: LoggingParams | None = None) -> None:
    """Apply the one central logging configuration to the running process.

    Call it once, at every entrypoint (a command-line script's callback, a web
    server's settings module, a worker's startup). ``params`` defaults to
    :class:`LoggingConfig`, i.e. the ``LOG_``-prefixed environment; pass an
    explicit ``LoggingParams`` only when the environment must not decide.
    """
    logging.config.dictConfig(get_logging_dict_config(params or LoggingConfig()))
