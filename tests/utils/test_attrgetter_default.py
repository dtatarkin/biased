import pytest

from biased.utils.attrgetter_default import attrgetter_default


class _Leaf:
    value = 1


class _Node:
    leaf = _Leaf()
    nothing = None

    @property
    def broken(self):
        return self.leaf.absent  # ty: ignore[unresolved-attribute] - the bug under test


class _Dynamic:
    def __getattr__(self, name):
        raise AttributeError(name)


def test_present_attribute():
    assert attrgetter_default("leaf.value")(_Node()) == 1


def test_missing_attribute_returns_default():
    assert attrgetter_default("absent", default=7)(_Node()) == 7


def test_missing_along_the_path_returns_default():
    assert attrgetter_default("nothing.value", default=7)(_Node()) == 7


def test_several_attributes_return_a_tuple():
    assert attrgetter_default("leaf.value", "nothing")(_Node()) == (1, None)


def test_any_missing_of_several_returns_default():
    assert attrgetter_default("leaf.value", "absent", default=7)(_Node()) == 7


def test_bare_attribute_error_from_getattr_counts_as_missing():
    assert attrgetter_default("anything", default=7)(_Dynamic()) == 7


def test_attribute_error_inside_a_property_propagates():
    with pytest.raises(AttributeError, match="absent"):
        attrgetter_default("broken")(_Node())
