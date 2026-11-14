from biased.utils.filter_not_none_values import filter_not_none_values


def test_drops_only_none():
    assert filter_not_none_values({"a": None, "b": 0, "c": "", "d": False}) == {
        "b": 0,
        "c": "",
        "d": False,
    }
