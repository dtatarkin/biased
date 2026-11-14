import asyncio
from typing import Any, cast

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

from biased.temporal import temporal_client_holder as holder_module
from biased.temporal.django.admin.trigger_temporal_workflow_mixin import (
    TriggerTemporalWorkflowMixin,
)
from biased.temporal.dtos import TemporalClientParams
from biased.temporal.temporal_client_holder import TemporalClientHolder
from biased.temporal.workflows.dtos import EchoWorkflowArg
from biased.temporal.workflows.echo import EchoWorkflow


def test_api_key_is_hidden_from_repr():
    params = TemporalClientParams(target_host="h", api_key="sekret")  # type: ignore[arg-type]
    assert "sekret" not in repr(params)
    assert "sekret" not in str(params.model_dump())


@pytest.mark.parametrize(("api_key", "expected"), [("sekret", "sekret"), (None, None)])
def test_holder_passes_the_plain_api_key(monkeypatch, api_key, expected):
    seen: dict[str, Any] = {}

    async def fake_connect(target_host: str, **kwargs: Any) -> object:
        seen.update(kwargs)
        return object()

    monkeypatch.setattr(holder_module.Client, "connect", fake_connect)
    holder = TemporalClientHolder(
        TemporalClientParams(target_host="h", api_key=api_key)
    )  # type: ignore[arg-type]
    asyncio.run(holder.get_or_create_temporal_client())
    assert seen["api_key"] == expected


@pytest.mark.parametrize("state", [None, {}])
def test_mixin_refuses_a_request_without_a_client_holder(state):
    request = HttpRequest()
    if state is not None:
        setattr(request, "state", state)  # noqa: B010 - HttpRequest declares no state
    with pytest.raises(ImproperlyConfigured, match="temporal_client_holder"):
        TriggerTemporalWorkflowMixin._start_temporal_workflow(
            cast(Any, None),
            request,
            EchoWorkflow,
            EchoWorkflowArg(message="m"),
            django_temporal_ui=cast(Any, None),
        )
