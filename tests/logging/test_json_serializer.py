import json
from datetime import UTC, time

import structlog
from pydantic import BaseModel, field_serializer

from biased.logging.utils import structlog_json_serializer


class _Opaque:
    def __repr__(self) -> str:
        return "<opaque>"


class _WithHook:
    def __structlog__(self) -> str:
        return "hooked"


class _BrokenModel(BaseModel):
    x: int = 1

    @field_serializer("x")
    def _fail(self, value: int) -> int:
        raise ValueError("boom")

    def __repr__(self) -> str:
        return "<broken model>"


class _BrokenHook:
    def __structlog__(self) -> str:
        raise RuntimeError("boom")

    def __repr__(self) -> str:
        return "<broken>"


def _render(value: object) -> dict:
    rendered = structlog.processors.JSONRenderer(serializer=structlog_json_serializer)(
        None, "info", {"event": "x", "v": value}
    )
    return json.loads(rendered)


class TestStructlogJsonSerializer:
    def test_known_types_use_the_default_encoder(self) -> None:
        assert _render(time(1, 2, 3))["v"] == "01:02:03"

    def test_unknown_type_falls_back_to_repr(self) -> None:
        assert _render(_Opaque())["v"] == "<opaque>"

    def test_structlog_hook_wins_over_repr(self) -> None:
        assert _render(_WithHook())["v"] == "hooked"

    def test_broken_structlog_hook_falls_back_to_repr(self) -> None:
        assert _render(_BrokenHook())["v"] == "<broken>"

    def test_type_error_from_the_encoder_falls_back(self) -> None:
        aware = time(1, tzinfo=UTC)

        assert _render(aware)["v"] == repr(aware)

    def test_non_type_error_from_the_encoder_falls_back(self) -> None:
        assert _render(_BrokenModel())["v"] == "<broken model>"

    def test_works_without_a_default_argument(self) -> None:
        assert structlog_json_serializer({"b": 1, "a": 2}) == '{"a":2,"b":1}'


class TestEventJsonCannotDumpAsItStands:
    def test_mixed_key_types_are_sorted_as_strings(self) -> None:
        assert _render({1: "a", "b": 2, None: 3, 2.5: 4, False: 5})["v"] == {
            "1": "a",
            "2.5": 4,
            "b": 2,
            "false": 5,
            "null": 3,
        }

    def test_non_scalar_key_is_rendered_by_repr(self) -> None:
        assert _render({(1, 2): 3})["v"] == {"(1, 2)": 3}

    def test_reference_cycle_is_cut(self) -> None:
        cycle: list[object] = [1]
        cycle.append(cycle)

        assert _render(cycle)["v"] == [1, "<circular reference>"]

    def test_values_keep_the_default_encoder_after_a_retry(self) -> None:
        assert _render({1: time(1, 2, 3), "b": _Opaque()})["v"] == {
            "1": "01:02:03",
            "b": "<opaque>",
        }

    def test_nesting_past_the_recursion_limit_falls_back_to_repr(self) -> None:
        nested: list[object] = []
        for _ in range(100_000):
            nested = [nested]

        rendered = _render(nested)

        assert rendered["event"] == "x"
        assert rendered["v"].startswith("[[[")
