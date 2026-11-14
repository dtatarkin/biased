import warnings

import pytest
from django import forms
from django.core.exceptions import ValidationError
from django.db import connection, models
from pydantic import BaseModel

from biased.django.models.pydantic_model_field import PydanticModelField


class Payload(BaseModel):
    a: int
    b: str


class Document(models.Model):
    data = PydanticModelField(Payload, null=True, blank=True)

    class Meta:
        app_label = "biased_django"


def _form_field(field: PydanticModelField) -> forms.Field:
    form_field = field.formfield()
    assert form_field is not None
    return form_field


@pytest.fixture
def document_table():
    with connection.schema_editor() as editor:
        editor.create_model(Document)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(Document)


@pytest.mark.usefixtures("document_table")
def test_whole_document_loads_as_the_model():
    Document.objects.create(data=Payload(a=1, b="x"))
    assert Document.objects.get().data == Payload(a=1, b="x")


@pytest.mark.usefixtures("document_table")
def test_nullable_field_stores_null():
    Document.objects.create(data=None)
    assert Document.objects.get().data is None


@pytest.mark.usefixtures("document_table")
def test_key_lookup_returns_the_member_not_a_model():
    Document.objects.create(data=Payload(a=1, b="x"))
    assert list(Document.objects.values_list("data__a", "data__b")) == [(1, "x")]


def test_optional_form_field_accepts_empty_input():
    form_field = _form_field(PydanticModelField(Payload, null=True, blank=True))
    assert form_field.clean("") is None


def test_required_form_field_rejects_empty_input():
    form_field = _form_field(PydanticModelField(Payload))
    with pytest.raises(Exception, match="required"):
        form_field.clean("")


def test_form_field_still_validates_the_schema():
    form_field = _form_field(PydanticModelField(Payload, null=True, blank=True))
    assert form_field.clean('{"a": 1, "b": "x"}') == Payload(a=1, b="x")
    with pytest.raises(Exception, match="invalid schema"):
        form_field.clean('{"a": "not a number"}')


@pytest.mark.usefixtures("document_table")
def test_row_no_longer_matching_the_schema_fails_loudly():
    Document.objects.create(data=Payload(a=1, b="x"))
    Document.objects.update(data={"a": "not a number"})
    with pytest.raises(ValidationError, match="invalid schema"):
        Document.objects.get()


def test_form_field_renders_a_model_as_json_without_deprecation():
    form_field = _form_field(PydanticModelField(Payload))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert form_field.prepare_value(Payload(a=1, b="x")) == '{"a": 1, "b": "x"}'
