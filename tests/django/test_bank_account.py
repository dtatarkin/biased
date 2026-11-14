import pytest
from django.core.exceptions import ValidationError

from biased.django.models.bank_account import AbaRoutingNumberField


def test_valid_routing_number_passes():
    AbaRoutingNumberField().run_validators("011000015")


@pytest.mark.parametrize("value", ["011000016", "01100001²", "٠١١٠٠٠٠١٥"])
def test_invalid_routing_number_is_a_validation_error(value):
    with pytest.raises(ValidationError):
        AbaRoutingNumberField().run_validators(value)
