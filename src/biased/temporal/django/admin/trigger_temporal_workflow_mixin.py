from typing import Any

from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils.html import format_html
from temporalio.client import WorkflowHandle

from biased.dtos.base import BaseDto
from biased.temporal.django.temporal_ui import DjangoTemporalUi
from biased.temporal.starting import start_workflow
from biased.temporal.temporal_client_holder import TemporalClientHolder
from biased.temporal.workflows.base import BaseWorkflow


class TriggerTemporalWorkflowMixin(ModelAdmin):
    def _start_temporal_workflow[ArgT: BaseDto, ResultT: BaseDto](
        self,
        request: HttpRequest,
        workflow: type[BaseWorkflow[ArgT, ResultT]],
        arg: ArgT,
        django_temporal_ui: DjangoTemporalUi,
        *,
        task_queue: str = "default",
        context: Any = None,
    ) -> WorkflowHandle[Any, ResultT]:
        """Start a Temporal workflow from Django admin.

        Args:
            request: Django HTTP request (must have state["temporal_client_holder"])
            workflow: Workflow class (must inherit from BaseWorkflow)
            arg: Workflow argument DTO
            django_temporal_ui: Builds the Temporal UI link in the success message
            task_queue: Task queue name
            context: Optional context to display in the success message

        Returns:
            WorkflowHandle for the started workflow.

        Raises:
            ImproperlyConfigured: the request carries no Temporal client holder.
        """
        state: dict[str, Any] | None = getattr(request, "state", None)
        temporal_client_holder: TemporalClientHolder | None = (
            state.get("temporal_client_holder") if state is not None else None
        )
        if temporal_client_holder is None:
            raise ImproperlyConfigured(
                'request.state["temporal_client_holder"] is not set: a middleware '
                "must attach a TemporalClientHolder to every admin request"
            )

        handle = start_workflow(
            temporal_client_holder=temporal_client_holder,
            workflow=workflow,
            arg=arg,
            task_queue=task_queue,
        )

        if context is None:
            context_str = ""
        else:
            context_str = f", {context}"
        self.message_user(
            request,
            message=format_html(
                "Successfully started Temporal workflow {workflow_html_link}{context_str}",
                workflow_html_link=django_temporal_ui.build_workflow_html_link(
                    workflow_id=handle.id, content=workflow.get_workflow_name()
                ),
                context_str=context_str,
            ),
            level=messages.SUCCESS,
        )

        return handle
