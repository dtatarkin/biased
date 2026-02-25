from datetime import timedelta

from temporalio.common import RetryPolicy

DEFAULT_START_TO_CLOSE_TIMEOUT = timedelta(seconds=30)

DEFAULT_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=5),
    backoff_coefficient=2,
    maximum_interval=timedelta(days=1),
)
