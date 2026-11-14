import pytest
from django.core.exceptions import ValidationError

from biased.django.models.char_field import FixedLengthDigitsField


def test_digits_of_the_right_length_pass():
    FixedLengthDigitsField(length=4).run_validators("1234")


@pytest.mark.parametrize("value", ["123\n", "12a4", "12345"])
def test_anything_else_fails(value):
    with pytest.raises(ValidationError):
        FixedLengthDigitsField(length=4).run_validators(value)
