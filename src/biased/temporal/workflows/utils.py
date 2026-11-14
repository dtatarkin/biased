from temporalio.types import ClassType
from temporalio.workflow import _Definition


def get_workflow_definition(workflow: ClassType) -> _Definition:
    # `must_from_class` refuses a definition inherited from a decorated parent,
    # which a plain attribute lookup would return for an undecorated subclass.
    return _Definition.must_from_class(workflow)
