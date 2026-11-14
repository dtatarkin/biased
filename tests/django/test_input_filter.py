import pytest
from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest

from biased.django.filters.entity_filter import ValueType, _parse_value
from biased.django.filters.input_filter import IntFieldInputFilter


class UserIdFilter(IntFieldInputFilter):
    title = "user"
    parameter_name = "user_id"
    field_name = "id"


@pytest.fixture
def user_id_filter():
    return UserIdFilter(
        request=HttpRequest(),
        params={},
        model=User,
        model_admin=ModelAdmin(User, AdminSite()),
    )


@pytest.mark.parametrize(("token", "number"), [("5", 5), ("-5", -5), ("+5", 5)])
def test_numeric_token_matches_the_id(user_id_filter, token, number):
    assert user_id_filter.value_to_filter(token) == Q(id=number)


@pytest.mark.parametrize(
    "token", ["abc", "--5", "5-", "²", "1.5", "1_000", "٣", " 5", "5\n"]
)
def test_non_integer_token_matches_nothing(user_id_filter, token):
    assert user_id_filter.value_to_filter(token) == Q(id__in=[])


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("42", (ValueType.int, 42)),
        ("1_000", (ValueType.str, "1_000")),
        ("٣", (ValueType.str, "٣")),
        ("01jxzea2cwn5mf175czatygywq", (ValueType.ulid, "01JXZEA2CWN5MF175CZATYGYWQ")),
        ('"quoted"', (ValueType.str, "quoted")),
    ],
)
def test_entity_token_is_parsed_by_kind(token, expected):
    assert _parse_value(token) == expected
