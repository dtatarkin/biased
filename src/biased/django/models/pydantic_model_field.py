from typing import Any

import pydantic
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import JSONField
from django.db.models.fields.json import KeyTransform
from pydantic import BaseModel

from biased.django.forms.pydantic_model_form_field import PydanticModelFormField
from biased.utils.default_json_encoder import DefaultJsonEncoder


# Consider to use [django-pydantic-field](https://github.com/surenkov/django-pydantic-field) instead
class PydanticModelField(JSONField):
    """A JSON column read and written as an instance of `pydantic_model`.

    Every whole-document load validates against the current `pydantic_model`, and
    a stored row that no longer matches raises `ValidationError` — on purpose: a
    schema change ships with a data migration of the rows it invalidates.
    """

    # Django reads this through the MRO into a per-instance dict; it is never mutated.
    default_error_messages = {  # noqa: RUF012
        "invalid": "Value must be valid JSON.",
        "invalid_schema": "Data has invalid schema. %(pydantic_error)s",
    }

    def _value_to_pydantic_model(self, value):
        try:
            value = self.pydantic_model.model_validate(value, from_attributes=True)
        except pydantic.ValidationError as e:
            raise ValidationError(
                self.error_messages["invalid_schema"],
                code="invalid_schema",
                params={
                    "pydantic_error": str(e),
                },
            ) from e

        return value

    def validate(self, value, model_instance):
        if isinstance(value, self.pydantic_model):
            return
        self._value_to_pydantic_model(value)
        super().validate(value, model_instance)

    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> forms.Field | None:
        params: dict[str, Any] = {
            "pydantic_model": self.pydantic_model,
            "encoder": self.encoder,
            "decoder": self.decoder,
            **kwargs,
        }
        return super().formfield(
            form_class=form_class or PydanticModelFormField,
            choices_form_class=choices_form_class,
            **params,
        )

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        self._value_to_pydantic_model(value)
        return value

    def __init__(self, pydantic_model: type[BaseModel], *args, **kwargs):
        self.pydantic_model = pydantic_model
        kwargs.setdefault("encoder", DefaultJsonEncoder)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["pydantic_model"] = self.pydantic_model
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        # A key lookup selects one member of the document, not a whole model.
        if value is None or isinstance(expression, KeyTransform):
            return value
        value = self._value_to_pydantic_model(value)
        return value

    def get_prep_value(self, value):
        if isinstance(value, BaseModel):
            value = value.model_dump(mode="json")
        return super().get_prep_value(value)
