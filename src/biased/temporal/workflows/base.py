from abc import ABC, abstractmethod

from temporalio.client import Client, WorkflowHandle
from temporalio.workflow import _Definition

from biased.dtos.base import BaseDto
from biased.temporal.workflows.utils import get_workflow_definition


class BaseWorkflow[ArgT: BaseDto, ResultT: BaseDto](ABC):
    @classmethod
    @abstractmethod
    def build_id(cls, arg: ArgT) -> str:
        """Generate a unique workflow ID based on the provided arg DTO."""
        ...

    @classmethod
    def _get_workflow_definition(cls) -> _Definition:
        """Get the Temporal workflow definition for this workflow class."""
        return get_workflow_definition(workflow=cls)

    @classmethod
    def get_workflow_name(cls) -> str:
        workflow_definition = cls._get_workflow_definition()
        assert workflow_definition.name is not None  # nosec B101:assert_used
        return workflow_definition.name

    @classmethod
    async def start(
        cls,
        client: Client,
        arg: ArgT,
        *,
        task_queue: str = "default",
        id: str | None = None,
        **kwargs,
    ) -> WorkflowHandle:
        """Start the workflow.

        Args:
            client: Temporal client
            arg: Workflow argument DTO
            task_queue: Task queue name
            id: Workflow ID. If None, will be generated using build_id
                by extracting kwargs from arg.model_dump().
            **kwargs: Additional kwargs passed to client.start_workflow.

        Returns:
            WorkflowHandle for the started workflow.
        """
        workflow_definition = cls._get_workflow_definition()
        if id is None:
            id = cls.build_id(arg=arg)
        handle = await client.start_workflow(
            workflow_definition.run_fn,
            arg=arg,
            id=id,
            task_queue=task_queue,
            **kwargs,
        )
        return handle
