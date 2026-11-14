import asyncio
from datetime import timedelta
from typing import Any

import pytest
from temporalio.common import RetryPolicy
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner

from biased.temporal.activities.consts import (
    DEFAULT_RETRY_POLICY,
    DEFAULT_START_TO_CLOSE_TIMEOUT,
)
from biased.temporal.activities.dtos import EchoActivityArg
from biased.temporal.activities.echo import echo_activity
from biased.temporal.activities.utils import with_default_execute_params
from biased.temporal.workflows import workflow as workflow_module
from biased.temporal.workflows.dtos import EchoWorkflowArg
from biased.temporal.workflows.echo import EchoWorkflow
from biased.temporal.workflows.utils import get_workflow_definition


class _UndecoratedEchoWorkflow(EchoWorkflow):
    pass


def test_definition_of_a_decorated_workflow():
    assert get_workflow_definition(EchoWorkflow).name == "echo"


def test_undecorated_subclass_has_no_definition():
    with pytest.raises(ValueError):
        get_workflow_definition(_UndecoratedEchoWorkflow)


def test_echo_workflow_passes_sandbox_validation():
    async def prepare() -> None:
        SandboxedWorkflowRunner().prepare_workflow(
            get_workflow_definition(EchoWorkflow)
        )

    asyncio.run(prepare())


def test_decorator_defaults_to_the_default_retry_policy():
    @with_default_execute_params()
    async def activity(arg: EchoActivityArg) -> EchoActivityArg:
        return arg

    assert activity.default_start_to_close_timeout == DEFAULT_START_TO_CLOSE_TIMEOUT
    assert activity.default_retry_policy is DEFAULT_RETRY_POLICY


@pytest.fixture
def captured(monkeypatch) -> dict[str, Any]:
    calls: dict[str, Any] = {}

    async def fake_execute_activity(**kwargs: Any) -> Any:
        calls.update(kwargs)

    async def fake_execute_child_workflow(**kwargs: Any) -> Any:
        calls.update(kwargs)

    monkeypatch.setattr(
        workflow_module.workflow, "execute_activity", fake_execute_activity
    )
    monkeypatch.setattr(
        workflow_module.workflow, "execute_child_workflow", fake_execute_child_workflow
    )
    return calls


def test_execute_activity_applies_the_activity_defaults(captured):
    asyncio.run(
        workflow_module.execute_activity(
            echo_activity, arg=EchoActivityArg(message="m")
        )
    )
    assert captured["start_to_close_timeout"] == timedelta(seconds=3)
    assert captured["retry_policy"] is DEFAULT_RETRY_POLICY


def test_execute_activity_lets_a_call_override_the_defaults(captured):
    policy = RetryPolicy(maximum_attempts=1)
    asyncio.run(
        workflow_module.execute_activity(
            echo_activity,
            arg=EchoActivityArg(message="m"),
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=policy,
        )
    )
    assert captured["start_to_close_timeout"] == timedelta(minutes=1)
    assert captured["retry_policy"] is policy


def test_execute_child_workflow_builds_the_id(captured):
    arg = EchoWorkflowArg(message="m")
    asyncio.run(workflow_module.execute_child_workflow(EchoWorkflow, arg=arg))
    assert captured["id"] == "echo-m"


def test_execute_child_workflow_lets_a_call_set_the_id(captured):
    arg = EchoWorkflowArg(message="m")
    asyncio.run(
        workflow_module.execute_child_workflow(EchoWorkflow, arg=arg, id="custom")
    )
    assert captured["id"] == "custom"
