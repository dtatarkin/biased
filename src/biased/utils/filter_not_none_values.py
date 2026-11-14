def filter_not_none_values(mapping: dict) -> dict:
    return {key: value for key, value in mapping.items() if value is not None}
