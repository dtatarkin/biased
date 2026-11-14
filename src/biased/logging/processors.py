from asyncio import current_task
from collections.abc import Mapping
from datetime import UTC, datetime

from structlog.typing import EventDict, WrappedLogger

from biased.logging.consts import DATA_KEY


def merge_data_payload(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Lift the call-site payload (``extra=dict(data=dict(...))``) to the top
    level of the event, so its fields render as first-class keys.

    Keys already present in the event — the event name, or anything an
    earlier processor set — win over the payload, and a processor running
    after this one may overwrite a lifted key; a ``data`` value that is not a
    mapping is left where it is.
    """
    data = event_dict.get(DATA_KEY)
    if not isinstance(data, Mapping):
        return event_dict
    del event_dict[DATA_KEY]
    for key, value in data.items():
        event_dict.setdefault(key, value)
    return event_dict


def add_async_task_info(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add the name and ``id`` of the asyncio task that logged the event.

    Nothing is added outside a task — with no running loop, or in a loop
    callback that no task runs.
    """
    try:
        task = current_task()
    except RuntimeError:
        return event_dict
    if task is None:
        return event_dict
    event_dict["async_task_name"] = task.get_name()
    event_dict["async_task"] = id(task)
    return event_dict


def add_record_timestamp(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Stamp the event with the time its ``LogRecord`` was created, as UTC
    ISO 8601 with a ``Z`` suffix.

    Unlike ``structlog.processors.TimeStamper``, which stamps the moment of
    formatting: a queued or buffered handler formats a record late, and the
    event would carry the wrong time.
    """
    created = datetime.fromtimestamp(event_dict["_record"].created, UTC)
    event_dict["timestamp"] = created.isoformat().replace("+00:00", "Z")
    return event_dict
