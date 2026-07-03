import operator
from abc import ABC, abstractmethod
from collections.abc import Iterator
from functools import reduce

from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.views.main import ChangeList
from django.db.models import Q, QuerySet
from django.http import HttpRequest


class InputFilter(SimpleListFilter):
    template = "admin/input_filter.html"

    def lookups(
        self, request: HttpRequest, model_admin: ModelAdmin
    ) -> list[tuple[str, str]]:
        return []

    def has_output(self) -> bool:
        # An input filter has no discrete lookup choices, so the default
        # ``len(lookup_choices) > 0`` would hide it. The text box must always be
        # offered, so force the filter visible.
        return True

    def get_facet_counts(self, pk_attname: str, filtered_qs: QuerySet) -> dict:
        return {}

    def choices(self, changelist: ChangeList) -> Iterator:
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice["query_parts"] = (  # type: ignore[typeddict-unknown-key]
            (k, v)
            for k, values in changelist.get_filters_params().items()
            for v in values
            if k != self.parameter_name
        )
        yield all_choice


class CommaSeparatedInputFilter(InputFilter, ABC):
    @abstractmethod
    def value_to_filter(self, value: str) -> Q:
        pass

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        filter_value = self.value()
        if filter_value is not None:
            filters: list[Q] = []
            for i in filter_value.split(","):
                value = i.strip()
                if not value:
                    continue
                filters.append(self.value_to_filter(value=value))
            if filters:
                return queryset.filter(reduce(operator.or_, filters))
        return None


class IntFieldInputFilter(CommaSeparatedInputFilter):
    """Filter an integer model field by a comma-separated list of ids.

    Subclasses set ``field_name`` (the model field to match) alongside the
    standard ``title`` and ``parameter_name``. A row matches if ``field_name``
    equals any numeric token; a non-numeric token cannot be an id, so it matches
    nothing. ``field_name`` may be a related lookup (e.g. ``account__id``).
    """

    field_name: str

    def value_to_filter(self, value: str) -> Q:
        if value.lstrip("-").isdigit():
            return Q(**{self.field_name: int(value)})
        # A non-numeric token cannot be an id; an empty ``__in`` is Django's
        # backend-agnostic "match nothing" (short-circuited as an empty result).
        return Q(**{f"{self.field_name}__in": []})


class StrArrayInputFilter(InputFilter):
    query_name: str

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        filter_value = self.value()
        if filter_value is not None:
            items: list[str] = []
            for i in filter_value.split(","):
                value = i.strip()
                if not value:
                    continue
                items.append(value)
            if items:
                return queryset.filter(**{f"{self.query_name}__contains": items})
        return None
