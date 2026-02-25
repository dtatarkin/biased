from temporalio import workflow

from biased.temporal.activities.dtos import EchoActivityArg, EchoActivityResult
from biased.temporal.activities.echo import echo_activity
from biased.temporal.workflows.base import BaseWorkflow
from biased.temporal.workflows.dtos import EchoWorkflowArg, EchoWorkflowResult
from biased.temporal.workflows.workflow import execute_activity

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    ...


@workflow.defn(name="echo")
class EchoWorkflow(BaseWorkflow[EchoWorkflowArg, EchoWorkflowResult]):
    @classmethod
    def build_id(cls, arg: EchoWorkflowArg) -> str:
        return f"{cls._get_workflow_definition().name}-{arg.message}"

    @workflow.run
    async def run(self, arg: EchoWorkflowArg) -> EchoWorkflowResult:
        result: EchoActivityResult = await execute_activity(
            echo_activity,
            arg=EchoActivityArg(message=arg.message),
        )
        return EchoWorkflowResult(
            message=result.message,
        )
