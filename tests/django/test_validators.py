from biased.django.validators.pydantic import PydanticDjangoValidator


def test_equal_validators_hash_alike():
    first = PydanticDjangoValidator("builtins.int")
    second = PydanticDjangoValidator("builtins.int")
    assert first == second
    assert len({first, second, PydanticDjangoValidator("builtins.str")}) == 2
