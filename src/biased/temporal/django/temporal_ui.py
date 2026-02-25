from django.utils.html import format_html

from biased.temporal.services.temporal_ui import TemporalUi


class DjangoTemporalUi(TemporalUi):
    def build_workflow_html_link(self, workflow_id: str, content: str | None = None) -> str:
        url = self.build_workflow_url(workflow_id=workflow_id)
        if content is None:
            content = workflow_id
        return format_html('<a href="{}" target="_blank">{}</a>', str(url), content)
