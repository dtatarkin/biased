import asyncio

from structlog.typing import EventDict

from biased.logging.processors import add_async_task_info, merge_data_payload


class TestMergeDataPayload:
    def test_payload_keys_are_lifted_and_data_removed(self) -> None:
        event = merge_data_payload(None, "info", {"event": "x", "data": {"id": 7}})

        assert event == {"event": "x", "id": 7}

    def test_existing_keys_win_over_the_payload(self) -> None:
        event = merge_data_payload(
            None, "info", {"event": "x", "data": {"event": "masked"}}
        )

        assert event == {"event": "x"}

    def test_non_mapping_data_is_left_alone(self) -> None:
        event = merge_data_payload(None, "info", {"event": "x", "data": "raw"})

        assert event == {"event": "x", "data": "raw"}

    def test_absent_data_is_a_no_op(self) -> None:
        assert merge_data_payload(None, "info", {"event": "x"}) == {"event": "x"}


class TestAddAsyncTaskInfo:
    def test_without_a_running_loop_nothing_is_added(self) -> None:
        assert add_async_task_info(None, "info", {"event": "x"}) == {"event": "x"}

    def test_inside_a_task_its_name_and_id_are_added(self) -> None:
        async def log() -> tuple[EventDict, asyncio.Task]:
            task = asyncio.current_task()
            assert task is not None
            return add_async_task_info(None, "info", {"event": "x"}), task

        event, task = asyncio.run(log())

        assert event == {
            "event": "x",
            "async_task_name": task.get_name(),
            "async_task": id(task),
        }

    def test_in_a_loop_callback_outside_a_task_nothing_is_added(self) -> None:
        events: list[EventDict] = []
        loop = asyncio.new_event_loop()
        try:
            loop.call_soon(
                lambda: events.append(add_async_task_info(None, "info", {"event": "x"}))
            )
            loop.call_soon(loop.stop)
            loop.run_forever()
        finally:
            loop.close()

        assert events == [{"event": "x"}]
