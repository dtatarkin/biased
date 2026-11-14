import pytest
from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest

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


@pytest.mark.parametrize("token", ["abc", "--5", "5-", "²", "1.5"])
def test_non_integer_token_matches_nothing(user_id_filter, token):
    assert user_id_filter.value_to_filter(token) == Q(id__in=[])
