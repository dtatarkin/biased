from collections.abc import Awaitable
from datetime import timedelta
from typing import Protocol

from temporalio.common import RetryPolicy

from biased.dtos.base import BaseDto


class ActivityFuncWrapper[ArgT: BaseDto, ResultT: BaseDto](Protocol):
    """Protocol for activity functions decorated with with_default_execute_params."""

    default_start_to_close_timeout: timedelta
    default_retry_policy: RetryPolicy | None

    def __call__(self, arg: ArgT, /) -> Awaitable[ResultT]: ...
