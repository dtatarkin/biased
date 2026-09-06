import json
import logging

import pytest

from biased.dtos.logging import LogFormatter, LoggingParams
from biased.logging.configure import configure_logging
from biased.logging.consts import HANDLER_NAME

log = logging.getLogger("tests.biased.logging")


class TestApplied:
    def test_root_gets_the_one_handler_at_the_configured_level(
        self, pristine_root_logger: logging.Logger
    ) -> None:
        configure_logging(LoggingParams(level="WARNING"))

        assert [h.name for h in pristine_root_logger.handlers] == [HANDLER_NAME]
        assert pristine_root_logger.level == logging.WARNING

    def test_defaults_come_from_the_environment(
        self, pristine_root_logger: logging.Logger, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LOG_LEVEL", "ERROR")

        configure_logging()

        assert pristine_root_logger.level == logging.ERROR

    def test_below_the_level_nothing_reaches_stderr(
        self, pristine_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        configure_logging(LoggingParams(level="WARNING"))

        log.info("quiet_event", extra={"data": {"id": 1}})

        assert capsys.readouterr().err == ""

    def test_per_logger_override_opens_one_logger(
        self, pristine_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        configure_logging(LoggingParams(level="WARNING", levels={log.name: "DEBUG"}))

        log.debug("loud_event")
        logging.getLogger("tests.biased.other").debug("quiet_event")

        err = capsys.readouterr().err
        assert "loud_event" in err
        assert "quiet_event" not in err


class TestRendering:
    def test_human_line_carries_payload_and_enrichment(
        self, pristine_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        configure_logging(
            LoggingParams(level="DEBUG", formatter=LogFormatter.human, colors=False)
        )

        log.warning("pane_run", extra={"data": {"pane_id": 7, "label": "build"}})

        (line,) = capsys.readouterr().err.splitlines()
        assert "pane_run" in line
        assert "[warning" in line
        assert f"[{log.name}]" in line
        assert "pane_id=7" in line and "label=build" in line
        assert "func_name=test_human_line_carries_payload_and_enrichment" in line

    def test_json_record_is_one_flat_object(
        self, pristine_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        configure_logging(LoggingParams(level="DEBUG", formatter=LogFormatter.json))

        log.info("panes_killed", extra={"data": {"pane_ids": [1, 2]}})

        (line,) = capsys.readouterr().err.splitlines()
        record = json.loads(line)
        assert record["event"] == "panes_killed"
        assert record["pane_ids"] == [1, 2]
        assert record["level"] == "info"
        assert record["logger"] == log.name
        assert "data" not in record
        assert {"timestamp", "filename", "module", "func_name", "lineno"} <= (
            record.keys()
        )
        assert record["module"] == "test_configure"

    def test_json_exception_is_rendered_as_a_traceback(
        self, pristine_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        configure_logging(LoggingParams(level="DEBUG", formatter=LogFormatter.json))

        try:
            raise ValueError("boom")
        except ValueError as exc:
            log.debug("unlock_error", exc_info=exc, extra={"data": {"code": "X"}})

        record = json.loads(capsys.readouterr().err)
        assert record["code"] == "X"
        assert "ValueError: boom" in record["exception"]

    def test_human_exception_is_rendered_as_a_traceback(
        self, pristine_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        configure_logging(
            LoggingParams(level="DEBUG", formatter=LogFormatter.human, colors=False)
        )

        try:
            raise ValueError("boom")
        except ValueError as exc:
            log.error("unlock_error", exc_info=exc)

        err = capsys.readouterr().err
        assert "unlock_error" in err
        assert "ValueError: boom" in err
        # The plain traceback: no Rich frame boxes, no rendered locals.
        assert "╭" not in err
        assert "locals" not in err

    def test_level_names_are_read_in_any_case(
        self, pristine_root_logger: logging.Logger, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LOG_LEVEL", "debug")

        configure_logging()

        assert pristine_root_logger.level == logging.DEBUG

    def test_payload_values_use_the_json_encoder(
        self, pristine_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from datetime import UTC, datetime
        from decimal import Decimal

        configure_logging(LoggingParams(level="DEBUG", formatter=LogFormatter.json))

        log.info(
            "paid",
            extra={
                "data": {
                    "amount": Decimal("1.50"),
                    "at": datetime(2026, 9, 6, 12, 0, tzinfo=UTC),
                }
            },
        )

        record = json.loads(capsys.readouterr().err)
        assert record["amount"] == "1.50"
        assert record["at"] == "2026-09-06T12:00:00Z"
