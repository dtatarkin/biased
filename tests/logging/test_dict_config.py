import logging

from structlog.stdlib import ProcessorFormatter

from biased.dtos.logging import LogFormatter, LoggingParams
from biased.logging.consts import HANDLER_NAME
from biased.logging.dict_config import LoggingDictConfig, get_logging_dict_config


class TestShape:
    def test_one_stderr_handler_per_formatter(self) -> None:
        config = get_logging_dict_config(LoggingParams())

        assert config["version"] == 1
        assert config["disable_existing_loggers"] is False
        for name in (LogFormatter.json.value, LogFormatter.human.value):
            assert config["formatters"][name]["()"] is ProcessorFormatter
        handler = config["handlers"][HANDLER_NAME]
        assert handler["stream"] == "ext://sys.stderr"
        assert handler["formatter"] == LogFormatter.json
        assert config["loggers"]["root"]["handlers"] == [HANDLER_NAME]

    def test_root_level_follows_params(self) -> None:
        assert get_logging_dict_config(LoggingParams())["loggers"]["root"]["level"] == (
            logging.INFO
        )
        config = get_logging_dict_config(LoggingParams(level="DEBUG"))
        assert config["loggers"]["root"]["level"] == logging.DEBUG

    def test_per_logger_overrides_become_logger_entries(self) -> None:
        config = get_logging_dict_config(LoggingParams(levels={"a.b": "WARNING"}))

        assert config["loggers"]["a.b"] == {"level": logging.WARNING}

    def test_renderer_is_the_last_processor(self) -> None:
        formatters = get_logging_dict_config(LoggingParams())["formatters"]

        json_tail = formatters[LogFormatter.json.value]["processors"][-1]
        human_tail = formatters[LogFormatter.human.value]["processors"][-1]
        assert type(json_tail).__name__ == "JSONRenderer"
        assert type(human_tail).__name__ == "ConsoleRenderer"

    def test_injectable_dict_has_the_same_shape(self) -> None:
        params = LoggingParams(level="ERROR")

        injectable = LoggingDictConfig(params)
        plain = get_logging_dict_config(params)
        # Processor instances are fresh per call, so compare the structure.
        assert injectable.keys() == plain.keys()
        assert injectable["loggers"] == plain["loggers"]
        assert injectable["handlers"] == plain["handlers"]
