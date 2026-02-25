from temporalio.types import ClassType
from temporalio.workflow import _Definition


def get_workflow_definition(workflow: ClassType) -> _Definition:
    workflow_definition: _Definition = getattr(workflow, "__temporal_workflow_definition")
    return workflow_definition
