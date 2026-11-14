from urllib.parse import quote

from injector import inject
from pydantic import HttpUrl

from biased.temporal.dtos import TemporalClientParams, TemporalParams


class TemporalUi:
    @inject
    def __init__(
        self, temporal_params: TemporalParams, client_params: TemporalClientParams
    ):
        self._temporal_params = temporal_params
        self._client_params = client_params

    def build_workflow_url(self, workflow_id: str) -> HttpUrl:
        base = self._temporal_params.ui_base_url
        # Narrows for the type checker: a validated HttpUrl always has a host.
        assert base.host is not None  # nosec B101:assert_used  # noqa: S101
        # Each segment is encoded whole: a workflow ID is free text, and a `/`,
        # `?`, `#` or `%` left raw would split the path or end it early.
        namespace = quote(self._client_params.namespace, safe="")
        workflow = quote(workflow_id, safe="")
        prefix = (base.path or "").strip("/")
        path = f"namespaces/{namespace}/workflows/{workflow}"
        return HttpUrl.build(
            scheme=base.scheme,
            host=base.host,
            port=base.port,
            path=f"{prefix}/{path}" if prefix else path,
        )
