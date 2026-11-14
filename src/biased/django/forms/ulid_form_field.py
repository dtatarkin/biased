from django import forms
from django.core.validators import RegexValidator

from biased.consts import ULID_PATTERN


class UlidFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["min_length"] = 26
        kwargs["max_length"] = 26
        kwargs["validators"] = [RegexValidator(ULID_PATTERN)]
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        # Crockford Base32 is case-insensitive; the canonical form, which
        # `UlidStr` also produces, is upper case.
        value = super().to_python(value)
        # `empty_value` may be set to `None`.
        return value.upper() if isinstance(value, str) else value
