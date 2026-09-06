from collections.abc import Mapping

from structlog.typing import EventDict, WrappedLogger

from biased.logging.consts import DATA_KEY


def merge_data_payload(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Lift the call-site payload (``extra=dict(data=dict(...))``) to the top
    level of the event, so its fields render as first-class keys.

    Keys already present in the event — the event name, or anything an
    earlier processor set — win over the payload; a ``data`` value that is not
    a mapping is left where it is.
    """
    data = event_dict.get(DATA_KEY)
    if not isinstance(data, Mapping):
        return event_dict
    del event_dict[DATA_KEY]
    for key, value in data.items():
        event_dict.setdefault(key, value)
    return event_dict
