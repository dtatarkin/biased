from biased.logging.processors import merge_data_payload


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
