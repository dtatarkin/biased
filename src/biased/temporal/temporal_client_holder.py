from injector import inject
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from biased.temporal.dtos import TemporalClientParams


class TemporalClientHolder:
    @inject
    def __init__(self, params: TemporalClientParams) -> None:
        self._params = params
        self._client: Client | None = None

    async def get_or_create_temporal_client(self) -> Client:
        if self._client is None:
            params = self._params
            self._client = await Client.connect(
                params.target_host,
                namespace=params.namespace,
                api_key=params.api_key,
                identity=params.identity,
                lazy=params.lazy,
                data_converter=pydantic_data_converter,
            )
        return self._client
