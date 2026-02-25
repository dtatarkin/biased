from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import cast

from temporalio.common import RetryPolicy

from biased.dtos.base import BaseDto
from biased.temporal.activities.consts import DEFAULT_START_TO_CLOSE_TIMEOUT
from biased.temporal.activities.types import ActivityFuncWrapper


def with_default_execute_params[ArgT: BaseDto, ResultT: BaseDto](
    start_to_close_timeout: timedelta = DEFAULT_START_TO_CLOSE_TIMEOUT,
    retry_policy: RetryPolicy | None = None,
) -> Callable[[Callable[[ArgT], Awaitable[ResultT]]], ActivityFuncWrapper[ArgT, ResultT]]:
    """Decorator to set default execution parameters on an activity function.

    Sets `default_start_to_close_timeout` and optionally `default_retry_policy`
    attributes on the activity function for use with `workflow.execute_activity()`.

    Args:
        start_to_close_timeout: Default timeout for the activity (default: DEFAULT_START_TO_CLOSE_TIMEOUT).
        retry_policy: Optional default retry policy for the activity.

    Usage:
        @activity.defn(name="my_activity")
        @with_default_execute_params(
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2,
                maximum_interval=timedelta(hours=1),
            ),
        )
        async def my_activity(arg: MyActivityArg) -> MyActivityResult:
            ...

        # Then in workflow:
        from biased.temporal.workflows.workflow import execute_activity

        await execute_activity(my_activity, arg=MyActivityArg(...))
    """

    def decorator(func: Callable[[ArgT], Awaitable[ResultT]]) -> ActivityFuncWrapper[ArgT, ResultT]:
        func = cast(ActivityFuncWrapper[ArgT, ResultT], func)
        func.default_start_to_close_timeout = start_to_close_timeout
        func.default_retry_policy = retry_policy
        return func

    return decorator
