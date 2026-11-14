from typing import Any

from temporalio import workflow

from biased.dtos.base import BaseDto
from biased.temporal.activities.types import ActivityFuncWrapper
from biased.temporal.workflows.base import BaseWorkflow


async def execute_activity[ArgT: BaseDto, ResultT: BaseDto](
    activity: ActivityFuncWrapper[ArgT, ResultT],
    *,
    arg: ArgT,
    **kwargs: Any,
) -> ResultT:
    """Execute an activity with the defaults `with_default_execute_params` set.

    A `start_to_close_timeout` or `retry_policy` in kwargs overrides the
    activity's default; every other kwarg goes to `workflow.execute_activity`.
    """
    kwargs.setdefault("start_to_close_timeout", activity.default_start_to_close_timeout)
    kwargs.setdefault("retry_policy", activity.default_retry_policy)
    return await workflow.execute_activity(activity=activity, arg=arg, **kwargs)


async def execute_child_workflow[ArgT: BaseDto, ResultT: BaseDto](
    child_workflow: type[BaseWorkflow[ArgT, ResultT]],
    *,
    arg: ArgT,
    id: str | None = None,
    **kwargs: Any,
) -> ResultT:
    """Execute a child workflow, its ID from `build_id` unless `id` is given."""
    workflow_definition = child_workflow._get_workflow_definition()
    if id is None:
        id = child_workflow.build_id(arg=arg)
    return await workflow.execute_child_workflow(
        workflow=workflow_definition.run_fn,
        arg=arg,
        id=id,
        **kwargs,
    )
