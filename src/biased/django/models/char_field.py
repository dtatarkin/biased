from collections.abc import Sequence
from typing import Any

from django.core.validators import BaseValidator, RegexValidator
from django.db import models
from django.db.models import CharField
from django.utils.deconstruct import deconstructible


@deconstructible
class FixedLengthValidator(BaseValidator):
    message = "Ensure this value has %(limit_value)d character (it has %(show_value)d)."
    code = "length"

    def compare(self, a: Any, b: Any) -> bool:
        return a != b

    def clean(self, x: Any) -> int:
        return len(x)


class FixedLengthCharField(CharField):
    def __init__(self, *args: Any, length: int, **kwargs: Any) -> None:
        self.length = length
        kwargs["max_length"] = length
        super().__init__(*args, **kwargs)
        self.validators.insert(0, FixedLengthValidator(length))

    def deconstruct(self) -> tuple[str, str, Sequence[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        kwargs["length"] = self.length
        return name, path, args, kwargs


class FixedLengthDigitsField(FixedLengthCharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.validators.append(
            RegexValidator(regex=r"^[0-9]+$", message="Only digit characters allowed.")
        )


class DefaultUlidField(FixedLengthCharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("length", 26)
        super().__init__(*args, **kwargs)


class SsnLast4Field(FixedLengthCharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("length", 4)
        super().__init__(*args, **kwargs)


class DefaultCharField(CharField):
    MAX_LENGTH = 254

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("max_length", self.MAX_LENGTH)
        super().__init__(*args, **kwargs)


class DefaultShortCharField(DefaultCharField):
    MAX_LENGTH = 36


class NameField(DefaultCharField):
    MAX_LENGTH = 150


class DefaultUrlField(models.URLField):
    MAX_LENGTH = 2000

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("max_length", self.MAX_LENGTH)
        super().__init__(*args, **kwargs)
