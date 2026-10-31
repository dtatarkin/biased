# An optional integration no extra declares, so the import does not resolve here.
from multiselectfield import MultiSelectField  # ty: ignore[unresolved-import]


class BiasedMultiSelectField(MultiSelectField):
    def get_prep_value(self, value):
        result = super().get_prep_value(value=value)
        return None if result == "" else result
