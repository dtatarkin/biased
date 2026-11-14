from logging import getLogger
from typing import Any

from asgiref.sync import async_to_sync
from temporalio.client import WorkflowHandle

from biased.dtos.base import BaseDto
from biased.temporal.temporal_client_holder import TemporalClientHolder
from biased.temporal.workflows.base import BaseWorkflow

# Client-side only: kept out of `workflows/` so that no workflow module, which
# the sandbox re-imports on every run, pulls in asgiref.

log = getLogger(__name__)


def start_workflow[ArgT: BaseDto, ResultT: BaseDto](
    temporal_client_holder: TemporalClientHolder,
    workflow: type[BaseWorkflow[ArgT, ResultT]],
    arg: ArgT,
    *,
    task_queue: str = "default",
    **kwargs: Any,
) -> WorkflowHandle[Any, ResultT]:
    """Start a workflow from synchronous code; see `BaseWorkflow.start`."""

    @async_to_sync
    async def _start() -> WorkflowHandle[Any, ResultT]:
        workflow_handle = await workflow.start(
            client=await temporal_client_holder.get_or_create_temporal_client(),
            arg=arg,
            task_queue=task_queue,
            **kwargs,
        )

        log.info(
            "started_temporal_workflow",
            extra={
                "data": {
                    "workflow_name": workflow.get_workflow_name(),
                    "workflow_handle_id": workflow_handle.id,
                }
            },
        )
        return workflow_handle

    return _start()
