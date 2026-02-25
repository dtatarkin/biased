from logging import getLogger

from asgiref.sync import async_to_sync
from temporalio import workflow
from temporalio.client import WorkflowHandle

from biased.dtos.base import BaseDto
from biased.temporal.activities.types import ActivityFuncWrapper
from biased.temporal.temporal_client_holder import TemporalClientHolder
from biased.temporal.workflows.base import BaseWorkflow

log = getLogger(__name__)


async def execute_activity[ArgT: BaseDto, ResultT: BaseDto](
    activity: ActivityFuncWrapper[ArgT, ResultT],
    *,
    arg: ArgT,
    **kwargs,
) -> ResultT:
    return await workflow.execute_activity(
        activity=activity,
        arg=arg,
        start_to_close_timeout=activity.default_start_to_close_timeout,
        retry_policy=activity.default_retry_policy,
        **kwargs,
    )


async def execute_child_workflow[ArgT: BaseDto, ResultT: BaseDto](
    child_workflow: type[BaseWorkflow[ArgT, ResultT]],
    *,
    arg: ArgT,
    **kwargs,
) -> ResultT:
    workflow_definition = child_workflow._get_workflow_definition()
    return await workflow.execute_child_workflow(
        workflow=workflow_definition.run_fn,
        arg=arg,
        id=child_workflow.build_id(arg=arg),
        **kwargs,
    )


def start_workflow[ArgT: BaseDto, ResultT: BaseDto](
    temporal_client_holder: TemporalClientHolder,
    workflow: type[BaseWorkflow[ArgT, ResultT]],
    arg: ArgT,
    *,
    task_queue: str = "default",
    **kwargs,
) -> WorkflowHandle:
    @async_to_sync
    async def _start() -> WorkflowHandle:
        workflow_handle = await workflow.start(
            client=await temporal_client_holder.get_or_create_temporal_client(),
            arg=arg,
            task_queue=task_queue,
            **kwargs,
        )

        log.info(
            "started_temporal_workflow",
            extra=dict(
                data=dict(
                    workflow_name=workflow.get_workflow_name(),
                    workflow_handle_id=workflow_handle.id,
                )
            ),
        )
        return workflow_handle

    return _start()
