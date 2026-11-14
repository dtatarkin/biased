import pytest
from django.core.exceptions import ValidationError

from biased.django.forms.ulid_form_field import UlidFormField

_ULID = "01JXZEA2CWN5MF175CZATYGYWQ"


@pytest.mark.parametrize("value", [_ULID, _ULID.lower(), f" {_ULID.lower()} "])
def test_ulid_in_any_case_cleans_to_upper_case(value):
    assert UlidFormField().clean(value) == _ULID


def test_non_ulid_is_rejected():
    with pytest.raises(ValidationError):
        UlidFormField().clean("U" * 26)


def test_optional_empty_input_stays_empty():
    assert UlidFormField(required=False).clean("") == ""


def test_none_as_empty_value_is_kept():
    assert UlidFormField(required=False, empty_value=None).clean("") is None
