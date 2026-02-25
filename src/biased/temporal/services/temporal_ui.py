from injector import inject
from pydantic import HttpUrl

from biased.temporal.dtos import TemporalClientParams, TemporalParams


class TemporalUi:
    @inject
    def __init__(self, temporal_params: TemporalParams, client_params: TemporalClientParams):
        self._temporal_params = temporal_params
        self._client_params = client_params

    def build_workflow_url(self, workflow_id: str) -> HttpUrl:
        base = self._temporal_params.ui_base_url
        assert base.host is not None  # nosec B101:assert_used
        return HttpUrl.build(
            scheme=base.scheme,
            host=base.host,
            port=base.port,
            path=f"namespaces/{self._client_params.namespace}/workflows/{workflow_id}",
        )
