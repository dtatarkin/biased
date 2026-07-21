import pytest
from biased.django.actor import actor, get_current_actor
from django.contrib.auth.models import AnonymousUser, User


@pytest.fixture
def user():
    return User(username="user")


@pytest.fixture
def user2():
    return User(username="user2")


def test_no_actor_bound_by_default():
    assert get_current_actor() is None


def test_actor_bound_within_block(user):
    with actor(user):
        assert get_current_actor() == user
    assert get_current_actor() is None


def test_nested_innermost_wins(user, user2):
    with actor(user):
        with actor(user2):
            assert get_current_actor() == user2
        assert get_current_actor() == user


def test_previous_binding_restored_on_exception(user):
    with pytest.raises(RuntimeError):
        with actor(user):
            raise RuntimeError
    assert get_current_actor() is None


def test_actor_none_forces_system_attribution(user):
    with actor(user), actor(None):
        assert get_current_actor() is None


def test_anonymous_user_resolves_to_no_actor():
    with actor(AnonymousUser()):
        assert get_current_actor() is None
