import io
import json
import logging
import re
from collections.abc import Callable

import pytest

from biased.dtos.logging_params import LogFormatter, LoggingParams
from biased.logging.configure import configure_logging
from biased.logging.consts import HANDLER_NAME
from biased.logging.settings import LoggingConfig

log = logging.getLogger("tests.biased.logging")

# Stands for a credential a process holds in memory: it is a local of the
# frame that fails and appears nowhere else — not in the exception's text, not
# in the event's payload.
_FRAME_LOCAL = "frame-local-credential"

# Removed before looking for a value, which a colored rendering may split.
_ANSI = re.compile(r"\x1b\[[0-9;]*m")

# What every escape sequence starts with: a rendering without it carries none.
_ESC = "\x1b"


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


def _fail_holding(credential: str) -> None:
    raise RuntimeError("request failed")


class TestFrameLocals:
    @pytest.mark.parametrize("colors", [False, True])
    def test_human_traceback_names_the_frame_and_not_what_it_holds(
        self,
        pristine_root_logger: logging.Logger,
        capsys: pytest.CaptureFixture[str],
        colors: bool,
    ) -> None:
        configure_logging(
            LoggingParams(level="DEBUG", formatter=LogFormatter.human, colors=colors)
        )

        try:
            _fail_holding(_FRAME_LOCAL)
        except RuntimeError:
            log.exception("request_error")

        err = _ANSI.sub("", capsys.readouterr().err)
        assert "_fail_holding" in err
        assert _FRAME_LOCAL not in err

    def test_json_traceback_names_the_frame_and_not_what_it_holds(
        self, pristine_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
    ) -> None:
        configure_logging(LoggingParams(level="DEBUG", formatter=LogFormatter.json))

        try:
            _fail_holding(_FRAME_LOCAL)
        except RuntimeError:
            log.exception("request_error")

        err = capsys.readouterr().err
        assert "_fail_holding" in err
        assert _FRAME_LOCAL not in err


class TestColors:
    @pytest.mark.parametrize("terminal", [True, False])
    def test_unset_colors_follow_the_terminal(
        self,
        pristine_root_logger: logging.Logger,
        stderr_builder: Callable[..., io.StringIO],
        terminal: bool,
    ) -> None:
        stderr = stderr_builder(terminal=terminal)
        configure_logging(LoggingParams(level="DEBUG", formatter=LogFormatter.human))

        log.warning("pane_run", extra={"data": {"pane_id": 7}})

        (line,) = stderr.getvalue().splitlines()
        assert "pane_run" in line
        assert (_ESC in line) is terminal

    @pytest.mark.parametrize("colors", [True, False])
    def test_explicit_colors_win_over_the_terminal(
        self,
        pristine_root_logger: logging.Logger,
        stderr_builder: Callable[..., io.StringIO],
        colors: bool,
    ) -> None:
        # The terminal says the opposite of what was asked for.
        stderr = stderr_builder(terminal=not colors)
        configure_logging(
            LoggingParams(level="DEBUG", formatter=LogFormatter.human, colors=colors)
        )

        log.warning("pane_run", extra={"data": {"pane_id": 7}})

        (line,) = stderr.getvalue().splitlines()
        assert "pane_run" in line
        assert (_ESC in line) is colors

    @pytest.mark.parametrize(("value", "colors"), [("true", True), ("false", False)])
    def test_environment_colors_win_over_the_terminal(
        self,
        pristine_root_logger: logging.Logger,
        stderr_builder: Callable[..., io.StringIO],
        monkeypatch: pytest.MonkeyPatch,
        value: str,
        colors: bool,
    ) -> None:
        monkeypatch.setenv("LOG_FORMATTER", "human")
        monkeypatch.setenv("LOG_COLORS", value)
        stderr = stderr_builder(terminal=not colors)
        configure_logging(LoggingConfig(_env_file=None))

        log.warning("pane_run", extra={"data": {"pane_id": 7}})

        (line,) = stderr.getvalue().splitlines()
        assert "pane_run" in line
        assert (_ESC in line) is colors

    @pytest.mark.parametrize("colors", [None, True, False])
    def test_json_record_carries_no_escape(
        self,
        pristine_root_logger: logging.Logger,
        stderr_builder: Callable[..., io.StringIO],
        colors: bool | None,
    ) -> None:
        # On a terminal, where the human rendering is colored unless told not
        # to be.
        stderr = stderr_builder(terminal=True)
        configure_logging(
            LoggingParams(level="DEBUG", formatter=LogFormatter.json, colors=colors)
        )

        log.warning("pane_run", extra={"data": {"pane_id": 7}})

        (line,) = stderr.getvalue().splitlines()
        assert _ESC not in line
        record = json.loads(line)
        assert record["event"] == "pane_run"
        # Nor inside a value, where the encoder would have written it escaped.
        assert not any(
            _ESC in value for value in record.values() if isinstance(value, str)
        )
