import pytest

from biased.utils.aba_routing_number import (
    is_aba_routing_number_valid,
    validate_aba_routing_number,
)


def test_valid_routing_number():
    assert is_aba_routing_number_valid("011000015")


@pytest.mark.parametrize(
    "value",
    [
        "011000016",  # bad checksum
        "01100001",  # too short
        "0110000150",  # too long
        "01100001²",  # isdigit() yet int() cannot parse it
        "٠١١٠٠٠٠١٥",  # Arabic-Indic digits of a valid number
    ],
)
def test_invalid_routing_numbers_are_rejected_without_raising(value):
    assert not is_aba_routing_number_valid(value)


def test_validate_raises_value_error():
    with pytest.raises(ValueError, match="Invalid ABA Routing Number"):
        validate_aba_routing_number("01100001²")
